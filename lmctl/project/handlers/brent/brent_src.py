import os
import yaml
import zipfile
import shutil
import lmctl.files as files
import lmctl.project.handlers.interface as handlers_api
import lmctl.project.validation as project_validation
import lmctl.utils.descriptors as descriptor_utils
from .brent_content import BrentResourcePackageContentTree, BrentPkgContentTree
from .brent_autocorrect import BrentCorrectableValidation

class OpenstackTree(files.Tree):

    HEAT_FILE_NAME_YAML = 'heat.yaml'
    HEAT_FILE_NAME_YML = 'heat.yml'
    TOSCA_FILE_NAME_YAML = 'tosca.yaml'
    TOSCA_FILE_NAME_YML = 'tosca.yml'
    DISCOVER_FILE_NAME_YAML = 'discover.yaml'
    DISCOVER_FILE_NAME_YML = 'discover.yml'

    @property
    def heat_file_path(self):
        yaml_path = self.resolve_relative_path(OpenstackTree.HEAT_FILE_NAME_YAML)
        yml_path = self.resolve_relative_path(OpenstackTree.HEAT_FILE_NAME_YML)
        if os.path.exists(yml_path):
            if os.path.exists(yaml_path):
                raise handlers_api.InvalidSourceError('Project has both a {0} file and a {1} file when there should only be one'.format(
                    OpenstackTree.HEAT_FILE_NAME_YAML, OpenstackTree.HEAT_FILE_NAME_YML))
            return yml_path
        else:
            return yaml_path

    @property
    def tosca_file_path(self):
        yaml_path = self.resolve_relative_path(OpenstackTree.TOSCA_FILE_NAME_YAML)
        yml_path = self.resolve_relative_path(OpenstackTree.TOSCA_FILE_NAME_YML)
        if os.path.exists(yml_path):
            if os.path.exists(yaml_path):
                raise handlers_api.InvalidSourceError('Project has both a {0} file and a {1} file when there should only be one'.format(
                    OpenstackTree.TOSCA_FILE_NAME_YAML, OpenstackTree.TOSCA_FILE_NAME_YML))
            return yml_path
        else:
            return yaml_path

    @property
    def discover_file_path(self):
        yaml_path = self.resolve_relative_path(OpenstackTree.DISCOVER_FILE_NAME_YAML)
        yml_path = self.resolve_relative_path(OpenstackTree.DISCOVER_FILE_NAME_YML)
        if os.path.exists(yml_path):
            if os.path.exists(yaml_path):
                raise handlers_api.InvalidSourceError('Project has both a {0} file and a {1} file when there should only be one'.format(
                    OpenstackTree.DISCOVER_FILE_NAME_YAML, OpenstackTree.DISCOVER_FILE_NAME_YML))
            return yml_path
        else:
            return yaml_path

OPENSTACK_EXAMPLE_HEAT = '''\
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

KEGD_INF_TEMPLATE = '''\
compose:
  - name: Create
    deploy:
      - objects:
          file: config-map.yaml
'''

KEGD_LIFECYCLE_TEMPLATE = '''\
compose:
  - name: Create
    deploy:
      - objects:
          file: config-map.yaml

  - name: Install
    deploy:
      - objects:
          file: deployment.yaml
'''

CONFIG_MAP_TEMPLATE = '''\
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ system_properties.resource_subdomain }}
data: {}
'''

DEPLOYMENT_TEMPLATE = '''\
apiVersion: extensions/v1beta1
kind: Deployment
metadata:
  name: {{ system_properties.resource_subdomain }}
spec:
  replicas: 1
  template:
    metadata:
      labels:
        app: busybox
    spec:
      containers:
        - name: busybox
          image: busybox
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

