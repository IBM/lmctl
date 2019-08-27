import os
from tests.common.project_testing import (ProjectSimTestCase,
                                          PROJECT_CONTAINS_DIR,
                                          ARM_DESCRIPTOR_DIR, ARM_LIFECYCLE_DIR, ARM_METAINF_DIR, ARM_MANIFEST_FILE)
from lmctl.project.source.core import Project, BuildResult, Options, BuildOptions
from lmctl.project.validation import ValidationResult
import tests.common.simulations.project_lab as project_lab
import lmctl.project.package.core as pkgs

BASIC_ARM_DESCRIPTOR_YAML = """\
name: resource::basic::1.0
description: descriptor for basic
"""

BASIC_ARM_INSTALL_PLAYBOOK = """\
---
- name: Install
  hosts: all
  gather_facts: False"""

BASIC_ARM_MANIFEST = """\
name: basic
version: 1.0
resource-manager: ansible
"""

SUB_BASIC_ARM_DESCRIPTOR_YAML = """\
name: resource::sub_basic-contains_basic::1.0
description: descriptor for basic
"""

SUB_BASIC_ARM_MANIFEST = """\
name: sub_basic-contains_basic
version: 1.0
resource-manager: ansible
"""


class TestBuildAnsibleRmProjects(ProjectSimTestCase):

    def test_build(self):
        project_sim = self.simlab.simulate_arm_basic()
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
            pkg_tester.assert_has_file_path('basic.csar')
            pkg_tester.assert_has_file('basic.yml', BASIC_ARM_DESCRIPTOR_YAML)
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'basic',
                'version': '1.0',
                'type': 'Resource',
                'resource-manager': 'ansiblerm'
            })
            with self.assert_zip(pkg_tester.get_file_path('basic.csar')) as zip_tester:
                zip_tester.assert_has_directory(ARM_DESCRIPTOR_DIR)
                zip_tester.assert_has_file(os.path.join(ARM_DESCRIPTOR_DIR, 'basic.yml'), BASIC_ARM_DESCRIPTOR_YAML)
                zip_tester.assert_has_directory(ARM_LIFECYCLE_DIR)
                zip_tester.assert_has_file(os.path.join(ARM_LIFECYCLE_DIR, 'Install.yml'), BASIC_ARM_INSTALL_PLAYBOOK)
                zip_tester.assert_has_directory(ARM_METAINF_DIR)
                zip_tester.assert_has_file(os.path.join(ARM_METAINF_DIR, ARM_MANIFEST_FILE), BASIC_ARM_MANIFEST)


class TestBuildAnsibleRmSubprojects(ProjectSimTestCase):

    def test_build(self):
        project_sim = self.simlab.simulate_assembly_contains_arm_basic()
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
        with self.assert_package(pkg) as pkg_tester:
            csar_relative_path = os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ARM_BASIC, 'sub_basic-contains_basic.csar')
            pkg_tester.assert_has_file_path(csar_relative_path)
            pkg_tester.assert_has_file(os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ARM_BASIC, 'sub_basic-contains_basic.yml'), SUB_BASIC_ARM_DESCRIPTOR_YAML)
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'contains_basic',
                'version': '1.0',
                'type': 'Assembly',
                'contains': [
                    {
                        'name': 'sub_basic',
                        'type': 'Resource',
                        'directory': 'sub_basic',
                        'resource-manager': 'ansiblerm'
                    }
                ]
            })
            with self.assert_zip(pkg_tester.get_file_path(csar_relative_path)) as zip_tester:
                zip_tester.assert_has_directory(ARM_DESCRIPTOR_DIR)
                zip_tester.assert_has_file(os.path.join(ARM_DESCRIPTOR_DIR, 'sub_basic-contains_basic.yml'), SUB_BASIC_ARM_DESCRIPTOR_YAML)
                zip_tester.assert_has_directory(ARM_LIFECYCLE_DIR)
                zip_tester.assert_has_file(os.path.join(ARM_LIFECYCLE_DIR, 'Install.yml'), BASIC_ARM_INSTALL_PLAYBOOK)
                zip_tester.assert_has_directory(ARM_METAINF_DIR)
                zip_tester.assert_has_file(os.path.join(ARM_METAINF_DIR, ARM_MANIFEST_FILE), SUB_BASIC_ARM_MANIFEST)
