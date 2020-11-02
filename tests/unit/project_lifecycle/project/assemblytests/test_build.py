import unittest
import os
import tests.common.simulations.project_lab as project_lab
import lmctl.project.package.core as pkgs
from tests.common.project_testing import (ProjectSimTestCase, PROJECT_VNFCS_DIR, PROJECT_CONTAINS_DIR,
                                          ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE, ASSEMBLY_DESCRIPTOR_TEMPLATE_YML_FILE,
                                          ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, ASSEMBLY_RUNTIME_DIR, ASSEMBLY_TESTS_DIR,
                                          ARM_DESCRIPTOR_DIR)
from lmctl.project.source.core import Project, BuildResult, BuildOptions
from lmctl.project.handlers.assembly.assembly_src import TEMPLATE_CONTENT

BASIC_ASSEMBLY_DESCRIPTOR_YAML = """\
name: assembly::basic::1.0
description: basic_assembly
"""

WITH_BEHAVIOUR_DESCRIPTOR_YAML = """\
name: assembly::with_behaviour::1.0
description: with_behaviour
"""

WITH_BEHAVIOUR_SIMPLE_CONFIGURATION_JSON = """\
{
  "name": "simple",
  "description": "a simple assembly config",
  "properties": {
    "a": "123"
  },
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "descriptorName": "assembly::with_behaviour::1.0",
  "projectId": "assembly::with_behaviour::1.0"
}"""

WITH_BEHAVIOUR_RUNTIME_JSON = """\
{
  "name": "runtime",
  "projectId": "assembly::with_behaviour::1.0",
  "description": "a runtime scenario",
  "stages": [
    {
      "name": "Stage One",
      "steps": [
        {
          "stepDefinitionName": "Utilities::SleepForTime",
          "properties": {
            "sleepTime": "20",
            "timeUnit": "seconds"
          }
        }
      ]
    }
  ],
  "assemblyActors": [
    {
      "instanceName": "ExistingProvidedAssembly",
      "provided": true
    }
  ],
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z"
}"""

WITH_BEHAVIOUR_TEST_JSON = """\
{
  "name": "test",
  "description": "a test scenario",
  "stages": [
    {
      "name": "Stage One",
      "steps": [
        {
          "stepDefinitionName": "Utilities::SleepForTime",
          "properties": {
            "sleepTime": "20",
            "timeUnit": "seconds"
          }
        }
      ]
    }
  ],
  "assemblyActors": [
    {
      "instanceName": "simple",
      "assemblyConfigurationRef": "simple",
      "initialState": "Active",
      "uninstallOnExit": true,
      "provided": false
    }
  ],
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "projectId": "assembly::with_behaviour::1.0"
}"""


SUB_BASIC_ASSEMBLY_DESCRIPTOR_YAML = """\
name: assembly::sub_basic-contains_basic::1.0
description: descriptor
"""

SUB_WITH_BEHAVIOUR_DESCRIPTOR_YAML = """\
name: assembly::sub_with_behaviour-contains_with_behaviour::1.0
description: with_behaviour
"""

SUB_WITH_BEHAVIOUR_SIMPLE_CONFIGURATION_JSON = """\
{
  "name": "simple",
  "description": "a simple assembly config",
  "properties": {
    "a": "123"
  },
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "descriptorName": "assembly::sub_with_behaviour-contains_with_behaviour::1.0",
  "projectId": "assembly::sub_with_behaviour-contains_with_behaviour::1.0"
}"""

SUB_WITH_BEHAVIOUR_RUNTIME_JSON = """\
{
  "name": "runtime",
  "description": "a runtime scenario",
  "stages": [
    {
      "name": "Stage One",
      "steps": [
        {
          "stepDefinitionName": "Utilities::SleepForTime",
          "properties": {
            "sleepTime": "20",
            "timeUnit": "seconds"
          }
        }
      ]
    }
  ],
  "assemblyActors": [
    {
      "instanceName": "ExistingProvidedAssembly",
      "provided": true
    }
  ],
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "projectId": "assembly::sub_with_behaviour-contains_with_behaviour::1.0"
}"""

