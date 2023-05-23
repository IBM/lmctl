import unittest
from unittest.mock import call
import os
import tests.common.simulations.project_lab as project_lab
from tests.common.project_testing import (ProjectSimTestCase, PROJECT_CONTAINS_DIR)
from lmctl.project.sessions import EnvironmentSessions
from lmctl.project.package.core import Pkg, PkgContent, PushOptions
from lmctl.project.handlers.assembly.assembly_src import TEMPLATE_CONTENT

WITH_TEMPLATE_ASSEMBLY_TEMPLATE_DESCRIPTOR_YAML = "name: assembly-template::with_template::1.0"
WITH_TEMPLATE_ASSEMBLY_TEMPLATE_DESCRIPTOR_YAML += "\n"
WITH_TEMPLATE_ASSEMBLY_TEMPLATE_DESCRIPTOR_YAML += TEMPLATE_CONTENT

class TestPushAssemblyPkgs(ProjectSimTestCase):

    def test_push_creates_descriptor(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_basic()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.descriptor_driver.get_descriptor.assert_called_once_with('assembly::basic::1.0')
        lm_session.descriptor_driver.create_descriptor.assert_called_once_with('name: assembly::basic::1.0\ndescription: basic_assembly\n')

    def test_push_updates_descriptors_if_exists(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_basic()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_descriptor('name: assembly::basic::1.0\ndescription: pre-update basic_assembly\n')
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.descriptor_driver.get_descriptor.assert_called_once_with('assembly::basic::1.0')
        lm_session.descriptor_driver.create_descriptor.assert_not_called()
        lm_session.descriptor_driver.update_descriptor.assert_called_once_with('assembly::basic::1.0', 'name: assembly::basic::1.0\ndescription: basic_assembly\n')

    def test_push_creates_descriptor_template(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_with_template()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.descriptor_template_driver.get_descriptor_template.assert_called_once_with('assembly-template::with_template::1.0')
        lm_session.descriptor_template_driver.create_descriptor_template.assert_called_once_with(WITH_TEMPLATE_ASSEMBLY_TEMPLATE_DESCRIPTOR_YAML)

    def test_push_updates_descriptors_template_if_exists(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_with_template()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_descriptor_template('name: assembly-template::with_template::1.0\ndescription: pre-update\n')
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.descriptor_template_driver.get_descriptor_template.assert_called_once_with('assembly-template::with_template::1.0')
        lm_session.descriptor_template_driver.create_descriptor_template.assert_not_called()
        lm_session.descriptor_template_driver.update_descriptor_template.assert_called_once_with('assembly-template::with_template::1.0', WITH_TEMPLATE_ASSEMBLY_TEMPLATE_DESCRIPTOR_YAML)

    def test_push_creates_behaviour_configuration(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_assembly_configuration.assert_called_once_with({
            "name": "simple",
            "projectId": "assembly::with_behaviour::1.0",
            "description": "a simple assembly config",
            "properties": {
                "a": "123"
            },
            "createdAt": "2019-01-01T01:00:00.613Z",
            "lastModifiedAt": "2019-01-02T01:00:00.613Z",
            "descriptorName": "assembly::with_behaviour::1.0"
        })

    def test_push_updates_behaviour_configuration_if_exists(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing', 'projectId': 'assembly::with_behaviour::1.0', 'name': 'simple'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_assembly_configuration.assert_not_called()
        lm_session.behaviour_driver.update_assembly_configuration.assert_called_once_with({
            "id": "existing",
            "name": "simple",
            "projectId": "assembly::with_behaviour::1.0",
            "description": "a simple assembly config",
            "properties": {
                "a": "123"
            },
            "createdAt": "2019-01-01T01:00:00.613Z",
            "lastModifiedAt": "2019-01-02T01:00:00.613Z",
            "descriptorName": "assembly::with_behaviour::1.0"
        })

    def test_push_creates_behaviour_scenarios(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing', 'projectId': 'assembly::with_behaviour::1.0', 'name': 'simple'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_scenario.assert_has_calls([
            call({
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
                    "provided": True
                    }
                ],
                "createdAt": "2019-01-01T01:00:00.613Z",
                "lastModifiedAt": "2019-01-02T01:00:00.613Z"
            }),
            call({
                "name": "test",
                "projectId": "assembly::with_behaviour::1.0",
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

    def test_push_creates_scenario_with_missing_config(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_with_scenario_referencing_missing_config() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_scenario_referencing_missing_config::1.0', 'name': 'assembly::with_scenario_referencing_missing_config::1.0'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_scenario.assert_called_once_with(
            {
                "name": "test",
                "projectId": "assembly::with_scenario_referencing_missing_config::1.0",
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
                    "assemblyConfigurationId": "missing",
                    "initialState": "Active",
                    "uninstallOnExit": True,
                    "provided": False
                    }
                ],
                "createdAt": "2019-01-01T01:00:00.613Z",
                "lastModifiedAt": "2019-01-02T01:00:00.613Z"
            }
        )

    def test_push_updates_behaviour_scenarios_if_exists(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::with_behaviour::1.0', 'name': 'assembly::with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing', 'projectId': 'assembly::with_behaviour::1.0', 'name': 'simple'})
        lm_sim.add_scenario({'id': 'existingRuntime', 'projectId': 'assembly::with_behaviour::1.0', 'name': 'runtime'})
        lm_sim.add_scenario({'id': 'existingTest', 'projectId': 'assembly::with_behaviour::1.0', 'name': 'test'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_scenario.assert_not_called()
        lm_session.behaviour_driver.update_scenario.assert_has_calls([
            call({
                "id": "existingRuntime", 
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
                    "provided": True
                    }
                ],
                "createdAt": "2019-01-01T01:00:00.613Z",
                "lastModifiedAt": "2019-01-02T01:00:00.613Z"
            }),
            call({
                "id": "existingTest", 
                "name": "test",
                "projectId": "assembly::with_behaviour::1.0",
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


class TestPushAssemblyPkgsSubcontent(ProjectSimTestCase):

    def test_push_creates_descriptor(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_assembly_basic()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.descriptor_driver.get_descriptor.assert_has_calls([call('assembly::sub_basic-contains_basic::1.0'), call('assembly::contains_basic::1.0')])
        lm_session.descriptor_driver.create_descriptor.assert_has_calls([
            call('name: assembly::sub_basic-contains_basic::1.0\ndescription: descriptor\n'),
            call('name: assembly::contains_basic::1.0\ndescription: basic_assembly\n')])

    def test_push_updates_descriptors_if_exists(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_assembly_basic()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_descriptor('name: assembly::sub_basic-contains_basic::1.0\ndescription: pre-update\n')
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.descriptor_driver.get_descriptor.assert_has_calls([call('assembly::sub_basic-contains_basic::1.0'), call('assembly::contains_basic::1.0')])
        lm_session.descriptor_driver.update_descriptor.assert_called_once_with('assembly::sub_basic-contains_basic::1.0', 'name: assembly::sub_basic-contains_basic::1.0\ndescription: descriptor\n')

    def test_push_creates_behaviour_configuration(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_assembly_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_assembly_configuration.assert_called_once_with({
            "name": "simple",
            "projectId": "assembly::sub_with_behaviour-contains_with_behaviour::1.0",
            "description": "a simple assembly config",
            "properties": {
                "a": "123"
            },
            "createdAt": "2019-01-01T01:00:00.613Z",
            "lastModifiedAt": "2019-01-02T01:00:00.613Z",
            "descriptorName": "assembly::sub_with_behaviour-contains_with_behaviour::1.0"
        })

    def test_push_updates_behaviour_configuration_if_exists(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_assembly_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::sub_with_behaviour-contains_with_behaviour::1.0', 'name': 'assembly::sub_with_behaviour-contains_with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing', 'projectId': 'assembly::sub_with_behaviour-contains_with_behaviour::1.0', 'name': 'simple'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_assembly_configuration.assert_not_called()
        lm_session.behaviour_driver.update_assembly_configuration.assert_called_once_with({
            "id": "existing",
            "name": "simple",
            "projectId": "assembly::sub_with_behaviour-contains_with_behaviour::1.0",
            "description": "a simple assembly config",
            "properties": {
                "a": "123"
            },
            "createdAt": "2019-01-01T01:00:00.613Z",
            "lastModifiedAt": "2019-01-02T01:00:00.613Z",
            "descriptorName": "assembly::sub_with_behaviour-contains_with_behaviour::1.0"
        })

    def test_push_creates_behaviour_scenarios(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_assembly_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::sub_with_behaviour-contains_with_behaviour::1.0', 'name': 'assembly::sub_with_behaviour-contains_with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing', 'projectId': 'assembly::sub_with_behaviour-contains_with_behaviour::1.0', 'name': 'simple'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_scenario.assert_has_calls([
            call({
                "name": "runtime",
                "projectId": "assembly::sub_with_behaviour-contains_with_behaviour::1.0",
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
                    "provided": True
                    }
                ],
                "createdAt": "2019-01-01T01:00:00.613Z",
                "lastModifiedAt": "2019-01-02T01:00:00.613Z"
            }),
            call({
                "name": "test",
                "projectId": "assembly::sub_with_behaviour-contains_with_behaviour::1.0",
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
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_assembly_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_project({'id': 'assembly::sub_with_behaviour-contains_with_behaviour::1.0', 'name': 'assembly::sub_with_behaviour-contains_with_behaviour::1.0'})
        lm_sim.add_assembly_configuration({'id': 'existing', 'projectId': 'assembly::sub_with_behaviour-contains_with_behaviour::1.0', 'name': 'simple'})
        lm_sim.add_scenario({'id': 'existingRuntime', 'projectId': 'assembly::sub_with_behaviour-contains_with_behaviour::1.0', 'name': 'runtime'})
        lm_sim.add_scenario({'id': 'existingTest', 'projectId': 'assembly::sub_with_behaviour-contains_with_behaviour::1.0', 'name': 'test'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        lm_session.behaviour_driver.create_scenario.assert_not_called()
        lm_session.behaviour_driver.update_scenario.assert_has_calls([
            call({
                "id": "existingRuntime", 
                "name": "runtime",
                "projectId": "assembly::sub_with_behaviour-contains_with_behaviour::1.0",
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
                    "provided": True
                    }
                ],
                "createdAt": "2019-01-01T01:00:00.613Z",
                "lastModifiedAt": "2019-01-02T01:00:00.613Z"
            }),
            call({
                "id": "existingTest", 
                "name": "test",
                "projectId": "assembly::sub_with_behaviour-contains_with_behaviour::1.0",
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


class TestPushOldStyle(ProjectSimTestCase):

    def test_push(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_old_style()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        arm_sim = self.simlab.simulate_arm()
        arm_session = arm_sim.as_mocked_session()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_rm({'name': arm_session.env.name, 'url': arm_session.env.address})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session, arm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        csar_a_path = os.path.join(result.tree.root_path, PROJECT_CONTAINS_DIR, 'vnfcA', 'vnfcA.csar')
        csar_b_path = os.path.join(result.tree.root_path, PROJECT_CONTAINS_DIR, 'vnfcB', 'vnfcB.csar')
        arm_session.arm_driver.onboard_type.assert_has_calls([call('vnfcA', '1.0', csar_a_path), call('vnfcB', '2.0', csar_b_path)])
