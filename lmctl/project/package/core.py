import os
import yaml
import tarfile
import tempfile
import shutil
import lmctl.utils.descriptors as descriptor_utils
import lmctl.files as files
import lmctl.journal as journal
import lmctl.project.journal as project_journal
import lmctl.project.package.meta as pkg_metas
import lmctl.project.processes.push as push_exec
import lmctl.project.processes.testing as test_exec
import lmctl.project.handlers.manager as handler_manager
import lmctl.drivers.lm.base as lm_drivers

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

class PkgInspectionReport:

    def __init__(self, pkg_name, pkg_version, includes):
        self.name = pkg_name
        self.version = pkg_version
        if includes is None:
            includes = []
        self.includes = includes

    def to_dict(self):
        tpl = {}
        tpl['name'] = self.name
        tpl['version'] = self.version
        tpl['includes'] = []
        for include in self.includes:
            tpl['includes'].append(include.to_dict())
        return tpl
    
class PkgIncludeEntry:

    def __init__(self, meta_entry):
        self.meta_entry = meta_entry
    
    @property
    def name(self):
        return self.meta_entry.full_name

    @property
    def descriptor_name(self):
        return self.meta_entry.descriptor_name

    @property
    def resource_manager(self):
        return self.meta_entry.resource_manager

    def to_dict(self):
        tpl = {}
        tpl['name'] = self.name
        tpl['descriptor'] = self.descriptor_name
        resource_manager = self.resource_manager
        if resource_manager != None:
            tpl['resource-manager'] = resource_manager
        return tpl

class Pkg:

    def __init__(self, path):
        self.path = path

    def inspect(self):
        tempdir = tempfile.mkdtemp()
        try:
            pkg_content = self.open(tempdir)
            return pkg_content.inspect()
        finally:
            if os.path.exists(tempdir):
                shutil.rmtree(tempdir)

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
            raise InvalidPackageError('Could not find meta file at path: {0}'.format(meta_file_path))
        with open(meta_file_path, 'rt') as f:
            config_dict = yaml.safe_load(f.read())
        if not config_dict:
            config_dict = {}
        try:
            return pkg_metas.PkgMetaParser.from_dict(config_dict)
        except pkg_metas.PkgMetaError as e:
            raise InvalidPackageError(str(e)) from e

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

    def inspect(self):
        includes = self.__inspect_meta(self.meta)
        return PkgInspectionReport(self.meta.full_name, self.meta.version, includes)

    def __inspect_meta(self, meta_entry):
        includes = []
        includes.append(PkgIncludeEntry(meta_entry))
        for subpkg in meta_entry.subpkgs:
            includes.extend(self.__inspect_meta(subpkg))
        return includes

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
        updating_an_env = False
        if env_sessions.is_arm_updated():
            updating_an_env = True
            lm_session = env_sessions.lm
            arm_session = env_sessions.arm
            self.__reonboard_rm(lm_session, arm_session.env.name, journal)
        if env_sessions.is_brent_updated():
            updating_an_env = True
            lm_session = env_sessions.lm
            brent_name = lm_session.env.brent_name
            self.__reonboard_rm(lm_session, brent_name, journal)
            
        if not updating_an_env:
            journal.event('No environments to update')

    def __reonboard_rm(self, lm_session, rm_name, journal):
        onboarding_driver = lm_session.onboard_rm_driver
        try:
            rm_data = onboarding_driver.get_rm_by_name(rm_name)
        except lm_drivers.NotFoundException as e:
            msg = 'Could not find RM named \'{0}\' in LM environment'.format(rm_name)
            journal.error_event(msg)
            raise PushError(msg) from e
        journal.event('Refreshing LM ({0}) view of RM known as {1} with url {2}'.format(lm_session.env.address, rm_name, rm_data['url']))
        onboarding_driver.update_rm(rm_data)

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
