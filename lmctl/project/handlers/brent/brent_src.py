import os
import yaml
import zipfile
import lmctl.files as files
import lmctl.project.handlers.interface as handlers_api
import lmctl.project.validation as project_validation
from .brent_content import BrentResourcePackageContentTree, BrentPkgContentTree

class BrentSourceTree(files.Tree):

    DEFINITIONS_DIR_NAME = 'Definitions'
    INFRASTRUCTURE_DIR_NAME = 'infrastructure'
    INFRASTRUCTURE_MANIFEST_FILE_NAME = 'infrastructure.mf'
    LM_DIR_NAME = 'lm'
    DESCRIPTOR_FILE_NAME_YML = 'resource.yml'
    DESCRIPTOR_FILE_NAME_YAML = 'resource.yaml'

    LIFECYCLE_DIR_NAME = 'Lifecycle'
    LIFECYCLE_MANIFEST_FILE_NAME = 'lifecycle.mf'
    ANSIBLE_LIFECYCLE_DIR_NAME = 'ansible'
    ANSIBLE_LIFECYCLE_CONFIG_DIR_NAME = 'config'
    ANSIBLE_LIFECYCLE_SCRIPTS_DIR_NAME = 'scripts'
    ANSIBLE_LIFECYCLE_CONFIG_INVENTORY_FILE_NAME = 'inventory'
    ANSIBLE_LIFECYCLE_CONFIG_HOSTVARS_DIR_NAME = 'host_vars'
    
    @property
    def definitions_path(self):
        return self.resolve_relative_path(BrentSourceTree.DEFINITIONS_DIR_NAME)

    @property
    def infrastructure_definitions_path(self):
        return self.resolve_relative_path(BrentSourceTree.DEFINITIONS_DIR_NAME, BrentSourceTree.INFRASTRUCTURE_DIR_NAME)

    @property
    def infrastructure_manifest_file_path(self):
        return self.resolve_relative_path(BrentSourceTree.DEFINITIONS_DIR_NAME, BrentSourceTree.INFRASTRUCTURE_DIR_NAME, BrentSourceTree.INFRASTRUCTURE_MANIFEST_FILE_NAME)

    @property
    def lm_definitions_path(self):
        return self.resolve_relative_path(BrentSourceTree.DEFINITIONS_DIR_NAME, BrentSourceTree.LM_DIR_NAME)

    @property
    def descriptor_file_path(self):
        yaml_path = self.resolve_relative_path(BrentSourceTree.DEFINITIONS_DIR_NAME, BrentSourceTree.LM_DIR_NAME, BrentSourceTree.DESCRIPTOR_FILE_NAME_YAML)
        yml_path = self.resolve_relative_path(BrentSourceTree.DEFINITIONS_DIR_NAME, BrentSourceTree.LM_DIR_NAME, BrentSourceTree.DESCRIPTOR_FILE_NAME_YML)
        if os.path.exists(yml_path):
            if os.path.exists(yaml_path):
                raise handlers_api.InvalidSourceError('Project has both a {0} file and a {1} file when there should only be one'.format(
                    BrentSourceTree.DESCRIPTOR_FILE_NAME_YAML, BrentSourceTree.DESCRIPTOR_FILE_NAME_YML))
            return yml_path
        else:
            return yaml_path

    @property
    def lifecycle_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME)

    @property
    def lifecycle_manifest_file_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.LIFECYCLE_MANIFEST_FILE_NAME)

    @property
    def ansible_lifecycle_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_DIR_NAME)

    @property
    def ansible_lifecycle_scripts_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_SCRIPTS_DIR_NAME)
   
    def gen_ansible_lifecycle_script_file_path(self, lifecycle_name):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_SCRIPTS_DIR_NAME, '{0}.yaml'.format(lifecycle_name))

    @property
    def ansible_lifecycle_config_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_CONFIG_DIR_NAME)

    @property
    def ansible_lifecycle_inventory_file_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_CONFIG_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_CONFIG_INVENTORY_FILE_NAME)

    @property
    def ansible_lifecycle_hostvars_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_CONFIG_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_CONFIG_HOSTVARS_DIR_NAME)

    def gen_ansible_lifecycle_hostvars_file_path(self, host_name):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_CONFIG_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_CONFIG_HOSTVARS_DIR_NAME, '{0}.yml'.format(host_name))