SUB_WITH_BEHAVIOUR_TEST_JSON = """\
{
  "name": "test",
  "description": "a test scenario",
  "stages": [
    {
      "name": "Stage One",
      "steps": [
        {
          "stepDefinitionName": "Utilities::SleepForTime",
          "properties": {
            "sleepTime": "20",
            "timeUnit": "seconds"
          }
        }
      ]
    }
  ],
  "assemblyActors": [
    {
      "instanceName": "simple",
      "assemblyConfigurationRef": "simple",
      "initialState": "Active",
      "uninstallOnExit": true,
      "provided": false
    }
  ],
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "projectId": "assembly::sub_with_behaviour-contains_with_behaviour::1.0"
}"""

WITH_TEMPLATE_ASSEMBLY_TEMPLATE_DESCRIPTOR_YAML = "name: assembly-template::with_template::1.0"
WITH_TEMPLATE_ASSEMBLY_TEMPLATE_DESCRIPTOR_YAML += "\n"
WITH_TEMPLATE_ASSEMBLY_TEMPLATE_DESCRIPTOR_YAML += TEMPLATE_CONTENT

WITH_TEMPLATE_ASSEMBLY_DESCRIPTOR_YAML = """\
name: assembly::with_template::1.0
description: descriptor for with_template
"""
class TestBuildAssemblyProjects(ProjectSimTestCase):

    def test_build(self):
        project_sim = self.simlab.simulate_assembly_basic()
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
            pkg_tester.assert_has_descriptor_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), BASIC_ASSEMBLY_DESCRIPTOR_YAML)
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'basic',
                'version': '1.0',
                'type': 'Assembly'
            })

    def test_build_with_template(self):
        project_sim = self.simlab.simulate_assembly_with_template()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        result = project.build(build_options)
        self.assertIsInstance(result, BuildResult)
        self.assertFalse(result.validation_result.has_warnings())
        pkg = result.pkg
        self.assertIsNotNone(pkg)
        self.assertIsInstance(pkg, pkgs.Pkg)
        package_base_name = os.path.basename(pkg.path)
        self.assertEqual(package_base_name, 'with_template-1.0.tgz')
        with self.assert_package(pkg) as pkg_tester:
            pkg_tester.assert_has_descriptor_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), WITH_TEMPLATE_ASSEMBLY_DESCRIPTOR_YAML)
            pkg_tester.assert_has_descriptor_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_TEMPLATE_YML_FILE), WITH_TEMPLATE_ASSEMBLY_TEMPLATE_DESCRIPTOR_YAML)
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'with_template',
                'version': '1.0',
                'type': 'Assembly'
            })

    def test_build_behaviour(self):
        project_sim = self.simlab.simulate_assembly_with_behaviour()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        result = project.build(build_options)
        self.assertFalse(result.validation_result.has_warnings())
        pkg = result.pkg
        with self.assert_package(pkg) as pkg_tester:
            pkg_tester.assert_has_descriptor_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), WITH_BEHAVIOUR_DESCRIPTOR_YAML)
            pkg_tester.assert_has_directory(ASSEMBLY_BEHAVIOUR_DIR)
            pkg_tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR))
            pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple.json'), WITH_BEHAVIOUR_SIMPLE_CONFIGURATION_JSON)
            pkg_tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR))
            pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime.json'), WITH_BEHAVIOUR_RUNTIME_JSON)
            pkg_tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR))
            pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test.json'), WITH_BEHAVIOUR_TEST_JSON)
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'with_behaviour',
                'version': '1.0',
                'type': 'Assembly'
            })


