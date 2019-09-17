import unittest
import os
import tests.common.simulations.project_lab as project_lab
from tests.common.project_testing import (ProjectSimTestCase, 
                                            ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE, 
                                            ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 
                                            ASSEMBLY_RUNTIME_DIR, ASSEMBLY_TESTS_DIR)
from lmctl.project.source.core import Project, PullOptions
from lmctl.project.sessions import EnvironmentSessions

DESCRIPTOR_WITH_UNRESOLVABLE_COMPONENT = """\
description: includes an component not part of this project
composition:
  other:
    type: resource::other_descriptor::1.0
"""

PULLED_SIMPLE_ASSEMBLY_CONFIGURATION = """\
{
  "projectId": "$lmctl:/descriptor_name",
  "name": "simple",
  "descriptorName": "$lmctl:/descriptor_name"
}"""

PULLED_SIMPLE_2_ASSEMBLY_CONFIGURATION = """\
{
  "projectId": "$lmctl:/descriptor_name",
  "name": "simple-2",
  "descriptorName": "$lmctl:/descriptor_name"
}"""

PULLED_SIMPLE_ASSEMBLY_CONFIGURATION_WITH_UNRESOLVABLE_DESCRIPTOR = """\
{
  "projectId": "$lmctl:/descriptor_name",
  "name": "simple",
  "descriptorName": "assembly::another_descriptor::1.0"
}"""

PULLED_RUNTIME_SCENARIO = """\
{
  "projectId": "$lmctl:/descriptor_name",
  "name": "runtime",
  "assemblyActors": [
    {
      "instanceName": "ExistingProvidedAssembly",
      "provided": true
    }
  ]
}"""

PULLED_RUNTIME_2_SCENARIO = """\
{
  "projectId": "$lmctl:/descriptor_name",
  "name": "runtime-2",
  "assemblyActors": [
    {
      "instanceName": "ExistingProvidedAssembly",
      "provided": true
    }
  ]
}"""

PULLED_RUNTIME_SCENARIO_ACTORS_REPLACED = """\
{
  "projectId": "$lmctl:/descriptor_name",
  "name": "runtime",
  "assemblyActors": [
    {
      "instanceName": "ExistingProvidedAssembly",
      "provided": true
    },
    {
      "instanceName": "simple",
      "initialState": "Active",
      "uninstallOnExit": true,
      "provided": false,
      "assemblyConfigurationRef": "simple"
    },
    {
      "instanceName": "another",
      "initialState": "Active",
      "uninstallOnExit": true,
      "provided": false,
      "assemblyConfigurationRef": "a123"
    }
  ]
}"""

PULLED_TEST_SCENARIO = """\
{
  "projectId": "$lmctl:/descriptor_name",
  "name": "test",
  "assemblyActors": [
    {
      "instanceName": "simple",
      "initialState": "Active",
      "uninstallOnExit": true,
      "provided": false,
      "assemblyConfigurationRef": "s123"
    }
  ]
}"""

PULLED_TEST_2_SCENARIO = """\
{
  "projectId": "$lmctl:/descriptor_name",
  "name": "test-2",
  "assemblyActors": [
    {
      "instanceName": "simple",
      "initialState": "Active",
      "uninstallOnExit": true,
      "provided": false,
      "assemblyConfigurationRef": "s123"
    }
  ]
}"""

PULLED_TEST_SCENARIO_ACTORS_REPLACED = """\
{
  "projectId": "$lmctl:/descriptor_name",
  "name": "test",
  "assemblyActors": [
    {
      "instanceName": "simple",
      "initialState": "Active",
      "uninstallOnExit": true,
      "provided": false,
      "assemblyConfigurationRef": "simple"
    },
    {
      "instanceName": "another",
      "initialState": "Active",
      "uninstallOnExit": true,
      "provided": false,
      "assemblyConfigurationRef": "a123"
    }
  ]
}"""

