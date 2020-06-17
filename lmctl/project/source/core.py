import os
import lmctl.files as files
import yaml
import lmctl.utils.descriptors as descriptor_utils
import lmctl.project.source.config as project_configs
import lmctl.project.journal as project_journal
import lmctl.project.processes.validation as validation_exec
import lmctl.project.processes.staging as stage_exec
import lmctl.project.processes.compile as compile_exec
import lmctl.project.processes.pull as pull_exec
import lmctl.project.processes.package as package_exec
import lmctl.project.processes.listelement as list_exec
import lmctl.project.handlers.interface as handlers_api
import lmctl.project.handlers.manager as handler_manager
import lmctl.project.package.core as pkgs

########################
# Exceptions
########################

class ProjectError(Exception):
    pass

class InvalidProjectError(ProjectError):
    pass

class ValidateError(ProjectError):
    pass

class BuildError(ProjectError):
    pass

class BuildValidationError(BuildError):

    def __init__(self, validation_result):
        super().__init__('Build failed with validation errors')
        self.validation_result = validation_result
        
class PullError(ProjectError):
    pass

class ListError(ProjectError):
    pass

########################
# Options
########################

class Options:

    def __init__(self):
        self.journal_consumer = None

class ValidateOptions(Options):

    def __init__(self):
        super().__init__()
        self.allow_autocorrect = False


class BuildOptions(ValidateOptions):

    def __init__(self):
        super().__init__()


class PullOptions(Options):

    def __init__(self):
        super().__init__()

########################
# Results
########################

class BuildResult:

    def __init__(self, pkg, validation_result):
        self.pkg = pkg
        self.validation_result = validation_result

########################
# Projects
########################

class ProjectBase():

    def __init__(self, tree, config):
        if tree is None:
            raise ValueError('tree must be provided')
        self.tree = tree
        if config is None:
            raise ValueError('config must be provided')
        self.config = config
        self.source_handler = handler_manager.source_handler_for(self.config)(self.tree.root_path, self.config)
        self.subprojects = self.__init_subprojects()

    def __init_subprojects(self):
        subprojects = []
        subprojects_config = self.config.subprojects
        for subproject_config in subprojects_config:
            child_project_path = self.tree.gen_child_project_path(subproject_config.directory)
            child_project = Subproject(child_project_path, subproject_config, self)
            subprojects.append(child_project)
        return subprojects

class Subproject(ProjectBase):

    def __init__(self, root_path, config, parent_project):
        if root_path is None:
            raise ValueError('root_path must be provided for a Subproject')
        if config is None:
            raise ValueError('config must be provided for a Subproject')
        if parent_project is None:
            raise ValueError('parent_project must be provided for a Subproject')
        self.parent_project = parent_project
        tree = SubprojectTree(root_path)
        super().__init__(tree, config)

class Project(ProjectBase):

    def __init__(self, root_path):
        if root_path is None:
            raise ValueError('root_path must be provided for a Project')
        tree = ProjectTree(root_path)
        config = self.__read_project_file(tree)
        super().__init__(tree, config)

    def __read_project_file(self, tree):
        project_file_path = tree.project_file_path
        if not os.path.exists(project_file_path):
            raise InvalidProjectError('Could not find project file at path: {0}'.format(project_file_path))
        with open(project_file_path, 'rt') as f:
            config_dict = yaml.safe_load(f.read())
        if not config_dict:
            config_dict = {}
        if 'schema' not in config_dict or config_dict['schema'] == project_configs.SCHEMA_1_0:
            version = self.__attempt_to_determine_version()
            config_dict = project_configs.ProjectConfigRewriter(project_file_path, config_dict, version).rewrite()
        try:
            return project_configs.ProjectConfigParser.from_dict(config_dict)
        except project_configs.ProjectConfigError as e:
            raise InvalidProjectError(str(e)) from e


    def __attempt_to_determine_version(self):
        try:
            potential_descriptor = os.path.join(self.root_path, 'Descriptor', 'assembly.yml')
            if os.path.exists(potential_descriptor):
                descriptor = descriptor_utils.DescriptorParser().read_from_file(potential_descriptor)
                return descriptor.get_version()
        except Exception as e:
            return None

    def __init_journal(self, journal_consumer=None):
        return project_journal.ProjectJournal(journal_consumer)

    def validate(self, options):
        journal = self.__init_journal(options.journal_consumer)
        return self.__do_validate(options, journal)

    def __do_validate(self, options, journal):
        try:
            return validation_exec.ValidationProcess(self, options, journal).execute()
        except validation_exec.ValidationProcessError as e:
            raise ValidateError(str(e)) from e

    def build(self, options):
        journal = self.__init_journal(options.journal_consumer)
        return self.__do_build(options, journal)

    def __do_build(self, options, journal):
        validate_result = self.__do_validate(options, journal)
        if validate_result.has_errors():
            raise BuildValidationError(validate_result)
        try:
            staging_tree = stage_exec.StageProcess(self, options, journal).execute()
            content_tree = compile_exec.CompileProcess(self, options, staging_tree, journal).execute()
            final_pkg = package_exec.PkgProcess(self, options, content_tree, journal).execute()
        except (stage_exec.StageProcessError, compile_exec.CompileProcessError, package_exec.PkgProcessError) as e:
            raise BuildError(str(e)) from e
        return BuildResult(final_pkg, validate_result)
    
    def pull(self, env_sessions, options):
        journal = self.__init_journal(options.journal_consumer)
        return self.__do_pull(env_sessions, options, journal)

    def __do_pull(self, env_sessions, options, journal):
        try:
            pull_exec.PullProcess(self, options, journal, env_sessions).execute()
        except pull_exec.PullProcessError as e:
            raise PullError(str(e)) from e

    def list_elements(self, element_type):
        journal = self.__init_journal()
        try:
            return list_exec.ListElementProcess(self, journal, element_type).execute()
        except list_exec.ListElementProcessError as e:
            raise ListError(str(e)) from e