class BrentSourceCreatorDelegate(handlers_api.ResourceSourceCreatorDelegate):

    def __init__(self):
        super().__init__()

    def create_source(self, journal, source_request, file_ops_executor):
        source_tree = BrentSourceTree()
        file_ops = []
        
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.definitions_path, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.infrastructure_definitions_path, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.lm_definitions_path, handlers_api.EXISTING_IGNORE))

        descriptor_content ='description: descriptor for {0}'.format(source_request.source_config.name)
        file_ops.append(handlers_api.CreateFileOp(source_tree.descriptor_file_path, descriptor_content, handlers_api.EXISTING_IGNORE))

        inf_manifest_content = 'templates: []\n  #- file: example.yaml\n  #  infrastructure_type: Openstack'
        file_ops.append(handlers_api.CreateFileOp(source_tree.infrastructure_manifest_file_path, inf_manifest_content, handlers_api.EXISTING_IGNORE))
        
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.lifecycle_path, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.ansible_lifecycle_path, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.ansible_lifecycle_config_path, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.ansible_lifecycle_hostvars_path, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.ansible_lifecycle_scripts_path, handlers_api.EXISTING_IGNORE))

        install_content = '---\n- name: Install\n  hosts: all\n  gather_facts: False'
        file_ops.append(handlers_api.CreateFileOp(source_tree.gen_ansible_lifecycle_script_file_path('Install'), install_content, handlers_api.EXISTING_IGNORE))
        
        inventory_content = '[example]\nexample-host'
        file_ops.append(handlers_api.CreateFileOp(source_tree.ansible_lifecycle_inventory_file_path, inventory_content, handlers_api.EXISTING_IGNORE))
        
        host_var_content = '---\nansible_host: {{ dl_properties.host }}\nansible_ssh_user: {{ dl_properties.ssh_user }}\nansible_ssh_pass: {{ dl_properties.ssh_pass }}'
        file_ops.append(handlers_api.CreateFileOp(source_tree.gen_ansible_lifecycle_hostvars_file_path('example-host'), host_var_content, handlers_api.EXISTING_IGNORE))

        lifecycle_manifest_content = 'types: \n  - lifecycle_type: ansible\n    infrastructure_type: \'*\''
        file_ops.append(handlers_api.CreateFileOp(source_tree.lifecycle_manifest_file_path, lifecycle_manifest_content, handlers_api.EXISTING_IGNORE))

        file_ops_executor(file_ops)

class BrentSourceHandlerDelegate(handlers_api.ResourceSourceHandlerDelegate):
    
    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)
        self.tree = BrentSourceTree(self.root_path)

    def validate_sources(self, journal, source_validator):
        errors = []
        warnings = []
        self.__validate_definitions(journal, errors, warnings)
        self.__validate_lifecycle(journal, errors, warnings)
        return project_validation.ValidationResult(errors, warnings)

    def __find_or_error(self, journal, errors, warnings, path, artifact_type):
        if not os.path.exists(path):
            msg = 'No {0} found at: {1}'.format(artifact_type, path)
            journal.error_event(msg)
            errors.append(project_validation.ValidationViolation(msg))
            return False
        else:
            journal.event('{0} found at: {1}'.format(artifact_type, path))
            return True

    def __validate_definitions(self, journal, errors, warnings):
        definitions_path = self.tree.definitions_path
        if self.__find_or_error(journal, errors, warnings, definitions_path, 'Definitions directory'):
            self.__validate_definitions_infrastructure(journal, errors, warnings)
            self.__validate_definitions_lm(journal, errors, warnings)

    def __validate_definitions_infrastructure(self, journal, errors, warnings):
        inf_path = self.tree.infrastructure_definitions_path
        if self.__find_or_error(journal, errors, warnings, inf_path, 'Infrastructure definitions directory'):
            self.__validate_infrastructure_manifest(journal, errors, warnings)
    
    def __validate_infrastructure_manifest(self, journal, errors, warnings):
        inf_manifest_path = self.tree.infrastructure_manifest_file_path
        if self.__find_or_error(journal, errors, warnings, inf_manifest_path, 'Infrastructure manifest'):
            with open(inf_manifest_path, 'rt') as manifest_file:
                try:
                    manifest_dict = yaml.safe_load(manifest_file.read())
                except yaml.YAMLError as e:
                    msg = 'Infrastructure manifest [{0}]: does not contain valid YAML: {1}'.format(inf_manifest_path, str(e))
                    journal.error_event(msg)
                    errors.append(project_validation.ValidationViolation(msg))
                    return
            if 'templates' not in manifest_dict:
                msg = 'Infrastructure manifest [{0}]: missing \'templates\' field'.format(inf_manifest_path)
                journal.error_event(msg)
                errors.append(project_validation.ValidationViolation(msg))

    def __validate_definitions_lm(self, journal, errors, warnings):
        lm_def_path = self.tree.lm_definitions_path
        if self.__find_or_error(journal, errors, warnings, lm_def_path, 'LM definitions directory'):
            descriptor_file_path = self.tree.descriptor_file_path
            self.__find_or_error(journal, errors, warnings, descriptor_file_path, 'Resource descriptor')

    def __validate_lifecycle(self, journal, errors, warnings):
        lifecycle_path = self.tree.lifecycle_path
        if self.__find_or_error(journal, errors, warnings, lifecycle_path, 'Lifecycle directory'):
            self.__validate_lifecycle_manifest(journal, errors, warnings)

    def __validate_lifecycle_manifest(self, journal, errors, warnings):
        lifecycle_manifest_path = self.tree.lifecycle_manifest_file_path
        if self.__find_or_error(journal, errors, warnings, lifecycle_manifest_path, 'Lifecycle manifest'):
            with open(lifecycle_manifest_path, 'rt') as manifest_file:
                try:
                    manifest_dict = yaml.safe_load(manifest_file.read())
                except yaml.YAMLError as e:
                    msg = 'Lifecycle manifest [{0}]: does not contain valid YAML: {1}'.format(lifecycle_manifest_path, str(e))
                    journal.error_event(msg)
                    errors.append(project_validation.ValidationViolation(msg))
                    return
            if 'types' not in manifest_dict:
                msg = 'Lifecycle manifest [{0}]: missing \'types\' field'.format(lifecycle_manifest_path)
                journal.error_event(msg)
                errors.append(project_validation.ValidationViolation(msg))

    def get_main_descriptor(self):
        main_descriptor_path = self.tree.descriptor_file_path
        return main_descriptor_path

    def stage_sources(self, journal, source_stager):
        staging_tree = BrentResourcePackageContentTree()
        journal.event('Staging Resource descriptor for {0} at {1}'.format(self.source_config.full_name, self.get_main_descriptor()))
        source_stager.stage_descriptor(self.get_main_descriptor(), staging_tree.descriptor_file_path)
        included_items = [
            {'path': self.tree.infrastructure_definitions_path, 'alias': staging_tree.infrastructure_definitions_path},
            {'path': self.tree.lifecycle_path, 'alias': staging_tree.lifecycle_path}
        ]
        self.__stage_directories(journal, source_stager, included_items)

    def __stage_directories(self, journal, source_stager, items):
        for item in items:
            if os.path.exists(item['path']):
                journal.event('Staging directory {0}'.format(item['path']))
                source_stager.stage_tree(item['path'], item['alias'])

    def build_staged_source_delegate(self, staging_path):
        return BrentStagedSourceHandlerDelegate(staging_path, self.source_config)