class Sol005LifecycleTree(files.Tree):
    SCRIPTS_DIR_NAME = 'scripts'
    CREATE_NS_REQUEST_FILE_NAME = 'CreateNsRequest.js'
    HEAL_NS_REQUEST_FILE_NAME = 'HealNsRequest.js'
    INSTANTIATE_NS_REQUEST_FILE_NAME = 'InstantiateNsRequest.js'
    UPDATE_NS_REQUEST_START_FILE_NAME = 'UpdateNsRequest-Start.js'
    UPDATE_NS_REQUEST_STOP_FILE_NAME = 'UpdateNsRequest-Stop.js'
    SCALE_NS_REQUEST_FILE_NAME = 'ScaleNsRequest.js'
    TERMINATE_NS_REQUEST_FILE_NAME = 'TerminateNsRequest.js'
    NS_INSTANCE_FILE_NAME = 'NsInstance.js'

    @property
    def scripts_path(self):
        return self.resolve_relative_path(Sol005LifecycleTree.SCRIPTS_DIR_NAME)
        
class RestConfTree(files.Tree):
    TEMPLATE_DIR_NAME = 'template'
    CREATE_RC_REQUEST_FILE_NAME = 'Create.xml'
    UPDATE_RC_REQUEST_FILE_NAME = 'Update.xml'
    DELETE_RC_REQUEST_FILE_NAME = 'Delete.xml'

    @property
    def scripts_path(self):
        return self.resolve_relative_path(RestConfTree.TEMPLATE_DIR_NAME)
    
class NetConfTree(files.Tree):
    TEMPLATE_DIR_NAME = 'template'
    RSA_DIR_NAME = 'keys'
    CREATE_NC_REQUEST_FILE_NAME = 'Create.xml'
    UPDATE_NC_REQUEST_FILE_NAME = 'Update.xml'
    DELETE_NC_REQUEST_FILE_NAME = 'Delete.xml'

    @property
    def scripts_path(self):
        return self.resolve_relative_path(NetConfTree.TEMPLATE_DIR_NAME)
    
    @property
    def rsa_path(self):
        return self.resolve_relative_path(NetConfTree.RSA_DIR_NAME)

class KubernetesLifecycleTree(files.Tree):
    
    OBJECTS_DIR_NAME = 'objects'
    HELM_DIR_NAME = 'helm'
    KEGD_FILE_NAME = 'kegd.yaml'

    @property
    def objects_path(self):
        return self.resolve_relative_path(KubernetesLifecycleTree.OBJECTS_DIR_NAME)

    def gen_object_file_path(self, object_name):
        return self.resolve_relative_path(KubernetesLifecycleTree.OBJECTS_DIR_NAME, '{0}.yaml'.format(object_name))

    @property
    def helm_path(self):
        return self.resolve_relative_path(KubernetesLifecycleTree.HELM_DIR_NAME)

    @property
    def kegd_file_path(self):
        return self.resolve_relative_path(KubernetesLifecycleTree.KEGD_FILE_NAME)

class BrentSourceTree(files.Tree):

    DEFINITIONS_DIR_NAME = 'Definitions'
    INFRASTRUCTURE_DIR_NAME = 'infrastructure'
    INFRASTRUCTURE_MANIFEST_FILE_NAME = 'infrastructure.mf'
    LM_DIR_NAME = 'lm'
    DESCRIPTOR_FILE_NAME_YML = 'resource.yml'
    DESCRIPTOR_FILE_NAME_YAML = 'resource.yaml'

    LIFECYCLE_DIR_NAME = 'Lifecycle'
    LIFECYCLE_MANIFEST_FILE_NAME = 'lifecycle.mf'
    OPENSTACK_LIFECYCLE_DIR_NAME = 'openstack'
    ANSIBLE_LIFECYCLE_DIR_NAME = 'ansible'
    SOL003_LIFECYCLE_DIR_NAME = 'sol003'
    SOL005_LIFECYCLE_DIR_NAME = 'sol005'
    KUBERNETES_LIFECYCLE_DIR_NAME = 'kubernetes'
    RESTCONF_LIFECYCLE_DIR_NAME = 'restconf'
    NETCONF_LIFECYCLE_DIR_NAME = 'netconf'
    
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
    def openstack_lifecycle_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.OPENSTACK_LIFECYCLE_DIR_NAME)

    @property
    def ansible_lifecycle_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.ANSIBLE_LIFECYCLE_DIR_NAME)

    @property
    def sol003_lifecycle_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.SOL003_LIFECYCLE_DIR_NAME)

    @property
    def sol005_lifecycle_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.SOL005_LIFECYCLE_DIR_NAME)

    @property
    def kubernetes_lifecycle_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.KUBERNETES_LIFECYCLE_DIR_NAME)
        
    @property
    def restconf_lifecycle_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.RESTCONF_LIFECYCLE_DIR_NAME)
    
    @property
    def netconf_lifecycle_path(self):
        return self.resolve_relative_path(BrentSourceTree.LIFECYCLE_DIR_NAME, BrentSourceTree.NETCONF_LIFECYCLE_DIR_NAME)
        

