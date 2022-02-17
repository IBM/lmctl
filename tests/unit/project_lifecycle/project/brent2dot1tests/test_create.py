import unittest
import tempfile
import shutil
import os
from lmctl.project.source.creator import CreateResourceProjectRequest, ResourceSubprojectRequest, ProjectCreator, CreateOptions
from tests.common.project_testing import (ProjectSimTestCase, PROJECT_CONTAINS_DIR, BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR, BRENT_DESCRIPTOR_DIR,
                                            BRENT_LIFECYCLE_MANIFEST_FILE, BRENT_LIFECYCLE_DIR, BRENT_LIFECYCLE_ANSIBLE_DIR, 
                                            BRENT_LIFECYCLE_ANSIBLE_SCRIPTS_DIR, BRENT_LIFECYCLE_ANSIBLE_CONFIG_HOSTVARS_DIR_NAME, 
                                            BRENT_LIFECYCLE_ANSIBLE_CONFIG_DIR, 
                                            BRENT_DESCRIPTOR_YML_FILE, BRENT_INFRASTRUCTURE_MANIFEST_FILE, BRENT_LIFECYCLE_ANSIBLE_INVENTORY_FILE,
                                            BRENT_SOL003_DIR, BRENT_SOL003_SCRIPTS_DIR, BRENT_SOL003_CREATE_VNF_REQUEST_FILE,
                                            BRENT_SOL003_HEAL_VNF_REQUEST_FILE, BRENT_SOL003_INSTANTIATE_VNF_REQUEST_FILE,
                                            BRENT_SOL003_OPERATE_VNF_REQUEST_START_FILE, BRENT_SOL003_OPERATE_VNF_REQUEST_STOP_FILE,
                                            BRENT_SOL003_SCALE_VNF_REQUEST_FILE, BRENT_SOL003_TERMINATE_VNF_REQUEST_FILE,
                                            BRENT_SOL003_VNF_INSTANCE_FILE, BRENT_SOL005_DIR, BRENT_SOL005_SCRIPTS_DIR, BRENT_SOL005_CREATE_NS_REQUEST_FILE,
                                            BRENT_SOL005_HEAL_NS_REQUEST_FILE, BRENT_SOL005_INSTANTIATE_NS_REQUEST_FILE,
                                            BRENT_SOL005_UPDATE_NS_REQUEST_START_FILE, BRENT_SOL005_UPDATE_NS_REQUEST_STOP_FILE,
                                            BRENT_SOL005_SCALE_NS_REQUEST_FILE, BRENT_SOL005_TERMINATE_NS_REQUEST_FILE,
                                            BRENT_SOL005_NS_INSTANCE_FILE)
from lmctl.project.source.core import Project

EXPECTED_OPENSTACK_EXAMPLE_TOSCA = '''\
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

EXPECTED_OS_AND_ANSIBLE_DESCRIPTOR = '''\
description: descriptor for {0}
infrastructure:
  Openstack:
    template:
      file: example.yaml
      template-type: HEAT
lifecycle:
  Create: {{}}
  Install: {{}}
  Delete: {{}}
default-driver:
  ansible:
    infrastructure-type:
    - \'*\'
