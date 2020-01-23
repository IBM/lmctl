import os
from tests.common.project_testing import (ProjectSimTestCase,
                                          PROJECT_CONTAINS_DIR, BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR, BRENT_DESCRIPTOR_DIR,
                                          BRENT_LIFECYCLE_DIR, BRENT_DESCRIPTOR_YML_FILE, 
                                          BRENT_LIFECYCLE_ANSIBLE_DIR, BRENT_LIFECYCLE_ANSIBLE_SCRIPTS_DIR,
                                          BRENT_LIFECYCLE_ANSIBLE_CONFIG_DIR)
from lmctl.project.source.core import Project, BuildResult, Options, BuildOptions
from lmctl.project.validation import ValidationResult
import tests.common.simulations.project_lab as project_lab
import lmctl.project.package.core as pkgs

BASIC_DESCRIPTOR_YAML = """\
name: resource::basic::1.0
description: descriptor
infrastructure:
  Openstack:
    template:
      file: example.yaml
default_driver:
  ansible:
    infrastructure_type:
    - '*'
"""

SUB_BASIC_DESCRIPTOR_YAML = """\
name: resource::sub_basic-contains_basic::1.0
description: descriptor
infrastructure:
  Openstack:
    template:
      file: example.yaml
default_driver:
  ansible:
    infrastructure_type:
    - '*'
"""

BASIC_INFRASTRUCTURE_TOSCA = """\
tosca_definitions_version: tosca_simple_yaml_1_0

description: Basic example 
topology_template: {}
"""

BASIC_INSTALL_PLAYBOOK = """\
---
- name: Install
  hosts: all
  gather_facts: False"""

BASIC_INVENTORY = """\
[example]
example-host"""

BASIC_EXAMPLE_HOST_YAML = """\
---
ansible_host: {{ dl_properties.host }}
ansible_ssh_user: {{ dl_properties.ssh_user }}
ansible_ssh_pass: {{ dl_properties.ssh_pass }}"""

class TestBuildBrentProjects(ProjectSimTestCase):

    def test_build(self):
        project_sim = self.simlab.simulate_brent_basic()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        result = project.build(build_options)
        self.assertIsInstance(result, BuildResult)
        self.assertFalse(result.validation_result.has_warnings())
        pkg = result.pkg
        self.assertIsNotNone(pkg)
        self.assertIsInstance(pkg, pkgs.Pkg)
        package_base_name = os.path.basename(pkg.path)
        self.assertEqual(package_base_name, 'basic-1.0.tgz')
        with self.assert_package(pkg) as pkg_tester:
            pkg_tester.assert_has_file_path('basic.zip')
            pkg_tester.assert_has_file(BRENT_DESCRIPTOR_YML_FILE, BASIC_DESCRIPTOR_YAML)
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'basic',
                'version': '1.0',
                'type': 'Resource',
                'resource-manager': 'brent'
            })
            with self.assert_zip(pkg_tester.get_file_path('basic.zip')) as zip_tester:
                zip_tester.assert_has_directory(BRENT_DEFINITIONS_DIR)
                inf_path = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
                zip_tester.assert_has_directory(inf_path)
                zip_tester.assert_has_file(os.path.join(inf_path, 'example.yaml'), BASIC_INFRASTRUCTURE_TOSCA)
                lm_path = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
                zip_tester.assert_has_file(os.path.join(lm_path, BRENT_DESCRIPTOR_YML_FILE), BASIC_DESCRIPTOR_YAML)
                zip_tester.assert_has_directory(BRENT_LIFECYCLE_DIR)
                ansible_dir = os.path.join(BRENT_LIFECYCLE_DIR, BRENT_LIFECYCLE_ANSIBLE_DIR)
                zip_tester.assert_has_directory(ansible_dir)
                ansible_scripts_dir = os.path.join(ansible_dir, BRENT_LIFECYCLE_ANSIBLE_SCRIPTS_DIR)
                zip_tester.assert_has_directory(ansible_scripts_dir)
                zip_tester.assert_has_file(os.path.join(ansible_scripts_dir, 'Install.yaml'), BASIC_INSTALL_PLAYBOOK)
                ansible_config_dir = os.path.join(ansible_dir, BRENT_LIFECYCLE_ANSIBLE_CONFIG_DIR)
                zip_tester.assert_has_directory(ansible_config_dir)
                zip_tester.assert_has_file(os.path.join(ansible_config_dir, 'inventory'), BASIC_INVENTORY)
                zip_tester.assert_has_file(os.path.join(ansible_config_dir, 'host_vars', 'example-host.yml'), BASIC_EXAMPLE_HOST_YAML)
    
    def test_build_empty_infrastructure(self):
        project_sim = self.simlab.simulate_brent_with_empty_infrastructure()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        result = project.build(build_options)
        self.assertIsInstance(result, BuildResult)
        self.assertFalse(result.validation_result.has_warnings())
        pkg = result.pkg
        self.assertIsNotNone(pkg)
        self.assertIsInstance(pkg, pkgs.Pkg)
        package_base_name = os.path.basename(pkg.path)
        self.assertEqual(package_base_name, 'with-empty-infrastructure-1.0.tgz')
        with self.assert_package(pkg) as pkg_tester:
            pkg_tester.assert_has_file_path('with-empty-infrastructure.zip')
            with self.assert_zip(pkg_tester.get_file_path('with-empty-infrastructure.zip')) as zip_tester:
                zip_tester.assert_has_directory(BRENT_DEFINITIONS_DIR)
                inf_path = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
                zip_tester.assert_has_directory(inf_path)
                zip_tester.assert_has_no_file(os.path.join(inf_path, '.gitkeep'))


