import os
import yaml
import tarfile
import tempfile
import lmctl.files as files
import lmctl.journal as journal
import lmctl.project.journal as project_journal
import lmctl.project.package.meta as pkg_metas
import lmctl.project.processes.push as push_exec
import lmctl.project.processes.testing as test_exec
import lmctl.project.handlers.manager as handler_manager

########################
# Exceptions
########################

class PackageError(Exception):
    pass

class InvalidPackageError(PackageError):
    pass

class PushError(PackageError):
    pass

class TestError(PackageError):
    pass


########################
# Options
########################

class Options:

    def __init__(self):
        self.journal_consumer = None


class PushOptions(Options):

    def __init__(self):
        super().__init__()


class TestOptions(Options):

    def __init__(self):
        super().__init__()
        self.selected_tests = ['*']


class PkgContentBase():

    def __init__(self, tree, meta):
        if tree is None:
            raise ValueError('tree must be provided')
        self.tree = tree
        if meta is None:
            raise ValueError('meta must be provided')
        self.meta = meta
        self.handler = handler_manager.content_handler_for(self.meta)(self.tree.root_path, self.meta)
        self.subcontents = self.__init_subcontents()

    def __init_subcontents(self):
        subcontents = []
        subcontents_config = self.meta.subpkgs
        for subcontent_config in subcontents_config:
            child_content_path = self.tree.gen_child_content_path(subcontent_config.directory)
            child_content = SubPkgContent(child_content_path, subcontent_config, self)
            subcontents.append(child_content)
        return subcontents
    
class SubPkgContent(PkgContentBase):

    def __init__(self, root_path, meta, parent_pkg):
        if root_path is None:
            raise ValueError('root_path must be provided for a Subproject')
        if meta is None:
            raise ValueError('meta must be provided for SubPkgContent')
        if parent_pkg is None:
            raise ValueError('parent_pkg must be provided for Subproject')
        self.parent_pkg = parent_pkg
        tree = PkgContentTree(root_path)
        super().__init__(tree, meta)

class Pkg:

    def __init__(self, path):
        self.path = path

    def extract(self, target_directory):
        with tarfile.open(self.path, mode='r:gz') as pkg_tar:
            pkg_tar.extractall(target_directory)

    def open(self, target_directory):
        self.extract(target_directory)
        pkg_tree = ExpandedPkgTree(target_directory)
        meta = self.__read_meta_file(pkg_tree)
        return PkgContent(pkg_tree.content_path, meta)

    def __read_meta_file(self, pkg_tree):
        meta_file_path = pkg_tree.pkg_meta_file_path
        deprecated_pkg_meta_file_path = pkg_tree.deprecated_pkg_meta_file_path
        if os.path.exists(deprecated_pkg_meta_file_path) and not os.path.exists(meta_file_path):
            with open(deprecated_pkg_meta_file_path, 'rt') as f:
                old_meta_dict = yaml.safe_load(f.read())
            version = self.__attempt_to_determine_version()
            pkg_metas.PkgMetaRewriter(deprecated_pkg_meta_file_path, meta_file_path, old_meta_dict, version).rewrite()
            content_tgz = pkg_tree.deprecated_content_tgz_path
            if os.path.exists(content_tgz):
                with tarfile.open(content_tgz, mode='r:gz') as content_tar:
                    content_tar.extractall(pkg_tree.content_path)
        if not os.path.exists(meta_file_path):
            raise InvalidPkgMetaError('Could not find meta file at path: {0}'.format(meta_file_path))
        with open(meta_file_path, 'rt') as f:
            config_dict = yaml.safe_load(f.read())
        if not config_dict:
            config_dict = {}
        return pkg_metas.PkgMetaParser.from_dict(config_dict)

    def __attempt_to_determine_version(self):
        try:
            potential_descriptor = os.path.join(self.path, 'Descriptor', 'assembly.yml')
            if os.path.exists(potential_descriptor):
                descriptor = descriptor_utils.DescriptorParser().read_from_file(potential_descriptor)
                return descriptor.get_version()
        except Exception as e:
            return None

    def __init_journal(self, journal_consumer=None):
        return project_journal.ProjectJournal(journal_consumer)

    def push(self, env_sessions, options):
        journal = self.__init_journal(options.journal_consumer)
        journal.section('Processing Package')
        journal.event('Processing {0}'.format(self.path))
        push_workspace = self.__create_push_workspace()
        files.clean_directory(push_workspace)
        pkg_content = self.open(push_workspace)
        pkg_content.push(env_sessions, options)
        return pkg_content

    def __create_push_workspace(self):
        tempdir = tempfile.mkdtemp()
        return tempdir