class TestBuildAssemblySubprojects(ProjectSimTestCase):

    def test_build(self):
        project_sim = self.simlab.simulate_assembly_contains_assembly_basic()
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
            pkg_tester.assert_has_descriptor_file(os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ASSEMBLY_BASIC,
                                                               ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), SUB_BASIC_ASSEMBLY_DESCRIPTOR_YAML)
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'contains_basic',
                'version': '1.0',
                'type': 'Assembly',
                'contains': [
                    {
                        'name': 'sub_basic',
                        'type': 'Assembly',
                        'directory': 'sub_basic'
                    }
                ]
            })

    def test_build_behaviour(self):
        project_sim = self.simlab.simulate_assembly_contains_assembly_with_behaviour()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        result = project.build(build_options)
        self.assertFalse(result.validation_result.has_warnings())
        pkg = result.pkg
        with self.assert_package(pkg) as pkg_tester:
            pkg_tester.assert_has_descriptor_file(os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ASSEMBLY_WITH_BEHAVIOUR,
                                                               ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), SUB_WITH_BEHAVIOUR_DESCRIPTOR_YAML)
            pkg_tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ASSEMBLY_WITH_BEHAVIOUR, ASSEMBLY_BEHAVIOUR_DIR))
            pkg_tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ASSEMBLY_WITH_BEHAVIOUR, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR))
            pkg_tester.assert_has_file(os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ASSEMBLY_WITH_BEHAVIOUR, ASSEMBLY_BEHAVIOUR_DIR,
                                                    ASSEMBLY_CONFIGURATIONS_DIR, 'simple.json'), SUB_WITH_BEHAVIOUR_SIMPLE_CONFIGURATION_JSON)
            pkg_tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ASSEMBLY_WITH_BEHAVIOUR, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR))
            pkg_tester.assert_has_file(os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ASSEMBLY_WITH_BEHAVIOUR,
                                                    ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime.json'), SUB_WITH_BEHAVIOUR_RUNTIME_JSON)
            pkg_tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ASSEMBLY_WITH_BEHAVIOUR, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR))
            pkg_tester.assert_has_file(os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ASSEMBLY_WITH_BEHAVIOUR,
                                                    ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test.json'), SUB_WITH_BEHAVIOUR_TEST_JSON)
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'contains_with_behaviour',
                'version': '1.0',
                'type': 'Assembly',
                'contains': [
                    {
                        'name': 'sub_with_behaviour',
                        'type': 'Assembly',
                        'directory': 'sub_with_behaviour'
                    }
                ]
            })

VNFC_A_DESCRIPTOR_YAML = """\
name: resource::vnfcA-old_style::1.0
description: descriptor for basic
"""

VNFC_B_DESCRIPTOR_YAML = """\
name: resource::vnfcB-old_style::1.0
description: descriptor for basic
"""

class TestBuildOldStyle(ProjectSimTestCase):

  def test_vnfcs(self):
    project_sim = self.simlab.simulate_assembly_old_style()
    project = Project(project_sim.path)
    build_options = BuildOptions()
    result = project.build(build_options)
    self.assertTrue(os.path.exists(os.path.join(project_sim.path, PROJECT_VNFCS_DIR)))
    self.assertTrue(os.path.exists(os.path.join(project_sim.path, PROJECT_VNFCS_DIR, 'vnfcA')))
    self.assertTrue(os.path.exists(os.path.join(project_sim.path, PROJECT_VNFCS_DIR, 'vnfcB')))
    pkg = result.pkg
    self.assertIsNotNone(pkg)
    self.assertIsInstance(pkg, pkgs.Pkg)
    package_base_name = os.path.basename(pkg.path)
    self.assertEqual(package_base_name, 'old_style-1.0.tgz')
    with self.assert_package(pkg) as pkg_tester:
        pkg_tester.assert_has_descriptor_file(os.path.join(PROJECT_CONTAINS_DIR, 'vnfcA',
                                                            'vnfcA-old_style.yml'), VNFC_A_DESCRIPTOR_YAML)
        pkg_tester.assert_has_descriptor_file(os.path.join(PROJECT_CONTAINS_DIR, 'vnfcB',
                                                            'vnfcB-old_style.yml'), VNFC_B_DESCRIPTOR_YAML)
        pkg_tester.assert_has_meta({
            'schema': '2.0',
            'name': 'old_style',
            'version': '1.0',
            'type': 'Assembly',
            'contains': [
                {
                    'name': 'vnfcA',
                    'type': 'Resource',
                    'directory': 'vnfcA',
                    'resource-manager': 'ansible-rm'
                },
                {
                    'name': 'vnfcB',
                    'type': 'Resource',
                    'directory': 'vnfcB',
                    'resource-manager': 'ansible-rm'
                }
            ]
        })

