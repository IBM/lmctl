import os
import yaml
import zipfile
import lmctl.files as files
import lmctl.project.handlers.interface as handlers_api
import lmctl.project.validation as project_validation
import lmctl.utils.descriptors as descriptor_utils
from .brent_content import BrentResourcePackageContentTree, BrentPkgContentTree

class OpenstackTemplatesTree(files.Tree):

    def gen_tosca_template(self, file_name):
        return self.resolve_relative_path('{0}.yaml'.format(file_name))

OPENSTACK_EXAMPLE_TOSCA = '''\
heat_template_version: 2013-05-23

description: >
  Basic example to deploy a single VM

parameters:
  key_name:
    type: string
    default: helloworld
  image:
    type: string
    default: xenial-server-cloudimg-amd64-disk1
resources:
  hello_world_server:
    type: OS::Nova::Server
    properties:
      flavor: ds2G
      user_data_format: SOFTWARE_CONFIG
      image:
        get_param: image
      key_name:
        get_param: key_name
      networks:
      - port: { get_resource: hello_world_server_port }
  hello_world_server_port:
    type: OS::Neutron::Port
    properties:
      network: private
outputs:
  hello_world_private_ip:
    value:
      get_attr:
      - hello_world_server
      - networks
      - private
      - 0
    description: The private IP address of the hello_world_server
'''

class AnsibleLifecycleTree(files.Tree):

    CONFIG_DIR_NAME = 'config'
    SCRIPTS_DIR_NAME = 'scripts'
    CONFIG_INVENTORY_FILE_NAME = 'inventory'
    CONFIG_HOSTVARS_DIR_NAME = 'host_vars'

    @property
    def scripts_path(self):
        return self.resolve_relative_path(AnsibleLifecycleTree.SCRIPTS_DIR_NAME)
   
    def gen_script_file_path(self, lifecycle_name):
        return self.resolve_relative_path(AnsibleLifecycleTree.SCRIPTS_DIR_NAME, '{0}.yaml'.format(lifecycle_name))

    @property
    def config_path(self):
        return self.resolve_relative_path(AnsibleLifecycleTree.CONFIG_DIR_NAME)

    @property
    def inventory_file_path(self):
        return self.resolve_relative_path(AnsibleLifecycleTree.CONFIG_DIR_NAME, AnsibleLifecycleTree.CONFIG_INVENTORY_FILE_NAME)

    @property
    def hostvars_path(self):
        return self.resolve_relative_path(AnsibleLifecycleTree.CONFIG_DIR_NAME, AnsibleLifecycleTree.CONFIG_HOSTVARS_DIR_NAME)

    def gen_hostvars_file_path(self, host_name):
        return self.resolve_relative_path(AnsibleLifecycleTree.CONFIG_DIR_NAME, AnsibleLifecycleTree.CONFIG_HOSTVARS_DIR_NAME, '{0}.yml'.format(host_name))

class Sol003LifecycleTree(files.Tree):
    SCRIPTS_DIR_NAME = 'scripts'
    CREATE_VNF_REQUEST_FILE_NAME = 'CreateVnfRequest.js'
    HEAL_VNF_REQUEST_FILE_NAME = 'HealVnfRequest.js'
    INSTANTIATE_VNF_REQUEST_FILE_NAME = 'InstantiateVnfRequest.js'
    OPERATE_VNF_REQUEST_START_FILE_NAME = 'OperateVnfRequest-Start.js'
    OPERATE_VNF_REQUEST_STOP_FILE_NAME = 'OperateVnfRequest-Stop.js'
    SCALE_VNF_REQUEST_FILE_NAME = 'ScaleVnfRequest.js'
    TERMINATE_VNF_REQUEST_FILE_NAME = 'TerminateVnfRequest.js'
    VNF_INSTANCE_FILE_NAME = 'VnfInstance.js'

    @property
    def scripts_path(self):
        return self.resolve_relative_path(Sol003LifecycleTree.SCRIPTS_DIR_NAME)

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
    SOL003_LIFECYCLE_DIR_NAME = 'sol003'
    
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
    def sol003_lifecycle_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.SOL003_LIFECYCLE_DIR_NAME)