DRIVER_PARAM_NAME = 'driver'
INFRASTRUCTURE_PARAM_NAME = 'inf'
LIFECYCLE_PARAM_NAME = 'lifecycle'
LIFECYCLE_TYPE_ANSIBLE = 'ansible'
LIFECYCLE_TYPE_SOL003 = 'sol003'
LIFECYCLE_TYPE_SOL005 = 'sol005'
LIFECYCLE_TYPE_KUBERNETES = 'kubernetes'
LIFECYCLE_TYPE_RESTCONF = 'restconf'
LIFECYCLE_TYPE_NETCONF = 'netconf'
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
SOL005_SCRIPT_NAMES = []
SOL005_SCRIPT_NAMES.append(Sol005LifecycleTree.CREATE_NS_REQUEST_FILE_NAME)
SOL005_SCRIPT_NAMES.append(Sol005LifecycleTree.HEAL_NS_REQUEST_FILE_NAME)
SOL005_SCRIPT_NAMES.append(Sol005LifecycleTree.INSTANTIATE_NS_REQUEST_FILE_NAME)
SOL005_SCRIPT_NAMES.append(Sol005LifecycleTree.UPDATE_NS_REQUEST_START_FILE_NAME)
SOL005_SCRIPT_NAMES.append(Sol005LifecycleTree.UPDATE_NS_REQUEST_STOP_FILE_NAME)
SOL005_SCRIPT_NAMES.append(Sol005LifecycleTree.SCALE_NS_REQUEST_FILE_NAME)
SOL005_SCRIPT_NAMES.append(Sol005LifecycleTree.TERMINATE_NS_REQUEST_FILE_NAME)
SOL005_SCRIPT_NAMES.append(Sol005LifecycleTree.NS_INSTANCE_FILE_NAME)
RESTCONF_SCRIPT_NAMES = []
RESTCONF_SCRIPT_NAMES.append(RestConfTree.CREATE_RC_REQUEST_FILE_NAME)
RESTCONF_SCRIPT_NAMES.append(RestConfTree.UPDATE_RC_REQUEST_FILE_NAME)
RESTCONF_SCRIPT_NAMES.append(RestConfTree.DELETE_RC_REQUEST_FILE_NAME)
NETCONF_SCRIPT_NAMES = []
NETCONF_SCRIPT_NAMES.append(NetConfTree.CREATE_NC_REQUEST_FILE_NAME)
NETCONF_SCRIPT_NAMES.append(NetConfTree.UPDATE_NC_REQUEST_FILE_NAME)
NETCONF_SCRIPT_NAMES.append(NetConfTree.DELETE_NC_REQUEST_FILE_NAME)
NETCONF_RSA_NAME = "id_rsa"