WITH_REFERENCE_ROOT_DESCRIPTOR_YAML = """\
name: assembly::with_descriptor_references::1.0
description: with references
composition:
  subA:
    type: assembly::subA-with_descriptor_references::1.0
references:
  subB:
    type: resource::subB-with_descriptor_references::1.0
"""

WITH_REFERENCE_SUBA_DESCRIPTOR_YAML = """\
name: assembly::subA-with_descriptor_references::1.0
description: subA
composition:
  subAA:
    type: assembly::subAA-subA-with_descriptor_references::1.0
"""

WITH_REFERENCE_SUBAA_DESCRIPTOR_YAML = """\
name: assembly::subAA-subA-with_descriptor_references::1.0
description: subAA
composition:
  subZ:
    type: $lmctl:/contains:/subZ:/descriptor_name
"""

WITH_REFERENCE_SUBAB_DESCRIPTOR_YAML = """\
name: assembly::subAB-subA-with_descriptor_references::1.0
description: subAB
composition:
  subB:
    type: resource::subB-with_descriptor_references::1.0
  another:
    type: resource::another::1.0
"""

WITH_REFERENCE_SUBB_DESCRIPTOR_YAML = """\
name: resource::subB-with_descriptor_references::1.0
description: subB
references:
  subA:
    type: assembly::subA-with_descriptor_references::1.0
"""

WITH_BEH_REFERENCE_ROOT_CONFIGURATION_ROOT = """\
{
  "name": "root",
  "projectId": "assembly::with_behaviour_references::1.0",
  "description": "assembly config for root project",
  "properties": {
    "a": "123"
  },
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "descriptorName": "assembly::with_behaviour_references::1.0"
}"""

WITH_BEH_REFERENCE_ROOT_CONFIGURATION_SUBA = """\
{
  "name": "subA",
  "projectId": "assembly::with_behaviour_references::1.0",
  "description": "assembly config for subA project",
  "properties": {
    "a": "123"
  },
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "descriptorName": "assembly::subA-with_behaviour_references::1.0"
}"""

WITH_BEH_REFERENCE_ROOT_CONFIGURATION_SUBAA = """\
{
  "name": "subAA",
  "projectId": "assembly::with_behaviour_references::1.0",
  "description": "assembly config for subAA project",
  "properties": {
    "a": "123"
  },
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "descriptorName": "assembly::subAA-subA-with_behaviour_references::1.0"
}"""

WITH_BEH_REFERENCE_ROOT_RUNTIME = """\
{
  "name": "runtime",
  "projectId": "assembly::with_behaviour_references::1.0",
  "description": "a runtime scenario",
  "stages": [
    {
      "name": "Stage One",
      "steps": [
        {
          "stepDefinitionName": "Utilities::SleepForTime",
          "properties": {
            "sleepTime": "20",
            "timeUnit": "seconds"
          }
        }
      ]
    }
  ],
  "assemblyActors": [
    {
      "instanceName": "ExistingProvidedAssembly",
      "provided": true
    }
  ],
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z"
}"""