INFRASTRUCTURE_PARAM_NAME = 'inf'
LIFECYCLE_PARAM_NAME = 'lifecycle'
LIFECYCLE_TYPE_ANSIBLE = 'ansible'
LIFECYCLE_TYPE_SOL003 = 'sol003'
INFRASTRUCTURE_TYPE_OPENSTACK = 'openstack'
SOL003_SCRIPT_NAMES = []
SOL003_SCRIPT_NAMES.append(Sol003LifecycleTree.CREATE_VNF_REQUEST_FILE_NAME)
SOL003_SCRIPT_NAMES.append(Sol003LifecycleTree.HEAL_VNF_REQUEST_FILE_NAME)
SOL003_SCRIPT_NAMES.append(Sol003LifecycleTree.INSTANTIATE_VNF_REQUEST_FILE_NAME)
SOL003_SCRIPT_NAMES.append(Sol003LifecycleTree.OPERATE_VNF_REQUEST_START_FILE_NAME)
SOL003_SCRIPT_NAMES.append(Sol003LifecycleTree.OPERATE_VNF_REQUEST_STOP_FILE_NAME)
SOL003_SCRIPT_NAMES.append(Sol003LifecycleTree.SCALE_VNF_REQUEST_FILE_NAME)
SOL003_SCRIPT_NAMES.append(Sol003LifecycleTree.TERMINATE_VNF_REQUEST_FILE_NAME)
SOL003_SCRIPT_NAMES.append(Sol003LifecycleTree.VNF_INSTANCE_FILE_NAME)