'''

EXPECTED_ANSIBLE_INSTALL_SCRIPT = '''\
---
- name: Install
  hosts: all
  gather_facts: False'''

EXPECTED_ANSIBLE_INVENTORY = '''\
[example]
example-host'''

EXPECTED_ANSIBLE_HOST_VARS = '''\
---
ansible_host: {{ properties.host }}
ansible_ssh_user: {{ properties.ssh_user }}
ansible_ssh_pass: {{ properties.ssh_pass }}'''

EXPECTED_OS_AND_SOL003_DESCRIPTOR = '''\
description: descriptor for {0}
properties:
  vnfdId:
    description: Identifier for the VNFD to use for this VNF instance
    type: string
    required: true
  vnfInstanceId:
    description: Identifier for the VNF instance, as provided by the vnfInstanceName
    type: string
    read-only: true
  vnfInstanceName:
    description: Name for the VNF instance
    type: string
    value: ${{name}}
  vnfInstanceDescription:
    description: Optional description for the VNF instance
    type: string
  vnfPkgId:
    description: Identifier for the VNF package to be used for this VNF instance
    type: string
    required: true
  vnfProvider:
    description: Provider of the VNF and VNFD
    type: string
    read-only: true
  vnfProductName:
    description: VNF Product Name
    type: string
    read-only: true
  vnfSoftwareVersion:
    description: VNF Software Version
    type: string
    read-only: true
  vnfdVersion:
    description: Version of the VNFD
    type: string
    read-only: true
  flavourId:
    description: Identifier of the VNF DF to be instantiated
    type: string
    required: true
  instantiationLevelId:
    description: Identifier of the instantiation level of the deployment flavour to
      be instantiated. If not present, the default instantiation level as declared
      in the VNFD is instantiated
    type: string
  localizationLanguage:
    description: Localization language of the VNF to be instantiated
    type: string
infrastructure:
  Openstack:
    template:
      file: example.yaml
      template-type: HEAT
lifecycle:
  Create: {{}}
  Install: {{}}
  Configure: {{}}
  Uninstall: {{}}
  Delete: {{}}
default-driver:
  sol003:
    infrastructure-type:
    - \'*\'
'''

EXPECTED_OS_AND_SOL005_DESCRIPTOR = '''\
description: descriptor for {0}
properties:
  nsdId:
    description: Identifier for the NSD to use for this NS instance
    type: string
    required: true
  nsInstanceId:
    description: Identifier for the NS instance, as provided by the nsInstanceName
    type: string
    read-only: true
  nsInstanceName:
    description: Name for the NS instance
    type: string
    value: ${{name}}
  nsInstanceDescription:
    description: Optional description for the NS instance
    type: string
  nsPkgId:
    description: Identifier for the NS package to be used for this NS instance
    type: string
    required: true
  nsProvider:
    description: Provider of the NS and NSD
    type: string
    read-only: true
  nsProductName:
    description: NS Product Name
    type: string
    read-only: true
  nsSoftwareVersion:
    description: NS Software Version
    type: string
    read-only: true
  nsdVersion:
    description: Version of the NSD
    type: string
    read-only: true
  flavourId:
    description: Identifier of the NS DF to be instantiated
    type: string
    required: true
  instantiationLevelId:
    description: Identifier of the instantiation level of the deployment flavour to
      be instantiated. If not present, the default instantiation level as declared
      in the NSD is instantiated
    type: string
  localizationLanguage:
    description: Localization language of the NS to be instantiated
    type: string
infrastructure:
  Openstack:
    template:
      file: example.yaml
      template-type: HEAT
lifecycle:
  Create: {{}}
  Install: {{}}
  Configure: {{}}
  Uninstall: {{}}
  Delete: {{}}
default-driver:
  sol005:
    infrastructure-type:
    - \'*\'