class TestBuildBrentSubprojects(ProjectSimTestCase):

    def test_build(self):
        project_sim = self.simlab.simulate_assembly_contains_brent_basic()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        result = project.build(build_options)
        self.assertIsInstance(result, BuildResult)
        self.assertFalse(result.validation_result.has_warnings())
        pkg = result.pkg
        self.assertIsNotNone(pkg)
        self.assertIsInstance(pkg, pkgs.Pkg)
        package_base_name = os.path.basename(pkg.path)
        self.assertEqual(package_base_name, 'contains_basic-1.0.tgz')
        sub_brent_basic_path = os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_BRENT_BASIC)
        with self.assert_package(pkg) as pkg_tester:
            pkg_tester.assert_has_file_path(os.path.join(sub_brent_basic_path, 'sub_basic-contains_basic.zip'))
            pkg_tester.assert_has_file(os.path.join(sub_brent_basic_path, BRENT_DESCRIPTOR_YML_FILE), SUB_BASIC_DESCRIPTOR_YAML)
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'contains_basic',
                'version': '1.0',
                'type': 'Assembly',
                'contains': [
                    {
                        'name': 'sub_basic',
                        'type': 'Resource',
                        'resource-manager': 'brent',
                        'directory': 'sub_basic'
                    }
                ]
            })
            with self.assert_zip(pkg_tester.get_file_path(os.path.join(sub_brent_basic_path, 'sub_basic-contains_basic.zip'))) as zip_tester:
                zip_tester.assert_has_directory(BRENT_DEFINITIONS_DIR)
                inf_path = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
                zip_tester.assert_has_directory(inf_path)
                zip_tester.assert_has_file(os.path.join(inf_path, 'example.yaml'), BASIC_INFRASTRUCTURE_TOSCA)
                lm_path = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
                zip_tester.assert_has_file(os.path.join(lm_path, BRENT_DESCRIPTOR_YML_FILE), SUB_BASIC_DESCRIPTOR_YAML)
                zip_tester.assert_has_directory(BRENT_LIFECYCLE_DIR)
                ansible_dir = os.path.join(BRENT_LIFECYCLE_DIR, BRENT_LIFECYCLE_ANSIBLE_DIR)
                zip_tester.assert_has_directory(ansible_dir)
                ansible_scripts_dir = os.path.join(ansible_dir, BRENT_LIFECYCLE_ANSIBLE_SCRIPTS_DIR)
                zip_tester.assert_has_directory(ansible_scripts_dir)
                zip_tester.assert_has_file(os.path.join(ansible_scripts_dir, 'Install.yaml'), BASIC_INSTALL_PLAYBOOK)
                ansible_config_dir = os.path.join(ansible_dir, BRENT_LIFECYCLE_ANSIBLE_CONFIG_DIR)
                zip_tester.assert_has_directory(ansible_config_dir)
                zip_tester.assert_has_file(os.path.join(ansible_config_dir, 'inventory'), BASIC_INVENTORY)
                zip_tester.assert_has_file(os.path.join(ansible_config_dir, 'host_vars', 'example-host.yml'), BASIC_EXAMPLE_HOST_YAML)