WITH_BEH_REFERENCE_ROOT_TEST = """\
{
  "name": "test",
  "projectId": "assembly::with_behaviour_references::1.0",
  "description": "a test scenario",
  "stages": [
    {
      "name": "Stage One",
      "steps": [
        {
          "stepDefinitionName": "Utilities::SleepForTime",
          "properties": {
            "sleepTime": "20",
            "timeUnit": "seconds"
          }
        }
      ]
    }
  ],
  "assemblyActors": [
    {
      "instanceName": "root",
      "assemblyConfigurationRef": "root",
      "initialState": "Active",
      "uninstallOnExit": true,
      "provided": false
    }
  ],
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z"
}"""

WITH_BEH_REFERENCE_SUBA_CONFIGURATION_ROOT = """\
{
  "name": "root",
  "projectId": "assembly::subA-with_behaviour_references::1.0",
  "description": "assembly config for root project",
  "properties": {
    "a": "123"
  },
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "descriptorName": "assembly::with_behaviour_references::1.0"
}"""

WITH_BEH_REFERENCE_SUBA_CONFIGURATION_SUBAB = """\
{
  "name": "subAB",
  "projectId": "assembly::subA-with_behaviour_references::1.0",
  "description": "assembly config for subAB project",
  "properties": {
    "a": "123"
  },
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "descriptorName": "assembly::subAB-subA-with_behaviour_references::1.0"
}"""

WITH_BEH_REFERENCE_SUBA_CONFIGURATION_SUBB = """\
{
  "name": "subB",
  "projectId": "assembly::subA-with_behaviour_references::1.0",
  "description": "assembly config for subB project",
  "properties": {
    "a": "123"
  },
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "descriptorName": "assembly::subB-with_behaviour_references::1.0"
}"""

WITH_BEH_REFERENCE_SUAB_CONFIGURATION_SUBB = """\
{
  "name": "subB",
  "projectId": "assembly::subAB-subA-with_behaviour_references::1.0",
  "description": "assembly config for subB project",
  "properties": {
    "a": "123"
  },
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "descriptorName": "assembly::subB-with_behaviour_references::1.0"
}"""

UNRESOLVABLE_DESCRIPTOR = """\
name: assembly::with_unresolvable_references::1.0
description: with references
composition:
  subZ:
    type: $lmctl:/contains:/subZ:/descriptor_name
references:
  subY:
    type: $lmctl:/contains:/subY:/descriptor_name
"""

UNRESOLVABLE_CONFIGURATION_BAD_PATH = """\
{
  "name": "bad_path",
  "projectId": "assembly::with_unresolvable_references::1.0",
  "description": "assembly config with a reference that leads to a bad path",
  "properties": {
    "a": "123"
  },
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "descriptorName": "$lmctl:/descriptor_name:/contains:/subB"
}"""

UNRESOLVABLE_CONFIGURATION_NOT_FOUND = """\
{
  "name": "not_found",
  "projectId": "assembly::with_unresolvable_references::1.0",
  "description": "assembly config with a reference that cannot be resolved",
  "properties": {
    "a": "123"
  },
  "createdAt": "2019-01-01T01:00:00.613Z",
  "lastModifiedAt": "2019-01-02T01:00:00.613Z",
  "descriptorName": "$lmctl:/contains:/subZ:/descriptor_name"
}"""