'''

class TestCreateBrentProjects(ProjectSimTestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_create_defaults(self):
        request = CreateResourceProjectRequest()
        request.name = 'Test'
        request.version = '9.9'
        request.target_location = self.tmp_dir
        request.resource_manager = 'brent2.1'
        creator = ProjectCreator(request, CreateOptions())
        creator.create()
        project = Project(self.tmp_dir)
        tester = self.assert_project(project)
        tester.assert_has_config({
            'schema':  '2.0',
            'name': 'Test',
            'version': '9.9',
            'type': 'Resource',
            'packaging': 'tgz',
            'resource-manager': 'brent2.1'
        })
        tester.assert_has_directory(BRENT_DEFINITIONS_DIR)
        inf_dir = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
        tester.assert_has_directory(inf_dir)
        tester.assert_has_file(os.path.join(inf_dir, 'example.yaml'), EXPECTED_OPENSTACK_EXAMPLE_TOSCA)
        lm_dir = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
        tester.assert_has_directory(lm_dir)
        descriptor_path = os.path.join(lm_dir, BRENT_DESCRIPTOR_YML_FILE)
        tester.assert_has_file(descriptor_path, EXPECTED_OS_AND_ANSIBLE_DESCRIPTOR.format('Test'))
        tester.assert_has_directory(os.path.join(BRENT_LIFECYCLE_DIR))
        ansible_dir = os.path.join(BRENT_LIFECYCLE_DIR, BRENT_LIFECYCLE_ANSIBLE_DIR)
        tester.assert_has_directory(ansible_dir)
        ansible_scripts_dir = os.path.join(ansible_dir, BRENT_LIFECYCLE_ANSIBLE_SCRIPTS_DIR)
        tester.assert_has_directory(ansible_scripts_dir)
        tester.assert_has_file(os.path.join(ansible_scripts_dir, 'Install.yaml'), EXPECTED_ANSIBLE_INSTALL_SCRIPT)
        ansible_config_dir = os.path.join(ansible_dir, BRENT_LIFECYCLE_ANSIBLE_CONFIG_DIR)
        tester.assert_has_directory(ansible_config_dir)
        tester.assert_has_file(os.path.join(ansible_config_dir, BRENT_LIFECYCLE_ANSIBLE_INVENTORY_FILE), EXPECTED_ANSIBLE_INVENTORY)
        ansible_hostvars_dir = os.path.join(ansible_config_dir, BRENT_LIFECYCLE_ANSIBLE_CONFIG_HOSTVARS_DIR_NAME)
        tester.assert_has_directory(ansible_hostvars_dir)
        tester.assert_has_file(os.path.join(ansible_hostvars_dir, 'example-host.yml'), EXPECTED_ANSIBLE_HOST_VARS)
    
    def test_create_sol003(self):
        request = CreateResourceProjectRequest()
        request.name = 'Test'
        request.version = '9.9'
        request.target_location = self.tmp_dir
        request.resource_manager = 'brent2.1'
        request.params['lifecycle'] = 'sol003'
        creator = ProjectCreator(request, CreateOptions())
        creator.create()
        project = Project(self.tmp_dir)
        tester = self.assert_project(project)
        tester.assert_has_config({
            'schema':  '2.0',
            'name': 'Test',
            'version': '9.9',
            'type': 'Resource',
            'packaging': 'tgz',
            'resource-manager': 'brent2.1'
        })
        tester.assert_has_directory(os.path.join(BRENT_DEFINITIONS_DIR))
        inf_dir = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
        tester.assert_has_directory(inf_dir)
        tester.assert_has_file(os.path.join(inf_dir, 'example.yaml'), EXPECTED_OPENSTACK_EXAMPLE_TOSCA)
        lm_dir = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
        tester.assert_has_directory(lm_dir)
        descriptor_path = os.path.join(lm_dir, BRENT_DESCRIPTOR_YML_FILE)
        tester.assert_has_file(descriptor_path, EXPECTED_OS_AND_SOL003_DESCRIPTOR.format('Test'))
        tester.assert_has_directory(os.path.join(BRENT_LIFECYCLE_DIR))
        sol003_dir = os.path.join(BRENT_LIFECYCLE_DIR, BRENT_SOL003_DIR)
        tester.assert_has_directory(sol003_dir)
        sol003_scripts_dir = os.path.join(sol003_dir, BRENT_SOL003_SCRIPTS_DIR)
        tester.assert_has_directory(sol003_scripts_dir)
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_CREATE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_HEAL_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_INSTANTIATE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_OPERATE_VNF_REQUEST_START_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_OPERATE_VNF_REQUEST_STOP_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_SCALE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_TERMINATE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_VNF_INSTANCE_FILE))

    def test_create_sol005(self):
        request = CreateResourceProjectRequest()
        request.name = 'Test'
        request.version = '9.9'
        request.target_location = self.tmp_dir
        request.resource_manager = 'brent2.1'
        request.params['lifecycle'] = 'sol005'
        creator = ProjectCreator(request, CreateOptions())
        creator.create()
        project = Project(self.tmp_dir)
        tester = self.assert_project(project)
        tester.assert_has_config({
            'schema':  '2.0',
            'name': 'Test',
            'version': '9.9',
            'type': 'Resource',
            'packaging': 'tgz',
            'resource-manager': 'brent2.1'
        })
        tester.assert_has_directory(os.path.join(BRENT_DEFINITIONS_DIR))
        inf_dir = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
        tester.assert_has_directory(inf_dir)
        tester.assert_has_file(os.path.join(inf_dir, 'example.yaml'), EXPECTED_OPENSTACK_EXAMPLE_TOSCA)
        lm_dir = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
        tester.assert_has_directory(lm_dir)
        descriptor_path = os.path.join(lm_dir, BRENT_DESCRIPTOR_YML_FILE)
        tester.assert_has_file(descriptor_path, EXPECTED_OS_AND_SOL005_DESCRIPTOR.format('Test'))
        tester.assert_has_directory(os.path.join(BRENT_LIFECYCLE_DIR))
        sol005_dir = os.path.join(BRENT_LIFECYCLE_DIR, BRENT_SOL005_DIR)
        tester.assert_has_directory(sol005_dir)
        sol005_scripts_dir = os.path.join(sol005_dir, BRENT_SOL005_SCRIPTS_DIR)
        tester.assert_has_directory(sol005_scripts_dir)
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_CREATE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_HEAL_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_INSTANTIATE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_UPDATE_NS_REQUEST_START_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_UPDATE_NS_REQUEST_STOP_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_SCALE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_TERMINATE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_NS_INSTANCE_FILE))

    def test_create_with_subprojects(self):
        request = CreateResourceProjectRequest()
        request.name = 'Test'
        request.target_location = self.tmp_dir
        request.resource_manager = 'brent2.1'
        request.version = '9.9'
        request.params['lifecycle'] = 'sol003'
        subprojectA_request = ResourceSubprojectRequest()
        subprojectA_request.name = 'SubA'
        subprojectA_request.directory = 'SubprojectA'
        subprojectA_request.resource_manager = 'brent2.1'
        subprojectA_request.params['lifecycle'] = 'ansible'
        request.subproject_requests.append(subprojectA_request)
        subprojectB_request = ResourceSubprojectRequest()
        subprojectB_request.name = 'SubB'
        subprojectB_request.directory = 'SubprojectB'
        subprojectB_request.resource_manager = 'brent2.1'
        request.subproject_requests.append(subprojectB_request)
        creator = ProjectCreator(request, CreateOptions())
        creator.create()
        project = Project(self.tmp_dir)
        tester = self.assert_project(project)
        tester.assert_has_config({
            'schema':  '2.0',
            'name': 'Test',
            'version': '9.9',
            'type': 'Resource',
            'packaging': 'tgz',
            'resource-manager': 'brent2.1',
            'contains': [
                {
                    'name': 'SubA',
                    'directory': 'SubprojectA',
                    'type': 'Resource',
                    'resource-manager': 'brent2.1'
                },
                {
                    'name': 'SubB',
                    'directory':  'SubprojectB',
                    'type': 'Resource',
                    'resource-manager': 'brent2.1'
                }
            ]
        })
        tester.assert_has_directory(os.path.join(BRENT_DEFINITIONS_DIR))
        inf_dir = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
        tester.assert_has_directory(inf_dir)
        tester.assert_has_file(os.path.join(inf_dir, 'example.yaml'), EXPECTED_OPENSTACK_EXAMPLE_TOSCA)
        lm_dir = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
        tester.assert_has_directory(lm_dir)
        descriptor_path = os.path.join(lm_dir, BRENT_DESCRIPTOR_YML_FILE)
        tester.assert_has_file(descriptor_path, EXPECTED_OS_AND_SOL003_DESCRIPTOR.format('Test'))
        tester.assert_has_directory(os.path.join(BRENT_LIFECYCLE_DIR))
        sol003_dir = os.path.join(BRENT_LIFECYCLE_DIR, BRENT_SOL003_DIR)
        tester.assert_has_directory(sol003_dir)
        sol003_scripts_dir = os.path.join(sol003_dir, BRENT_SOL003_SCRIPTS_DIR)
        tester.assert_has_directory(sol003_scripts_dir)
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_CREATE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_HEAL_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_INSTANTIATE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_OPERATE_VNF_REQUEST_START_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_OPERATE_VNF_REQUEST_STOP_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_SCALE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_TERMINATE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_VNF_INSTANCE_FILE))
        tester.assert_has_directory(PROJECT_CONTAINS_DIR)

        subprojectA_path = os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA')
        tester.assert_has_directory(subprojectA_path)
        tester.assert_has_directory(os.path.join(subprojectA_path, BRENT_DEFINITIONS_DIR))
        inf_dir = os.path.join(subprojectA_path, BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
        tester.assert_has_directory(inf_dir)
        tester.assert_has_file(os.path.join(inf_dir, 'example.yaml'), EXPECTED_OPENSTACK_EXAMPLE_TOSCA)
        lm_dir = os.path.join(subprojectA_path, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
        tester.assert_has_directory(lm_dir)
        descriptor_path = os.path.join(lm_dir, BRENT_DESCRIPTOR_YML_FILE)
        tester.assert_has_file(descriptor_path, EXPECTED_OS_AND_ANSIBLE_DESCRIPTOR.format('SubA'))
        tester.assert_has_directory(os.path.join(subprojectA_path, BRENT_LIFECYCLE_DIR))
        ansible_dir = os.path.join(subprojectA_path, BRENT_LIFECYCLE_DIR, BRENT_LIFECYCLE_ANSIBLE_DIR)
        tester.assert_has_directory(ansible_dir)
        ansible_scripts_dir = os.path.join(ansible_dir, BRENT_LIFECYCLE_ANSIBLE_SCRIPTS_DIR)
        tester.assert_has_directory(ansible_scripts_dir)
        tester.assert_has_file(os.path.join(ansible_scripts_dir, 'Install.yaml'), EXPECTED_ANSIBLE_INSTALL_SCRIPT)
        ansible_config_dir = os.path.join(ansible_dir, BRENT_LIFECYCLE_ANSIBLE_CONFIG_DIR)
        tester.assert_has_directory(ansible_config_dir)
        tester.assert_has_file(os.path.join(ansible_config_dir, BRENT_LIFECYCLE_ANSIBLE_INVENTORY_FILE), EXPECTED_ANSIBLE_INVENTORY)
        ansible_hostvars_dir = os.path.join(ansible_config_dir, BRENT_LIFECYCLE_ANSIBLE_CONFIG_HOSTVARS_DIR_NAME)
        tester.assert_has_directory(ansible_hostvars_dir)
        tester.assert_has_file(os.path.join(ansible_hostvars_dir, 'example-host.yml'), EXPECTED_ANSIBLE_HOST_VARS)

        subprojectB_path = os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB')
        tester.assert_has_directory(subprojectB_path)
        tester.assert_has_directory(os.path.join(subprojectB_path, BRENT_DEFINITIONS_DIR))
        inf_dir = os.path.join(subprojectB_path, BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
        tester.assert_has_directory(inf_dir)
        tester.assert_has_file(os.path.join(inf_dir, 'example.yaml'), EXPECTED_OPENSTACK_EXAMPLE_TOSCA)
        lm_dir = os.path.join(subprojectB_path, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
        tester.assert_has_directory(lm_dir)
        descriptor_path = os.path.join(lm_dir, BRENT_DESCRIPTOR_YML_FILE)
        tester.assert_has_file(descriptor_path, EXPECTED_OS_AND_SOL003_DESCRIPTOR.format('SubB'))
        tester.assert_has_directory(os.path.join(subprojectB_path, BRENT_LIFECYCLE_DIR))
        sol003_dir = os.path.join(subprojectB_path, BRENT_LIFECYCLE_DIR, BRENT_SOL003_DIR)
        tester.assert_has_directory(sol003_dir)
        sol003_scripts_dir = os.path.join(sol003_dir, BRENT_SOL003_SCRIPTS_DIR)
        tester.assert_has_directory(sol003_scripts_dir)
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_CREATE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_HEAL_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_INSTANTIATE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_OPERATE_VNF_REQUEST_START_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_OPERATE_VNF_REQUEST_STOP_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_SCALE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_TERMINATE_VNF_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol003_scripts_dir, BRENT_SOL003_VNF_INSTANCE_FILE))

    def test_create_sol005_with_subprojects(self):
        request = CreateResourceProjectRequest()
        request.name = 'Test'
        request.target_location = self.tmp_dir
        request.resource_manager = 'brent2.1'
        request.version = '9.9'
        request.params['lifecycle'] = 'sol005'
        subprojectA_request = ResourceSubprojectRequest()
        subprojectA_request.name = 'SubA'
        subprojectA_request.directory = 'SubprojectA'
        subprojectA_request.resource_manager = 'brent2.1'
        subprojectA_request.params['lifecycle'] = 'ansible'
        request.subproject_requests.append(subprojectA_request)
        subprojectB_request = ResourceSubprojectRequest()
        subprojectB_request.name = 'SubB'
        subprojectB_request.directory = 'SubprojectB'
        subprojectB_request.resource_manager = 'brent2.1'
        request.subproject_requests.append(subprojectB_request)
        creator = ProjectCreator(request, CreateOptions())
        creator.create()
        project = Project(self.tmp_dir)
        tester = self.assert_project(project)
        tester.assert_has_config({
            'schema':  '2.0',
            'name': 'Test',
            'version': '9.9',
            'type': 'Resource',
            'packaging': 'tgz',
            'resource-manager': 'brent2.1',
            'contains': [
                {
                    'name': 'SubA',
                    'directory': 'SubprojectA',
                    'type': 'Resource',
                    'resource-manager': 'brent2.1'
                },
                {
                    'name': 'SubB',
                    'directory':  'SubprojectB',
                    'type': 'Resource',
                    'resource-manager': 'brent2.1'
                }
            ]
        })
        tester.assert_has_directory(os.path.join(BRENT_DEFINITIONS_DIR))
        inf_dir = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
        tester.assert_has_directory(inf_dir)
        tester.assert_has_file(os.path.join(inf_dir, 'example.yaml'), EXPECTED_OPENSTACK_EXAMPLE_TOSCA)
        lm_dir = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
        tester.assert_has_directory(lm_dir)
        descriptor_path = os.path.join(lm_dir, BRENT_DESCRIPTOR_YML_FILE)
        tester.assert_has_directory(os.path.join(BRENT_LIFECYCLE_DIR))
        sol005_dir = os.path.join(BRENT_LIFECYCLE_DIR, BRENT_SOL005_DIR)
        tester.assert_has_directory(sol005_dir)
        sol005_scripts_dir = os.path.join(sol005_dir, BRENT_SOL005_SCRIPTS_DIR)
        tester.assert_has_directory(sol005_scripts_dir)
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_CREATE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_HEAL_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_INSTANTIATE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_UPDATE_NS_REQUEST_START_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_UPDATE_NS_REQUEST_STOP_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_SCALE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_TERMINATE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_NS_INSTANCE_FILE))
        tester.assert_has_directory(PROJECT_CONTAINS_DIR)

        subprojectA_path = os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA')
        tester.assert_has_directory(subprojectA_path)
        tester.assert_has_directory(os.path.join(subprojectA_path, BRENT_DEFINITIONS_DIR))
        inf_dir = os.path.join(subprojectA_path, BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
        tester.assert_has_directory(inf_dir)
        tester.assert_has_file(os.path.join(inf_dir, 'example.yaml'), EXPECTED_OPENSTACK_EXAMPLE_TOSCA)
        lm_dir = os.path.join(subprojectA_path, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
        tester.assert_has_directory(lm_dir)
        descriptor_path = os.path.join(lm_dir, BRENT_DESCRIPTOR_YML_FILE)
        tester.assert_has_file(descriptor_path, EXPECTED_OS_AND_ANSIBLE_DESCRIPTOR.format('SubA'))
        tester.assert_has_directory(os.path.join(subprojectA_path, BRENT_LIFECYCLE_DIR))
        ansible_dir = os.path.join(subprojectA_path, BRENT_LIFECYCLE_DIR, BRENT_LIFECYCLE_ANSIBLE_DIR)
        tester.assert_has_directory(ansible_dir)
        ansible_scripts_dir = os.path.join(ansible_dir, BRENT_LIFECYCLE_ANSIBLE_SCRIPTS_DIR)
        tester.assert_has_directory(ansible_scripts_dir)
        tester.assert_has_file(os.path.join(ansible_scripts_dir, 'Install.yaml'), EXPECTED_ANSIBLE_INSTALL_SCRIPT)
        ansible_config_dir = os.path.join(ansible_dir, BRENT_LIFECYCLE_ANSIBLE_CONFIG_DIR)
        tester.assert_has_directory(ansible_config_dir)
        tester.assert_has_file(os.path.join(ansible_config_dir, BRENT_LIFECYCLE_ANSIBLE_INVENTORY_FILE), EXPECTED_ANSIBLE_INVENTORY)
        ansible_hostvars_dir = os.path.join(ansible_config_dir, BRENT_LIFECYCLE_ANSIBLE_CONFIG_HOSTVARS_DIR_NAME)
        tester.assert_has_directory(ansible_hostvars_dir)
        tester.assert_has_file(os.path.join(ansible_hostvars_dir, 'example-host.yml'), EXPECTED_ANSIBLE_HOST_VARS)

        subprojectB_path = os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB')
        tester.assert_has_directory(subprojectB_path)
        tester.assert_has_directory(os.path.join(subprojectB_path, BRENT_DEFINITIONS_DIR))
        inf_dir = os.path.join(subprojectB_path, BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
        tester.assert_has_directory(inf_dir)
        tester.assert_has_file(os.path.join(inf_dir, 'example.yaml'), EXPECTED_OPENSTACK_EXAMPLE_TOSCA)
        lm_dir = os.path.join(subprojectB_path, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
        tester.assert_has_directory(lm_dir)
        descriptor_path = os.path.join(lm_dir, BRENT_DESCRIPTOR_YML_FILE)
        tester.assert_has_file(descriptor_path, EXPECTED_OS_AND_SOL005_DESCRIPTOR.format('SubB'))
        tester.assert_has_directory(os.path.join(subprojectB_path, BRENT_LIFECYCLE_DIR))
        sol005_dir = os.path.join(subprojectB_path, BRENT_LIFECYCLE_DIR, BRENT_SOL005_DIR)
        tester.assert_has_directory(sol005_dir)
        sol005_scripts_dir = os.path.join(sol005_dir, BRENT_SOL005_SCRIPTS_DIR)
        tester.assert_has_directory(sol005_scripts_dir)
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_CREATE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_HEAL_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_INSTANTIATE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_UPDATE_NS_REQUEST_START_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_UPDATE_NS_REQUEST_STOP_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_SCALE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_TERMINATE_NS_REQUEST_FILE))
        tester.assert_has_file_path(os.path.join(sol005_scripts_dir, BRENT_SOL005_NS_INSTANCE_FILE))