class BrentSourceCreatorDelegate(handlers_api.ResourceSourceCreatorDelegate):

    def __init__(self):
        super().__init__()

    def get_params(self, source_request):
        params = []
        params.append(handlers_api.SourceParam(LIFECYCLE_PARAM_NAME, required=False, default_value=LIFECYCLE_TYPE_ANSIBLE, allowed_values=[LIFECYCLE_TYPE_ANSIBLE, LIFECYCLE_TYPE_SOL003]))
        params.append(handlers_api.SourceParam(INFRASTRUCTURE_PARAM_NAME, required=False, default_value=INFRASTRUCTURE_TYPE_OPENSTACK, allowed_values=[INFRASTRUCTURE_TYPE_OPENSTACK]))
        return params

    def create_source(self, journal, source_request, file_ops_executor):
        source_tree = BrentSourceTree()
        file_ops = []
        descriptor = descriptor_utils.Descriptor({}, is_2_dot_1=True)
        descriptor.description = 'descriptor for {0}'.format(source_request.source_config.name)

        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.definitions_path, handlers_api.EXISTING_IGNORE))

        inf_type = source_request.param_values.get_value(INFRASTRUCTURE_PARAM_NAME)
        self.__create_infrastructure(journal, source_request, file_ops, source_tree, inf_type, descriptor)
        
        lifecycle_type = source_request.param_values.get_value(LIFECYCLE_PARAM_NAME)
        self.__create_lifecycle(journal, source_request, file_ops, source_tree, lifecycle_type, descriptor)
        
        self.__create_descriptor(journal, source_request, file_ops, source_tree, descriptor)
        
        file_ops_executor(file_ops)

    def __create_descriptor(self, journal, source_request, file_ops, source_tree, descriptor):
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.lm_definitions_path, handlers_api.EXISTING_IGNORE))
        descriptor_content = descriptor_utils.DescriptorParser().write_to_str(descriptor)
        file_ops.append(handlers_api.CreateFileOp(source_tree.descriptor_file_path, descriptor_content, handlers_api.EXISTING_IGNORE))

    def __create_infrastructure(self, journal, source_request, file_ops, source_tree, inf_type, descriptor):
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.infrastructure_definitions_path, handlers_api.EXISTING_IGNORE))
        if inf_type == INFRASTRUCTURE_TYPE_OPENSTACK:
            descriptor.insert_lifecycle('Create')
            descriptor.insert_lifecycle('Delete')
            templates_tree = OpenstackTemplatesTree(source_tree.infrastructure_definitions_path)
            file_ops.append(handlers_api.CreateFileOp(templates_tree.gen_tosca_template('example'), OPENSTACK_EXAMPLE_TOSCA, handlers_api.EXISTING_IGNORE))
            descriptor.insert_infrastructure_template('Openstack', 'example.yaml', template_type='HEAT')

    def __create_lifecycle(self, journal, source_request, file_ops, source_tree, lifecycle_type, descriptor):
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.lifecycle_path, handlers_api.EXISTING_IGNORE))
        if lifecycle_type == LIFECYCLE_TYPE_ANSIBLE:
            file_ops.append(handlers_api.CreateDirectoryOp(source_tree.ansible_lifecycle_path, handlers_api.EXISTING_IGNORE))
            ansible_tree = AnsibleLifecycleTree(source_tree.ansible_lifecycle_path)
            file_ops.append(handlers_api.CreateDirectoryOp(ansible_tree.config_path, handlers_api.EXISTING_IGNORE))
            file_ops.append(handlers_api.CreateDirectoryOp(ansible_tree.hostvars_path, handlers_api.EXISTING_IGNORE))
            file_ops.append(handlers_api.CreateDirectoryOp(ansible_tree.scripts_path, handlers_api.EXISTING_IGNORE))
            install_content = '---\n- name: Install\n  hosts: all\n  gather_facts: False'
            file_ops.append(handlers_api.CreateFileOp(ansible_tree.gen_script_file_path('Install'), install_content, handlers_api.EXISTING_IGNORE))
            descriptor.insert_lifecycle('Install')
            inventory_content = '[example]\nexample-host'
            file_ops.append(handlers_api.CreateFileOp(ansible_tree.inventory_file_path, inventory_content, handlers_api.EXISTING_IGNORE))
            host_var_content = '---\nansible_host: {{ properties.host }}\nansible_ssh_user: {{ properties.ssh_user }}\nansible_ssh_pass: {{ properties.ssh_pass }}'
            file_ops.append(handlers_api.CreateFileOp(ansible_tree.gen_hostvars_file_path('example-host'), host_var_content, handlers_api.EXISTING_IGNORE))
            descriptor.insert_default_driver('ansible', infrastructure_types=['*'])
        elif lifecycle_type == LIFECYCLE_TYPE_SOL003:
            file_ops.append(handlers_api.CreateDirectoryOp(source_tree.sol003_lifecycle_path, handlers_api.EXISTING_IGNORE))
            sol003_tree = Sol003LifecycleTree(source_tree.sol003_lifecycle_path)
            file_ops.append(handlers_api.CreateDirectoryOp(sol003_tree.scripts_path, handlers_api.EXISTING_IGNORE))
            current_path = os.path.abspath(__file__)
            dir_path = os.path.dirname(current_path)
            sol003_scripts_template_path = os.path.join(dir_path, 'sol003', 'scripts')
            for script_name in SOL003_SCRIPT_NAMES:
                orig_script_path = os.path.join(sol003_scripts_template_path, script_name)
                with open(orig_script_path, 'r') as f:
                    content = f.read()
                file_ops.append(handlers_api.CreateFileOp(os.path.join(sol003_tree.scripts_path, script_name), content, handlers_api.EXISTING_IGNORE))
            descriptor.insert_default_driver('sol003', infrastructure_types=['*'])
            descriptor.add_property('vnfdId', description='Identifier for the VNFD to use for this VNF instance', ptype='string', required=True)
            descriptor.add_property('vnfInstanceId', description='Identifier for the VNF instance, as provided by the vnfInstanceName', ptype='string', read_only=True)
            descriptor.add_property('vnfInstanceName', description='Name for the VNF instance', ptype='string', value='${name}')
            descriptor.add_property('vnfInstanceDescription', description='Optional description for the VNF instance', ptype='string')
            descriptor.add_property('vnfPkgId', description='Identifier for the VNF package to be used for this VNF instance', ptype='string', required=True)
            descriptor.add_property('vnfProvider', description='Provider of the VNF and VNFD', ptype='string', read_only=True)
            descriptor.add_property('vnfProductName', description='VNF Product Name', ptype='string', read_only=True)
            descriptor.add_property('vnfSoftwareVersion', description='VNF Software Version', ptype='string', read_only=True)
            descriptor.add_property('vnfdVersion', description='Version of the VNFD', ptype='string', read_only=True)
            descriptor.add_property('flavourId', description='Identifier of the VNF DF to be instantiated', ptype='string', required=True)
            descriptor.add_property('instantiationLevelId', description='Identifier of the instantiation level of the deployment flavour to be instantiated. If not present, the default instantiation level as declared in the VNFD is instantiated', \
                ptype='string')
            descriptor.add_property('localizationLanguage', description='Localization language of the VNF to be instantiated', ptype='string')    
            descriptor.insert_lifecycle('Install')
            descriptor.insert_lifecycle('Configure')
            descriptor.insert_lifecycle('Uninstall')

