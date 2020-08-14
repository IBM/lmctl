import unittest
import os
import tests.common.simulations.project_lab as project_lab
import lmctl.project.package.core as pkgs
from tests.common.project_testing import (ProjectSimTestCase, PROJECT_VNFCS_DIR, PROJECT_CONTAINS_DIR,
                                          TYPE_DESCRIPTOR_DIR, TYPE_DESCRIPTOR_YML_FILE,
                                          ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, ASSEMBLY_RUNTIME_DIR, ASSEMBLY_TESTS_DIR,
                                          ARM_DESCRIPTOR_DIR)
from lmctl.project.source.core import Project, BuildResult, BuildOptions

BASIC_TYPE_DESCRIPTOR_YAML = """\
name: type::basic::1.0
description: descriptor for basic
"""

WITH_BEHAVIOUR_DESCRIPTOR_YAML = """\
name: type::with_behaviour::1.0
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
  "descriptorName": "type::with_behaviour::1.0",
  "projectId": "type::with_behaviour::1.0"
}"""

WITH_BEHAVIOUR_RUNTIME_JSON = """\
{
  "name": "runtime",
  "projectId": "type::with_behaviour::1.0",
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
  "projectId": "type::with_behaviour::1.0"
}"""

class TestBuildTypeProjects(ProjectSimTestCase):

    def test_build(self):
        project_sim = self.simlab.simulate_type_basic()
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
            pkg_tester.assert_has_descriptor_file(os.path.join(TYPE_DESCRIPTOR_DIR, TYPE_DESCRIPTOR_YML_FILE), BASIC_TYPE_DESCRIPTOR_YAML)
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'basic',
                'version': '1.0',
                'type': 'Type'
            })

    def test_build_behaviour(self):
        project_sim = self.simlab.simulate_type_with_behaviour()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        result = project.build(build_options)
        self.assertFalse(result.validation_result.has_warnings())
        pkg = result.pkg
        with self.assert_package(pkg) as pkg_tester:
            pkg_tester.assert_has_descriptor_file(os.path.join(TYPE_DESCRIPTOR_DIR, TYPE_DESCRIPTOR_YML_FILE), WITH_BEHAVIOUR_DESCRIPTOR_YAML)
            pkg_tester.assert_has_directory(ASSEMBLY_BEHAVIOUR_DIR)
            pkg_tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR))
            pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple.json'), WITH_BEHAVIOUR_SIMPLE_CONFIGURATION_JSON)
            pkg_tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR))
            pkg_tester.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test.json'), WITH_BEHAVIOUR_TEST_JSON)
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'with_behaviour',
                'version': '1.0',
                'type': 'Type'
            })