class BrentSourceCreatorDelegate(handlers_api.ResourceSourceCreatorDelegate):

    def __init__(self):
        super().__init__()

    def get_params(self, source_request):
        params = []
        params.append(handlers_api.SourceParam(DRIVER_PARAM_NAME, required=False, default_value=None, allowed_values=[LIFECYCLE_TYPE_ANSIBLE, LIFECYCLE_TYPE_SOL003, LIFECYCLE_TYPE_SOL005, LIFECYCLE_TYPE_KUBERNETES, LIFECYCLE_TYPE_RESTCONF, LIFECYCLE_TYPE_NETCONF]))
        params.append(handlers_api.SourceParam(LIFECYCLE_PARAM_NAME, required=False, default_value=None, allowed_values=[LIFECYCLE_TYPE_ANSIBLE, LIFECYCLE_TYPE_SOL003, LIFECYCLE_TYPE_SOL005, LIFECYCLE_TYPE_KUBERNETES, LIFECYCLE_TYPE_RESTCONF, LIFECYCLE_TYPE_NETCONF]))
        params.append(handlers_api.SourceParam(INFRASTRUCTURE_PARAM_NAME, required=False, default_value=None, allowed_values=[INFRASTRUCTURE_TYPE_OPENSTACK, LIFECYCLE_TYPE_KUBERNETES]))
        return params

    def create_source(self, journal, source_request, file_ops_executor):
        source_tree = BrentSourceTree()
        file_ops = []
        descriptor = descriptor_utils.Descriptor({})
        descriptor.description = 'descriptor for {0}'.format(source_request.source_config.name)
        had_inf = False
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.definitions_path, handlers_api.EXISTING_IGNORE))
        driver_type = source_request.param_values.get_value(DRIVER_PARAM_NAME)
        driver_type_set_to_default = False
        if driver_type is None:
            driver_type = source_request.param_values.get_value(LIFECYCLE_PARAM_NAME)
            if driver_type is None:
                driver_type = LIFECYCLE_TYPE_ANSIBLE
                driver_type_set_to_default = True
        inf_type = source_request.param_values.get_value(INFRASTRUCTURE_PARAM_NAME)
        if inf_type is None:
            if driver_type == LIFECYCLE_TYPE_ANSIBLE and driver_type_set_to_default:
                inf_type = INFRASTRUCTURE_TYPE_OPENSTACK
        if inf_type is not None:
            had_inf = True
            self.__create_infrastructure(journal, source_request, file_ops, source_tree, inf_type, descriptor)
        
        self.__create_lifecycle(journal, source_request, file_ops, source_tree, driver_type, descriptor, had_inf=had_inf)
        self.__create_descriptor(journal, source_request, file_ops, source_tree, descriptor)
        
        file_ops_executor(file_ops)

    def __create_descriptor(self, journal, source_request, file_ops, source_tree, descriptor):
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.lm_definitions_path, handlers_api.EXISTING_IGNORE))
        descriptor_content = descriptor_utils.DescriptorParser().write_to_str(descriptor)
        file_ops.append(handlers_api.CreateFileOp(source_tree.descriptor_file_path, descriptor_content, handlers_api.EXISTING_IGNORE))

    def __create_infrastructure(self, journal, source_request, file_ops, source_tree, inf_type, descriptor):
        if inf_type == INFRASTRUCTURE_TYPE_OPENSTACK:
            create_driver_entry = {
                'openstack': {
                    'selector': {
                        'infrastructure-type': [
                            '*'
                        ]
                    }
                }
            }
            descriptor.insert_lifecycle('Create', drivers=create_driver_entry)
            delete_driver_entry = {
                'openstack': {
                    'selector': {
                        'infrastructure-type': [
                            '*'
                        ]
                    }
                }
            }
            descriptor.insert_lifecycle('Delete', drivers=delete_driver_entry)
            file_ops.append(handlers_api.CreateDirectoryOp(source_tree.openstack_lifecycle_path, handlers_api.EXISTING_IGNORE))
            openstack_tree = OpenstackTree(source_tree.openstack_lifecycle_path)
            file_ops.append(handlers_api.CreateFileOp(openstack_tree.heat_file_path, OPENSTACK_EXAMPLE_HEAT, handlers_api.EXISTING_IGNORE))
            descriptor.infrastructure['Openstack'] = {}
        elif inf_type == LIFECYCLE_TYPE_KUBERNETES:
            file_ops.append(handlers_api.CreateDirectoryOp(source_tree.kubernetes_lifecycle_path, handlers_api.EXISTING_IGNORE))
            kube_tree = KubernetesLifecycleTree(source_tree.kubernetes_lifecycle_path)
            file_ops.append(handlers_api.CreateDirectoryOp(kube_tree.objects_path, handlers_api.EXISTING_IGNORE))
            file_ops.append(handlers_api.CreateDirectoryOp(kube_tree.helm_path, handlers_api.EXISTING_IGNORE))
            file_ops.append(handlers_api.CreateFileOp(kube_tree.kegd_file_path, KEGD_INF_TEMPLATE, handlers_api.EXISTING_IGNORE))
            file_ops.append(handlers_api.CreateFileOp(kube_tree.gen_object_file_path('config-map'), CONFIG_MAP_TEMPLATE, handlers_api.EXISTING_IGNORE))
            create_driver_entry = {
                'kubernetes': {
                    'selector': {
                        'infrastructure-type': [
                            '*'
                        ]
                    }
                }
            }
            descriptor.insert_lifecycle('Create', drivers=create_driver_entry)
            delete_driver_entry = {
                'kubernetes': {
                    'selector': {
                        'infrastructure-type': [
                            '*'
                        ]
                    }
                }
            }
            descriptor.insert_lifecycle('Delete', drivers=delete_driver_entry)
            descriptor.infrastructure['Kubernetes'] = {}

    def __create_lifecycle(self, journal, source_request, file_ops, source_tree, lifecycle_type, descriptor, had_inf=False):
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.lifecycle_path, handlers_api.EXISTING_IGNORE))
        if lifecycle_type == LIFECYCLE_TYPE_KUBERNETES:
            file_ops.append(handlers_api.CreateDirectoryOp(source_tree.kubernetes_lifecycle_path, handlers_api.EXISTING_IGNORE))
            kube_tree = KubernetesLifecycleTree(source_tree.kubernetes_lifecycle_path)
            file_ops.append(handlers_api.CreateDirectoryOp(kube_tree.objects_path, handlers_api.EXISTING_IGNORE))
            file_ops.append(handlers_api.CreateDirectoryOp(kube_tree.helm_path, handlers_api.EXISTING_IGNORE))
            file_ops.append(handlers_api.CreateFileOp(kube_tree.kegd_file_path, KEGD_LIFECYCLE_TEMPLATE, handlers_api.EXISTING_IGNORE))
            if not had_inf:
                file_ops.append(handlers_api.CreateFileOp(kube_tree.gen_object_file_path('config-map'), CONFIG_MAP_TEMPLATE, handlers_api.EXISTING_IGNORE))
                descriptor.insert_lifecycle('Create')
                descriptor.insert_lifecycle('Delete')
                descriptor.infrastructure['Kubernetes'] = {}
            file_ops.append(handlers_api.CreateFileOp(kube_tree.gen_object_file_path('deployment'), DEPLOYMENT_TEMPLATE, handlers_api.EXISTING_IGNORE))
            descriptor.insert_lifecycle('Install')
            descriptor.insert_default_driver('kubernetes', infrastructure_types=['*'])
        elif lifecycle_type == LIFECYCLE_TYPE_ANSIBLE:
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
        elif lifecycle_type == LIFECYCLE_TYPE_SOL005:
            file_ops.append(handlers_api.CreateDirectoryOp(source_tree.sol005_lifecycle_path, handlers_api.EXISTING_IGNORE))
            sol005_tree = Sol005LifecycleTree(source_tree.sol005_lifecycle_path)
            file_ops.append(handlers_api.CreateDirectoryOp(sol005_tree.scripts_path, handlers_api.EXISTING_IGNORE))
            current_path = os.path.abspath(__file__)
            dir_path = os.path.dirname(current_path)
            sol005_scripts_template_path = os.path.join(dir_path, 'sol005', 'scripts')
            for script_name in SOL005_SCRIPT_NAMES:
                orig_script_path = os.path.join(sol005_scripts_template_path, script_name)
                with open(orig_script_path, 'r') as f:
                    content = f.read()
                file_ops.append(handlers_api.CreateFileOp(os.path.join(sol005_tree.scripts_path, script_name), content, handlers_api.EXISTING_IGNORE))
            descriptor.insert_default_driver('sol005', infrastructure_types=['*'])
            descriptor.add_property('nsdId', description='Identifier for the NSD to use for this NS instance', ptype='string', required=True)
            descriptor.add_property('nsInstanceId', description='Identifier for the NS instance, as provided by the nsInstanceName', ptype='string', read_only=True)
            descriptor.add_property('nsInstanceName', description='Name for the NS instance', ptype='string', value='${name}')
            descriptor.add_property('nsInstanceDescription', description='Optional description for the NS instance', ptype='string')
            descriptor.add_property('nsPkgId', description='Identifier for the NS package to be used for this NS instance', ptype='string', required=True)
            descriptor.add_property('nsProvider', description='Provider of the NS and NSD', ptype='string', read_only=True)
            descriptor.add_property('nsProductName', description='NS Product Name', ptype='string', read_only=True)
            descriptor.add_property('nsSoftwareVersion', description='NS Software Version', ptype='string', read_only=True)
            descriptor.add_property('nsdVersion', description='Version of the NSD', ptype='string', read_only=True)
            descriptor.add_property('flavourId', description='Identifier of the NS DF to be instantiated', ptype='string', required=True)
            descriptor.add_property('instantiationLevelId', description='Identifier of the instantiation level of the deployment flavour to be instantiated. If not present, the default instantiation level as declared in the NSD is instantiated', \
                ptype='string')
            descriptor.add_property('localizationLanguage', description='Localization language of the NS to be instantiated', ptype='string')
            descriptor.insert_lifecycle('Create')
            descriptor.insert_lifecycle('Install')
            descriptor.insert_lifecycle('Uninstall')
            descriptor.insert_lifecycle('Delete')
        elif lifecycle_type == LIFECYCLE_TYPE_RESTCONF:
            file_ops.append(
                handlers_api.CreateDirectoryOp(source_tree.restconf_lifecycle_path, handlers_api.EXISTING_IGNORE))
            restconf_tree = RestConfTree(source_tree.restconf_lifecycle_path)
            file_ops.append(handlers_api.CreateDirectoryOp(restconf_tree.scripts_path, handlers_api.EXISTING_IGNORE))
            current_path = os.path.abspath(__file__)
            dir_path = os.path.dirname(current_path)
            restconf_scripts_template_path = os.path.join(dir_path, 'restconf', 'template')
            for script_name in RESTCONF_SCRIPT_NAMES:
                orig_script_path = os.path.join(restconf_scripts_template_path, script_name)
                with open(orig_script_path, 'r') as f:
                    content = f.read()
                file_ops.append(handlers_api.CreateFileOp(os.path.join(restconf_tree.scripts_path, script_name), content,
                                                          handlers_api.EXISTING_IGNORE))
            descriptor.insert_default_driver('restconf', infrastructure_types=['*'])
            descriptor.add_property('id', description='Identifier for the ID',
                                    ptype='string', required=True)
            descriptor.add_property('type',
                                    description='Identifier for the type',
                                    ptype='string', read_only=True)
            descriptor.add_property('ipaddress', description='IPAddress', ptype='string',
                                    value='${name}')
            descriptor.add_property('neighborIPv4', description='Optional neighborIPv4',
                                    ptype='string')
            descriptor.add_property('remoteAsIPv4', description='remoteAsIPv4',
                                    ptype='string', required=True)
            descriptor.insert_lifecycle('Create')
            descriptor.insert_lifecycle('Update')
            descriptor.insert_lifecycle('Delete') 
        elif lifecycle_type == LIFECYCLE_TYPE_NETCONF:
            file_ops.append(
                handlers_api.CreateDirectoryOp(source_tree.netconf_lifecycle_path, handlers_api.EXISTING_IGNORE))
            netconf_tree = NetConfTree(source_tree.netconf_lifecycle_path)
            file_ops.append(handlers_api.CreateDirectoryOp(netconf_tree.rsa_path, handlers_api.EXISTING_IGNORE))
            file_ops.append(handlers_api.CreateDirectoryOp(netconf_tree.scripts_path, handlers_api.EXISTING_IGNORE))
            current_path = os.path.abspath(__file__)
            dir_path = os.path.dirname(current_path)
            netconf_scripts_template_path = os.path.join(dir_path, 'netconf', 'template')
            netconf_rsa_template_path = os.path.join(dir_path, 'netconf', 'keys')
            for script_name in NETCONF_SCRIPT_NAMES:
                orig_script_path = os.path.join(netconf_scripts_template_path, script_name)
                with open(orig_script_path, 'r') as f:
                    content = f.read()
                file_ops.append(handlers_api.CreateFileOp(os.path.join(netconf_tree.scripts_path, script_name), content,
                                                          handlers_api.EXISTING_IGNORE))
        
            rsa_script_path = os.path.join(netconf_rsa_template_path, NETCONF_RSA_NAME)
            with open(rsa_script_path, 'r') as f:
                content = f.read()
            file_ops.append(handlers_api.CreateFileOp(os.path.join(netconf_tree.rsa_path, NETCONF_RSA_NAME), content,
                                                          handlers_api.EXISTING_IGNORE))

            descriptor.insert_default_driver('netconf', infrastructure_types=['*'])
            descriptor.add_property('netconfId', description='Identifier for the Netconf',
                                    ptype='string', required=True)
            descriptor.add_property('netconfParam',
                                    description='Parmeter for the ID',
                                    ptype='string', required=True)
            descriptor.add_property('defaultOperation',
                                    description='Acceptable values - merge, replace, none',
                                    ptype='string')
            descriptor.insert_lifecycle('Create')
            descriptor.insert_lifecycle('Delete')
            descriptor.insert_lifecycle('Upgrade')