class BrentSourceHandlerDelegate(handlers_api.ResourceSourceHandlerDelegate):
    
    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)
        self.tree = BrentSourceTree(self.root_path)

    def validate_sources(self, journal, source_validator, validation_options):
        errors = []
        warnings = []
        self.__validate_definitions(journal, validation_options, errors, warnings)
        self.__validate_lifecycle(journal, validation_options, errors, warnings)
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

    def __validate_definitions(self, journal, validation_options, errors, warnings):
        definitions_path = self.tree.definitions_path
        if self.__find_or_error(journal, errors, warnings, definitions_path, 'Definitions directory'):
            self.__validate_definitions_infrastructure(journal, validation_options, errors, warnings)
            self.__validate_definitions_lm(journal, errors, warnings)

    def __validate_definitions_infrastructure(self, journal, validation_options, errors, warnings):
        inf_path = self.tree.infrastructure_definitions_path
        if self.__find_or_error(journal, errors, warnings, inf_path, 'Infrastructure definitions directory'):
            self.__validate_unsupported_infrastructure_manifest(journal, validation_options, errors, warnings)

    def __validate_unsupported_infrastructure_manifest(self, journal, validation_options, errors, warnings):
        inf_manifest_path = self.tree.infrastructure_manifest_file_path
        if os.path.exists(inf_manifest_path):
            if validation_options.allow_autocorrect == True:
                journal.event('Found unsupported infrastructure manifest [{0}], attempting to autocorrect by moving contents to Resource descriptor'.format(inf_manifest_path))
                managed_to_autocorrect = False
                autocorrect_error = None
                try:
                    with open(inf_manifest_path, 'r') as f:
                        inf_manifest_content = yaml.safe_load(f.read())
                    descriptor = descriptor_utils.DescriptorParser().read_from_file(self.get_main_descriptor())
                    descriptor.is_2_dot_1 = True
                    if 'templates' in inf_manifest_content:
                        for template_entry in inf_manifest_content['templates']:
                            if 'infrastructure_type' in template_entry:
                                infrastructure_type = template_entry['infrastructure_type']
                                template_file = template_entry.get('file', None)
                                template_type = template_entry.get('template_type', None)
                                descriptor.insert_infrastructure_template(infrastructure_type, template_file, template_type=template_type)
                    if 'discover' in inf_manifest_content:
                        for discover_entry in inf_manifest_content['discover']:
                            if 'infrastructure_type' in discover_entry:
                                infrastructure_type = discover_entry['infrastructure_type']
                                template_file = discover_entry.get('file', None)
                                template_type = discover_entry.get('template_type', None)
                                descriptor.insert_infrastructure_discover(infrastructure_type, template_file, template_type=template_type)
                    descriptor_utils.DescriptorParser().write_to_file(descriptor, self.get_main_descriptor())
                    os.rename(inf_manifest_path, inf_manifest_path + '.bak')
                    managed_to_autocorrect = True
                except Exception as e:
                    autocorrect_error = e
                if not managed_to_autocorrect:
                    msg = 'Found infrastructure manifest [{0}]: this file is no longer supported by the Brent Resource Manager. Unable to autocorrect this issue, please add this information to the Resource descriptor manually instead'.format(inf_manifest_path)
                    if autocorrect_error is not None:
                        msg += ' (autocorrect error={0})'.format(str(autocorrect_error))
                    journal.error_event(msg)
                    errors.append(project_validation.ValidationViolation(msg))
                    return    
            else:
                msg = 'Found infrastructure manifest [{0}]: this file is no longer supported by the Brent Resource Manager. Add this information to the Resource descriptor instead or enable the autocorrect option'.format(inf_manifest_path)
                journal.error_event(msg)
                errors.append(project_validation.ValidationViolation(msg))
                return

    def __validate_definitions_lm(self, journal, errors, warnings):
        lm_def_path = self.tree.lm_definitions_path
        if self.__find_or_error(journal, errors, warnings, lm_def_path, 'CP4NA orchestration definitions directory'):
            descriptor_file_path = self.tree.descriptor_file_path
            self.__find_or_error(journal, errors, warnings, descriptor_file_path, 'Resource descriptor')

    def __validate_lifecycle(self, journal, validation_options, errors, warnings):
        lifecycle_path = self.tree.lifecycle_path
        if self.__find_or_error(journal, errors, warnings, lifecycle_path, 'Lifecycle directory'):
            self.__validate_unsupported_lifecycle_manifest(journal, validation_options, errors, warnings)

    def __validate_unsupported_lifecycle_manifest(self, journal, validation_options, errors, warnings):
        lifecycle_manifest_path = self.tree.lifecycle_manifest_file_path
        if os.path.exists(lifecycle_manifest_path):
            if validation_options.allow_autocorrect == True:
                journal.event('Found unsupported lifecycle manifest [{0}], attempting to autocorrect by moving contents to Resource descriptor'.format(lifecycle_manifest_path))
                managed_to_autocorrect = False
                autocorrect_error = None
                try:
                    with open(lifecycle_manifest_path, 'r') as f:
                        lifecycle_manifest_content = yaml.safe_load(f.read())
                    descriptor = descriptor_utils.DescriptorParser().read_from_file(self.get_main_descriptor())
                    descriptor.is_2_dot_1 = True
                    if 'types' in lifecycle_manifest_content:
                        for entry in lifecycle_manifest_content['types']:
                            if 'lifecycle_type' in entry and 'infrastructure_type' in entry:
                                lifecycle_type = entry['lifecycle_type']
                                infrastructure_type = entry['infrastructure_type']
                                if lifecycle_type in descriptor.default_driver and 'infrastructure-type' in descriptor.default_driver[lifecycle_type]:
                                    descriptor.default_driver[lifecycle_type]['infrastructure-type'].append(infrastructure_type)
                                else:
                                    descriptor.insert_default_driver(lifecycle_type, [infrastructure_type])
                    descriptor_utils.DescriptorParser().write_to_file(descriptor, self.get_main_descriptor())
                    os.rename(lifecycle_manifest_path, lifecycle_manifest_path + '.bak')
                    managed_to_autocorrect = True
                except Exception as e:
                    autocorrect_error = e
                if not managed_to_autocorrect:
                    msg = 'Found lifecycle manifest [{0}]: this file is no longer supported by the Brent Resource Manager. Unable to autocorrect this issue, please add this information to the Resource descriptor manually instead'.format(lifecycle_manifest_path)
                    if autocorrect_error is not None:
                        msg += ' (autocorrect error={0})'.format(str(autocorrect_error))
                    journal.error_event(msg)
                    errors.append(project_validation.ValidationViolation(msg))
                    return 
            else:
                msg = 'Found lifecycle manifest [{0}]: this file is no longer supported by the Brent Resource Manager. Add this information to the Resource descriptor instead or enable the autocorrect option'.format(lifecycle_manifest_path)
                journal.error_event(msg)
                errors.append(project_validation.ValidationViolation(msg))
                return

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
                for dirname in dirs:
                    full_path = os.path.join(root, dirname)
                    res_pkg.write(full_path, arcname=os.path.join(included_item['alias'], full_path[rootlen:]))
                for filename in files:
                    full_path = os.path.join(root, filename)
                    res_pkg.write(full_path, arcname=os.path.join(included_item['alias'], full_path[rootlen:]))
        else:
            if included_item['required']:
                msg = 'Required directory for Resource package not found: {0}'.format(path)
                journal.error_event(msg)
                raise handlers_api.SourceHandlerError(msg)
            else:
                journal.event('Skipping directory for Resource package, not found: {0}'.format(path))