class PkgContent(PkgContentBase):

    def __init__(self, root_path, meta):
        if root_path is None:
            raise ValueError('root_path must be provided for PkgContent')
        tree = PkgContentTree(root_path)
        super().__init__(tree, meta)
        self.__rename_old_directories(tree)

    def __rename_old_directories(self, pkg_tree):
        vnfcs_path = pkg_tree.vnfcs_path
        contains_path = pkg_tree.child_content_path
        if os.path.exists(vnfcs_path) and not os.path.exists(contains_path):
            os.rename(vnfcs_path, contains_path)

    def __init_journal(self, journal_consumer=None):
        return project_journal.ProjectJournal(journal_consumer)

    def push(self, env_sessions, options):
        journal = self.__init_journal(options.journal_consumer)
        return self.__do_push(env_sessions, options, journal)

    def __do_push(self, env_sessions, options, journal):
        try:
            push_exec.PushProcess(self, options, journal, env_sessions).execute()
        except push_exec.PushProcessError as e:
            raise PushError(str(e)) from e
        journal.section('Post process environments')
        self.__post_process_updated_environments(env_sessions, options, journal)

    def test(self, env_sessions, options):
        journal = self.__init_journal(options.journal_consumer)
        return self.__do_test(env_sessions, options, journal)

    def __do_test(self, env_sessions, options, journal):
        try:
            return test_exec.TestProcess(self, options, journal, env_sessions).execute()
        except test_exec.TestProcessError as e:
            raise TestError(str(e)) from e

    def __post_process_updated_environments(self, env_sessions, options, journal):
        if env_sessions.is_arm_updated():
            arm_session = env_sessions.arm
            lm_session = env_sessions.lm
            onboarding_driver = lm_session.onboard_rm_driver
            arm_onboarding_addr = '{0}/api/v1.0/resource-manager'.format(arm_session.env.onboarding_address)
            journal.event('Refreshing LM ({0}) view of ansible-rm known as {1} with url {2}'.format(lm_session.env.address, arm_session.env.name, arm_onboarding_addr))
            onboarding_driver.update_rm(arm_session.env.name, arm_onboarding_addr)
        else:
            journal.event('No environments to update')


class ExpandedPkgTree(files.Tree):

    CONTENT_DIR = 'content'
    PKG_META_FILE_YML = 'lmpkg.yml'

    @property
    def deprecated_pkg_meta_file_path(self):
        return self.resolve_relative_path('lmproject.yml')

    @property
    def deprecated_content_tgz_path(self):
        return self.resolve_relative_path('content.tgz')

    @property
    def pkg_meta_file_name(self):
        return ExpandedPkgTree.PKG_META_FILE_YML

    @property
    def pkg_meta_file_path(self):
        return self.resolve_relative_path(self.pkg_meta_file_name)

    @property
    def content_path(self):
        return self.resolve_relative_path(ExpandedPkgTree.CONTENT_DIR)

    @property
    def content_dir_name(self):
        return ExpandedPkgTree.CONTENT_DIR

class PkgContentTree(files.Tree):
    CONTAINS_DIR = 'Contains'
    VNFCS_DIR = 'VNFCs'

    def __init__(self, root_path):
        super().__init__(root_path)

    def __relative_child_content_path(self):
        return self.relative_path(PkgContentTree.CONTAINS_DIR)

    @property
    def vnfcs_path(self):
        return self.resolve_relative_path(PkgContentTree.VNFCS_DIR)

    @property
    def child_content_path(self):
        return self.resolve_relative_path(self.__relative_child_content_path())

    def gen_child_content_path(self, subcontent_name):
        return self.resolve_relative_path(self.__relative_child_content_path(), subcontent_name)

    def gen_child_content_tree(self, subcontent_name):
        return PkgContentTree(self.gen_child_content_path(subcontent_name))