class TestBuildReferences(ProjectSimTestCase):

  def test_descriptor_references(self):
    project_sim = self.simlab.simulate_assembly_with_descriptor_references()
    project = Project(project_sim.path)
    build_options = BuildOptions()
    result = project.build(build_options)
    pkg = result.pkg
    self.assertIsNotNone(pkg)
    self.assertIsInstance(pkg, pkgs.Pkg)
    package_base_name = os.path.basename(pkg.path)
    self.assertEqual(package_base_name, 'with_descriptor_references-1.0.tgz')
    with self.assert_package(pkg) as pkg_tester:
        pkg_tester.assert_has_descriptor_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), WITH_REFERENCE_ROOT_DESCRIPTOR_YAML)
        subA_path = os.path.join(PROJECT_CONTAINS_DIR, 'subA')
        pkg_tester.assert_has_descriptor_file(os.path.join(subA_path, ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), WITH_REFERENCE_SUBA_DESCRIPTOR_YAML)
        pkg_tester.assert_has_descriptor_file(os.path.join(subA_path, PROJECT_CONTAINS_DIR, 'subAA', ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), WITH_REFERENCE_SUBAA_DESCRIPTOR_YAML)
        pkg_tester.assert_has_descriptor_file(os.path.join(subA_path, PROJECT_CONTAINS_DIR, 'subAB', ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), WITH_REFERENCE_SUBAB_DESCRIPTOR_YAML)
        pkg_tester.assert_has_descriptor_file(os.path.join(PROJECT_CONTAINS_DIR, 'subB', 'subB-with_descriptor_references.yml'), WITH_REFERENCE_SUBB_DESCRIPTOR_YAML)

  def test_behaviour_references(self):
    project_sim = self.simlab.simulate_assembly_with_behaviour_references()
    project = Project(project_sim.path)
    build_options = BuildOptions()
    result = project.build(build_options)
    pkg = result.pkg
    self.assertIsNotNone(pkg)
    self.assertIsInstance(pkg, pkgs.Pkg)
    package_base_name = os.path.basename(pkg.path)
    self.assertEqual(package_base_name, 'with_behaviour_references-1.0.tgz')
    with self.assert_package(pkg) as pkg_tester:
      pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'root.json'), WITH_BEH_REFERENCE_ROOT_CONFIGURATION_ROOT)
      pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'subA.json'), WITH_BEH_REFERENCE_ROOT_CONFIGURATION_SUBA)
      pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'subAA.json'), WITH_BEH_REFERENCE_ROOT_CONFIGURATION_SUBAA)
      pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime.json'), WITH_BEH_REFERENCE_ROOT_RUNTIME)
      pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test.json'), WITH_BEH_REFERENCE_ROOT_TEST)
      subA_path = os.path.join(PROJECT_CONTAINS_DIR, 'subA')
      pkg_tester.assert_has_file(os.path.join(subA_path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'root.json'), WITH_BEH_REFERENCE_SUBA_CONFIGURATION_ROOT)
      pkg_tester.assert_has_file(os.path.join(subA_path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'subAB.json'), WITH_BEH_REFERENCE_SUBA_CONFIGURATION_SUBAB)
      pkg_tester.assert_has_file(os.path.join(subA_path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'subB.json'), WITH_BEH_REFERENCE_SUBA_CONFIGURATION_SUBB)
      subAB_path = os.path.join(subA_path, PROJECT_CONTAINS_DIR, 'subAB')
      pkg_tester.assert_has_file(os.path.join(subAB_path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'subB.json'), WITH_BEH_REFERENCE_SUAB_CONFIGURATION_SUBB)
      
  def test_unresolvable_references(self):
    project_sim = self.simlab.simulate_assembly_with_unresolvable_references()
    project = Project(project_sim.path)
    build_options = BuildOptions()
    result = project.build(build_options)
    pkg = result.pkg
    self.assertIsNotNone(pkg)
    self.assertIsInstance(pkg, pkgs.Pkg)
    package_base_name = os.path.basename(pkg.path)
    self.assertEqual(package_base_name, 'with_unresolvable_references-1.0.tgz')
    with self.assert_package(pkg) as pkg_tester:
      pkg_tester.assert_has_descriptor_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), UNRESOLVABLE_DESCRIPTOR)
      pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'bad_path.json'), UNRESOLVABLE_CONFIGURATION_BAD_PATH)
      pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'not_found.json'), UNRESOLVABLE_CONFIGURATION_NOT_FOUND)
      