class BrentStagedSourceHandlerDelegate(handlers_api.ResourceStagedSourceHandlerDelegate):

    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)
        self.tree = BrentResourcePackageContentTree(self.root_path)

    def compile_sources(self, journal, source_compiler):
        pkg_tree = BrentPkgContentTree()
        self.__build_res_pkg(journal, source_compiler, pkg_tree)
        self.__add_root_descriptor(journal, source_compiler, pkg_tree)

    def __add_root_descriptor(self, journal, source_compiler, pkg_tree):
        relative_root_descriptor_path = pkg_tree.root_descriptor_file_path
        source_compiler.compile_file(self.tree.descriptor_file_path, relative_root_descriptor_path)

    def __build_res_pkg(self, journal, source_compiler, pkg_tree):
        res_pkg_content_tree = BrentResourcePackageContentTree()
        relative_res_pkg_path = pkg_tree.gen_resource_package_file_path(self.source_config.full_name)
        full_res_pkg_path = source_compiler.make_file_path(relative_res_pkg_path)
        journal.event('Creating Resource package for {0}: {1}'.format(self.source_config.name, relative_res_pkg_path))
        with zipfile.ZipFile(full_res_pkg_path, "w") as res_pkg:
            included_items = [
                {'path': self.tree.definitions_path, 'alias': res_pkg_content_tree.definitions_path, 'required': True},
                {'path': self.tree.lifecycle_path, 'alias': res_pkg_content_tree.lifecycle_path, 'required': True}
            ]
            for included_item in included_items:
                self.__add_directory_if_exists(journal, res_pkg, included_item)

    def __add_directory_if_exists(self, journal, res_pkg, included_item):
        path = included_item['path']
        if os.path.exists(path):
            journal.event('Adding directory to Resource package: {0}'.format(os.path.basename(path)))
            res_pkg.write(path, arcname=included_item['alias'])
            rootlen = len(path) + 1
            for root, dirs, files in os.walk(path):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    res_pkg.write(full_path, arcname=os.path.join(included_item['alias'], full_path[rootlen:]))
        else:
            if included_item['required']:
                msg = 'Required directory for Resource package not found: {0}'.format(path)
                journal.error_event(msg)
                raise SourceHandlerError(msg)
            else:
                journal.event('Skipping directory for Resource package, not found: {0}'.format(path))