########################
# Trees
########################

class ProjectBaseTree(files.Tree):

    CONTAINS_DIR = 'Contains'
    VNFCS_DIR = 'VNFCs'
    TOSCA_METADATA_DIR = 'TOSCA-Metadata'
    TOSCA_META_FILE = 'TOSCA.meta'

    def __relative_child_projects_path(self):
        return self.relative_path(ProjectBaseTree.CONTAINS_DIR)

    def __vnfcs_or_contains(self):
        vnfcs_path = self.vnfcs_path
        contains_path = self.contains_path
        if os.path.exists(vnfcs_path):
            if os.path.exists(contains_path):
                raise InvalidProjectError('Project has both a {0} directory and a {1} directory when there should only be one'.format(ProjectBaseTree.VNFCS_DIR, ProjectBaseTree.CONTAINS_DIR))
            return vnfcs_path
        else:
            return contains_path

    @property
    def tosca_metadata_path(self):
        return self.resolve_relative_path(ProjectBaseTree.TOSCA_METADATA_DIR)

    @property
    def tosca_meta_file_path(self):
        return self.resolve_relative_path(ProjectBaseTree.TOSCA_META_FILE)

    @property
    def vnfcs_path(self):
        return self.resolve_relative_path(ProjectBaseTree.VNFCS_DIR)

    @property
    def contains_path(self):
        return self.resolve_relative_path(ProjectBaseTree.CONTAINS_DIR)

    @property
    def child_projects_path(self):
        child_projects_path = self.__vnfcs_or_contains()
        return child_projects_path

    def gen_child_project_path(self, child_project_dir_name):
        child_projects_path = self.__vnfcs_or_contains()
        return os.path.join(child_projects_path, child_project_dir_name)

    def gen_child_project_tree(self, child_project_dir_name):
        return SubprojectTree(self.gen_child_project_path(child_project_dir_name))

class ProjectTree(ProjectBaseTree):

    PROJECT_FILE_YML = 'lmproject.yml'
    PROJECT_FILE_YAML = 'lmproject.yaml'

    def __init__(self, root_path=None):
        super().__init__(root_path)

    @property
    def project_file_name(self):
        full_path = self.project_file_path
        return os.path.basename(full_path)

    @property
    def project_file_path(self):
        yml_path = self.resolve_relative_path(ProjectTree.PROJECT_FILE_YML)
        yaml_path = self.resolve_relative_path(ProjectTree.PROJECT_FILE_YAML)
        if os.path.exists(yaml_path):
            if os.path.exists(yml_path):
                raise InvalidProjectError('Project has both a {0} file and a {1} file when there should only be one'.format(ProjectTree.PROJECT_FILE_YML, ProjectTree.PROJECT_FILE_YAML))
            return yaml_path
        else:
            return yml_path

class SubprojectTree(ProjectBaseTree):

    def __init__(self, root_path):
        super().__init__(root_path)