class TestPullAssemblyProjects(ProjectSimTestCase):

    def __exec_pull(self, project_sim, lm_session):
        project = project_sim.as_project()
        pull_options = PullOptions()
        env_sessions = EnvironmentSessions(lm_session)
        project.pull(env_sessions, pull_options)

    def test_pull_descriptors_and_remove_name(self):
        project_sim = self.simlab.simulate_assembly_basic()
        with open(os.path.join(project_sim.path, ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), 'r') as current_descriptor:
            current_descriptor_content = current_descriptor.read()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_descriptor('name: assembly::basic::1.0\ndescription: descriptor content pulled from the environment\n')
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        lm_session.descriptor_driver.get_descriptor.assert_called_once_with('assembly::basic::1.0')
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_backup(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), current_descriptor_content)
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), 'description: descriptor content pulled from the environment\n')
        
    def test_pull_descriptor_ignores_not_found(self):
        project_sim = self.simlab.simulate_assembly_basic()
        with open(os.path.join(project_sim.path, ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), 'r') as current_descriptor:
            current_descriptor_content = current_descriptor.read()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        lm_session.descriptor_driver.get_descriptor.assert_called_once_with('assembly::basic::1.0')
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_no_backup(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE))
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), current_descriptor_content)
    
    def test_pull_descriptor_with_unresolvable_descriptor_name(self):
        project_sim = self.simlab.simulate_assembly_basic()
        with open(os.path.join(project_sim.path, ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), 'r') as current_descriptor:
            current_descriptor_content = current_descriptor.read()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_descriptor('name: assembly::basic::1.0\n'+DESCRIPTOR_WITH_UNRESOLVABLE_COMPONENT)
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_backup(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), current_descriptor_content)
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), DESCRIPTOR_WITH_UNRESOLVABLE_COMPONENT)

    def test_pull_behaviour_configuration(self):
        project_sim = self.simlab.simulate_assembly_with_behaviour()
        with open(os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple.json'), 'r') as current_configuration:
            current_configuration_content = current_configuration.read()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing', 'projectId': 'assembly::with_behaviour::1.0', 'name': 'simple', 'descriptorName': 'assembly::with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing2', 'projectId': 'assembly::with_behaviour::1.0', 'name': 'simple-2', 'descriptorName': 'assembly::with_behaviour::1.0'})
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        lm_session.behaviour_driver.get_assembly_configurations.assert_called_once_with('assembly::with_behaviour::1.0')
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_backup(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple.json'), current_configuration_content)
        project_assertions.assert_has_no_backup(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple-2.json'))
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple.json'), PULLED_SIMPLE_ASSEMBLY_CONFIGURATION)
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple-2.json'), PULLED_SIMPLE_2_ASSEMBLY_CONFIGURATION)
    
    def test_pull_behaviour_configuration_with_unresolvable_descriptor_name(self):
        project_sim = self.simlab.simulate_assembly_with_behaviour()
        with open(os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple.json'), 'r') as current_configuration:
            current_configuration_content = current_configuration.read()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing', 'projectId': 'assembly::with_behaviour::1.0', 'name': 'simple', 'descriptorName': 'assembly::another_descriptor::1.0'})
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        lm_session.behaviour_driver.get_assembly_configurations.assert_called_once_with('assembly::with_behaviour::1.0')
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple.json'), PULLED_SIMPLE_ASSEMBLY_CONFIGURATION_WITH_UNRESOLVABLE_DESCRIPTOR)
        
    def test_pull_behaviour_configuration_leaves_not_found_untouched(self):
        project_sim = self.simlab.simulate_assembly_with_behaviour()
        with open(os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple.json'), 'r') as current_configuration:
            current_configuration_content = current_configuration.read()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        lm_session.behaviour_driver.get_assembly_configurations.assert_called_once_with('assembly::with_behaviour::1.0')
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_no_backup(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple.json'))
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'simple.json'), current_configuration_content)
      
    def test_pull_runtime_scenarios(self):
        project_sim = self.simlab.simulate_assembly_with_behaviour()
        with open(os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime.json'), 'r') as current_runtime:
            current_runtime_content = current_runtime.read()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_sim.add_scenario(
            {
                'id': 'existingRuntime', 
                'projectId': 'assembly::with_behaviour::1.0', 
                'name': 'runtime', 
                'assemblyActors': [
                    {
                        'instanceName': 'ExistingProvidedAssembly',
                        'provided': True
                    }
                ]
            }
        )
        lm_sim.add_scenario(
            {
                'id': 'existingRuntime2', 
                'projectId': 'assembly::with_behaviour::1.0', 
                'name': 'runtime-2', 
                'assemblyActors': [
                    {
                        'instanceName': 'ExistingProvidedAssembly',
                        'provided': True
                    }
                ]
            }
        )
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_backup(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime.json'), current_runtime_content)
        project_assertions.assert_has_no_backup(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime-2.json'))
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime.json'), PULLED_RUNTIME_SCENARIO)
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime-2.json'), PULLED_RUNTIME_2_SCENARIO)
    
    def test_pull_runtime_scenarios_replaces_actor_ids(self):
        project_sim = self.simlab.simulate_assembly_with_behaviour()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 's123', 'projectId': 'assembly::with_behaviour::1.0', 'name': 'simple', 'descriptorName': 'assembly::with_behaviour::1.0'})
        lm_sim.add_scenario(
            {
                'id': 'existingRuntime', 
                'projectId': 'assembly::with_behaviour::1.0', 
                'name': 'runtime', 
                'assemblyActors': [
                    {
                        'instanceName': 'ExistingProvidedAssembly',
                        'provided': True
                    },
                    {
                        "instanceName": "simple",
                        "assemblyConfigurationId": "s123",
                        "initialState": "Active",
                        "uninstallOnExit": True,
                        "provided": False
                    },
                    {
                        "instanceName": "another",
                        "assemblyConfigurationId": "a123",
                        "initialState": "Active",
                        "uninstallOnExit": True,
                        "provided": False
                    }
                ]
            }
        )
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        lm_session.behaviour_driver.get_scenarios.assert_called_once_with('assembly::with_behaviour::1.0')
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime.json'), PULLED_RUNTIME_SCENARIO_ACTORS_REPLACED)

    def test_pull_behaviour_runtime_leaves_not_found_untouched(self):
        project_sim = self.simlab.simulate_assembly_with_behaviour()
        with open(os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime.json'), 'r') as current_runtime:
            current_runtime_content = current_runtime.read()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_no_backup(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime.json'))
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'runtime.json'), current_runtime_content)
      
    def test_pull_test_scenarios(self):
        project_sim = self.simlab.simulate_assembly_with_behaviour()
        with open(os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test.json'), 'r') as current_test:
            current_test_content = current_test.read()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_sim.add_scenario(
            {
                'id': 't123', 
                'projectId': 'assembly::with_behaviour::1.0', 
                'name': 'test', 
                'assemblyActors': [
                    {
                        "instanceName": "simple",
                        "assemblyConfigurationId": "s123",
                        "initialState": "Active",
                        "uninstallOnExit": True,
                        "provided": False
                    }
                ]
            }
        )
        lm_sim.add_scenario(
            {
                'id': 't456', 
                'projectId': 'assembly::with_behaviour::1.0', 
                'name': 'test-2', 
                'assemblyActors': [
                    {
                        "instanceName": "simple",
                        "assemblyConfigurationId": "s123",
                        "initialState": "Active",
                        "uninstallOnExit": True,
                        "provided": False
                    }
                ]
            }
        )
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        lm_session.behaviour_driver.get_scenarios.assert_called_once_with('assembly::with_behaviour::1.0')
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_backup(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test.json'), current_test_content)
        project_assertions.assert_has_no_backup(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test-2.json'))
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test.json'), PULLED_TEST_SCENARIO)
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test-2.json'), PULLED_TEST_2_SCENARIO)
    
    def test_pull_test_scenarios_replaces_actor_ids(self):
        project_sim = self.simlab.simulate_assembly_with_behaviour()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 's123', 'projectId': 'assembly::with_behaviour::1.0', 'name': 'simple', 'descriptorName': 'assembly::with_behaviour::1.0'})
        lm_sim.add_scenario(
            {
                'id': 't123', 
                'projectId': 'assembly::with_behaviour::1.0', 
                'name': 'test', 
                'assemblyActors': [
                    {
                        "instanceName": "simple",
                        "assemblyConfigurationId": "s123",
                        "initialState": "Active",
                        "uninstallOnExit": True,
                        "provided": False
                    },
                    {
                        "instanceName": "another",
                        "assemblyConfigurationId": "a123",
                        "initialState": "Active",
                        "uninstallOnExit": True,
                        "provided": False
                    }
                ]
            }
        )
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        lm_session.behaviour_driver.get_scenarios.assert_called_once_with('assembly::with_behaviour::1.0')
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test.json'), PULLED_TEST_SCENARIO_ACTORS_REPLACED)

    def test_pull_behaviour_test_leaves_not_found_untouched(self):
        project_sim = self.simlab.simulate_assembly_with_behaviour()
        with open(os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test.json'), 'r') as current_test:
            current_test_content = current_test.read()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_session = lm_sim.as_mocked_session()
        self.__exec_pull(project_sim, lm_session)
        project_assertions = self.assert_project(project_sim.as_project())
        project_assertions.assert_has_no_backup(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test.json'))
        project_assertions.assert_has_file(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'test.json'), current_test_content)
     