import unittest
from unittest.mock import call
import os
import tests.common.simulations.project_lab as project_lab
from tests.common.project_testing import (ProjectSimTestCase, PROJECT_CONTAINS_DIR)
from lmctl.project.sessions import EnvironmentSessions
from lmctl.project.package.core import Pkg, PkgContent, PushOptions

class TestPushTestPkgs(ProjectSimTestCase):

    def test_push_creates_descriptor(self):
        pkg_sim = self.simlab.simulate_pkg_type_basic()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.descriptor_driver.get_descriptor.assert_called_once_with('type::basic::1.0')
        lm_session.descriptor_driver.create_descriptor.assert_called_once_with('name: type::basic::1.0\ndescription: descriptor for basic\n', object_group_id=None)

    def test_push_updates_descriptors_if_exists(self):
        pkg_sim = self.simlab.simulate_pkg_type_basic()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_descriptor('name: type::basic::1.0\ndescription: pre-update descriptor for basic\n')
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.descriptor_driver.get_descriptor.assert_called_once_with('type::basic::1.0')
        lm_session.descriptor_driver.create_descriptor.assert_not_called()
        lm_session.descriptor_driver.update_descriptor.assert_called_once_with('type::basic::1.0', 'name: type::basic::1.0\ndescription: descriptor for basic\n')

    def test_push_creates_behaviour_configuration(self):
        pkg_sim = self.simlab.simulate_pkg_type_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_assembly_configuration.assert_called_once_with({
            "name": "simple",
            "projectId": "type::with_behaviour::1.0",
            "description": "a simple assembly config",
            "properties": {
                "a": "123"
            },
            "createdAt": "2019-01-01T01:00:00.613Z",
            "lastModifiedAt": "2019-01-02T01:00:00.613Z",
            "descriptorName": "type::with_behaviour::1.0"
        })

    def test_push_updates_behaviour_configuration_if_exists(self):
        pkg_sim = self.simlab.simulate_pkg_type_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'type::with_behaviour::1.0', 'name': 'type::with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing', 'projectId': 'type::with_behaviour::1.0', 'name': 'simple'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_assembly_configuration.assert_not_called()
        lm_session.behaviour_driver.update_assembly_configuration.assert_called_once_with({
            "id": "existing",
            "name": "simple",
            "projectId": "type::with_behaviour::1.0",
            "description": "a simple assembly config",
            "properties": {
                "a": "123"
            },
            "createdAt": "2019-01-01T01:00:00.613Z",
            "lastModifiedAt": "2019-01-02T01:00:00.613Z",
            "descriptorName": "type::with_behaviour::1.0"
        })

    def test_push_creates_behaviour_scenarios(self):
        pkg_sim = self.simlab.simulate_pkg_type_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'type::with_behaviour::1.0', 'name': 'type::with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing', 'projectId': 'type::with_behaviour::1.0', 'name': 'simple'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_scenario.assert_has_calls([
            call({
                "name": "test",
                "projectId": "type::with_behaviour::1.0",
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
                    "assemblyConfigurationId": "existing",
                    "initialState": "Active",
                    "uninstallOnExit": True,
                    "provided": False
                    }
                ],
                "createdAt": "2019-01-01T01:00:00.613Z",
                "lastModifiedAt": "2019-01-02T01:00:00.613Z"
            })
        ])

    def test_push_updates_behaviour_scenarios_if_exists(self):
        pkg_sim = self.simlab.simulate_pkg_type_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'type::with_behaviour::1.0', 'name': 'type::with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing', 'projectId': 'type::with_behaviour::1.0', 'name': 'simple'})
        lm_sim.add_scenario({'id': 'existingRuntime', 'projectId': 'type::with_behaviour::1.0', 'name': 'runtime'})
        lm_sim.add_scenario({'id': 'existingTest', 'projectId': 'type::with_behaviour::1.0', 'name': 'test'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_scenario.assert_not_called()
        lm_session.behaviour_driver.update_scenario.assert_has_calls([
            call({
                "id": "existingTest", 
                "name": "test",
                "projectId": "type::with_behaviour::1.0",
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
                    "assemblyConfigurationId": "existing",
                    "initialState": "Active",
                    "uninstallOnExit": True,
                    "provided": False
                    }
                ],
                "createdAt": "2019-01-01T01:00:00.613Z",
                "lastModifiedAt": "2019-01-02T01:00:00.613Z"
            })
        ])