class BrentSourceHandlerDelegate(handlers_api.ResourceSourceHandlerDelegate):
    
    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)
        self.tree = BrentSourceTree(self.root_path)

    def validate_sources(self, journal, source_validator, validation_options):
        errors = []
        warnings = []
        self.__validate_definitions(journal, validation_options, errors, warnings)
        self.__validate_lifecycle(journal, validation_options, errors, warnings)
        BrentCorrectableValidation().validate_and_autocorrect(journal, validation_options, errors, warnings, self.get_main_descriptor(), \
            self.tree.infrastructure_definitions_path, self.tree.infrastructure_manifest_file_path, self.tree.lifecycle_path, \
                self.tree.lifecycle_manifest_file_path)
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
            self.__validate_definitions_lm(journal, errors, warnings)

    def __validate_definitions_lm(self, journal, errors, warnings):
        lm_def_path = self.tree.lm_definitions_path
        if self.__find_or_error(journal, errors, warnings, lm_def_path, 'CP4NA orchestration definitions directory'):
            descriptor_file_path = self.tree.descriptor_file_path
            self.__find_or_error(journal, errors, warnings, descriptor_file_path, 'Resource descriptor')

    def __validate_lifecycle(self, journal, validation_options, errors, warnings):
        lifecycle_path = self.tree.lifecycle_path
        self.__find_or_error(journal, errors, warnings, lifecycle_path, 'Lifecycle directory')

    def get_main_descriptor(self):
        main_descriptor_path = self.tree.descriptor_file_path
        return main_descriptor_path

    def stage_sources(self, journal, source_stager):
        staging_tree = BrentResourcePackageContentTree()
        journal.event('Staging Resource descriptor for {0} at {1}'.format(self.source_config.full_name, self.get_main_descriptor()))
        source_stager.stage_descriptor(self.get_main_descriptor(), staging_tree.descriptor_file_path)
        included_items = [
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