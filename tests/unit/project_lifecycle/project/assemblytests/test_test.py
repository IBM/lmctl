import unittest
from unittest.mock import call
import tests.common.simulations.project_lab as project_lab
from tests.common.project_testing import (ProjectSimTestCase, PROJECT_CONTAINS_DIR)
from lmctl.project.sessions import EnvironmentSessions
from lmctl.project.package.core import Pkg, PkgContent, TestOptions, PushOptions
from lmctl.project.testing import PkgTestReport, TestSuiteExecutionReport, TEST_STATUS_PASSED, TEST_STATUS_FAILED
import lmctl.project.handlers.assembly.assembly_content as assembly_content


class TestTestAssemblyPkgs(ProjectSimTestCase):

    def setUp(self):
        assembly_content.set_polling_period(0.1)

    def tearDown(self):
        assembly_content.reset_polling_period()

    def test_runs_with_no_tests(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_basic() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        test_options = TestOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options).test(env_sessions, test_options)
        self.assertIsInstance(result, PkgTestReport)
        self.assertEqual(result.name, 'basic')
        self.assertEqual(result.full_name, 'basic')
        self.assertIsInstance(result.suite_report, TestSuiteExecutionReport)
        self.assertEqual(len(result.suite_report.entries), 0)

    def test_runs_test_scenarios(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        test_options = TestOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options).test(env_sessions, test_options)
        self.assertIsInstance(result, PkgTestReport)
        self.assertEqual(result.name, 'with_behaviour')
        self.assertEqual(result.full_name, 'with_behaviour')
        self.assertIsInstance(result.suite_report, TestSuiteExecutionReport)
        self.assertEqual(len(result.suite_report.entries), 1)
        self.assertEqual(result.suite_report.entries[0].test_name, 'test')
        self.assertEqual(result.suite_report.entries[0].result, TEST_STATUS_PASSED)
        self.assertIsNone(result.suite_report.entries[0].detail)
        scenarios_on_project = lm_sim.get_scenarios_on_project('assembly::with_behaviour::1.0')
        expected_scenario = next((x for x in scenarios_on_project if x['name'] == 'test'), None)
        lm_session.behaviour_driver.execute_scenario.assert_called_once_with(expected_scenario['id'])
        scenario_executions = lm_sim.get_executions_on_scenario(expected_scenario['id'])
        self.assertEqual(len(scenario_executions), 1)
        lm_session.behaviour_driver.get_execution.assert_called_with(scenario_executions[0]['id'])

    def test_runs_multi_tests(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_with_behaviour_multi_tests() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        test_options = TestOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options).test(env_sessions, test_options)
        self.assertEqual(len(result.suite_report.entries), 3)
        test1_entry = None
        test2_entry = None
        test3_entry = None
        for entry in result.suite_report.entries:
            if entry.test_name == 'test':
                test1_entry = entry
            elif entry.test_name == 'test2':
                test2_entry = entry
            elif entry.test_name == 'test3':
                test3_entry = entry
        self.assertEqual(test1_entry.test_name, 'test')
        self.assertEqual(test1_entry.result, TEST_STATUS_PASSED)
        self.assertIsNone(test1_entry.detail)
        self.assertEqual(test2_entry.test_name, 'test2')
        self.assertEqual(test2_entry.result, TEST_STATUS_PASSED)
        self.assertIsNone(test2_entry.detail)
        self.assertEqual(test3_entry.test_name, 'test3')
        self.assertEqual(test3_entry.result, TEST_STATUS_PASSED)
        self.assertIsNone(test3_entry.detail)
        scenarios_on_project = lm_sim.get_scenarios_on_project('assembly::with_behaviour_multi_tests::1.0')
        expected_calls = []
        for scenario in scenarios_on_project:
            if scenario['name'] != 'runtime':
                expected_calls.append(call(scenario['id']))
        lm_session.behaviour_driver.execute_scenario.assert_has_calls(expected_calls)
    
    def test_reports_test_failure(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_with_behaviour_multi_tests() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        test_options = TestOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.execution_listener.add_step_failure_trigger('assembly::with_behaviour_multi_tests::1.0', 'test2', 1, 0, 'Mocked Error')
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options).test(env_sessions, test_options)
        self.assertEqual(len(result.suite_report.entries), 3)
        test1_entry = None
        test2_entry = None
        test3_entry = None
        for entry in result.suite_report.entries:
            if entry.test_name == 'test':
                test1_entry = entry
            elif entry.test_name == 'test2':
                test2_entry = entry
            elif entry.test_name == 'test3':
                test3_entry = entry
        self.assertEqual(test1_entry.test_name, 'test')
        self.assertEqual(test1_entry.result, TEST_STATUS_PASSED)
        self.assertIsNone(test1_entry.detail)
        self.assertEqual(test2_entry.test_name, 'test2')
        self.assertEqual(test2_entry.result, TEST_STATUS_FAILED)
        self.assertEqual(test2_entry.detail, 'test2 failed: Mocked Error')
        self.assertEqual(test3_entry.test_name, 'test3')
        self.assertEqual(test3_entry.result, TEST_STATUS_PASSED)
        self.assertIsNone(test3_entry.detail)


class TestTestAssemblyPkgsSubcontent(ProjectSimTestCase):

    def setUp(self):
        assembly_content.set_polling_period(0.1)

    def tearDown(self):
        assembly_content.reset_polling_period()

    def test_runs_with_no_tests(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_assembly_basic() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        test_options = TestOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options).test(env_sessions, test_options)
        self.assertIsInstance(result, PkgTestReport)
        self.assertEqual(result.name, 'contains_basic')
        self.assertEqual(result.full_name, 'contains_basic')
        self.assertIsInstance(result.suite_report, TestSuiteExecutionReport)
        self.assertEqual(len(result.suite_report.entries), 0)
        self.assertEqual(len(result.sub_reports), 1)
        sub_report = result.sub_reports[0]
        self.assertIsInstance(sub_report, PkgTestReport)
        self.assertEqual(sub_report.name, 'sub_basic')
        self.assertEqual(sub_report.full_name, 'sub_basic-contains_basic')
        self.assertIsInstance(sub_report.suite_report, TestSuiteExecutionReport)
        self.assertEqual(len(sub_report.suite_report.entries), 0)

    def test_runs_test_scenarios(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_assembly_with_behaviour() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        test_options = TestOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options).test(env_sessions, test_options)
        self.assertIsInstance(result, PkgTestReport)
        self.assertEqual(result.name, 'contains_with_behaviour')
        self.assertEqual(result.full_name, 'contains_with_behaviour')
        self.assertIsInstance(result.suite_report, TestSuiteExecutionReport)
        self.assertEqual(len(result.suite_report.entries), 0)
        self.assertEqual(len(result.sub_reports), 1)
        sub_report = result.sub_reports[0]
        self.assertEqual(sub_report.name, 'sub_with_behaviour')
        self.assertEqual(sub_report.full_name, 'sub_with_behaviour-contains_with_behaviour')
        self.assertEqual(len(sub_report.suite_report.entries), 1)
        self.assertEqual(sub_report.suite_report.entries[0].test_name, 'test')
        self.assertEqual(sub_report.suite_report.entries[0].result, TEST_STATUS_PASSED)
        self.assertIsNone(sub_report.suite_report.entries[0].detail)
        scenarios_on_project = lm_sim.get_scenarios_on_project('assembly::sub_with_behaviour-contains_with_behaviour::1.0')
        expected_scenario = next((x for x in scenarios_on_project if x['name'] == 'test'), None)
        lm_session.behaviour_driver.execute_scenario.assert_called_once_with(expected_scenario['id'])
        scenario_executions = lm_sim.get_executions_on_scenario(expected_scenario['id'])
        self.assertEqual(len(scenario_executions), 1)
        lm_session.behaviour_driver.get_execution.assert_called_with(scenario_executions[0]['id'])

    def test_runs_multi_tests(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_assembly_with_behaviour_multi_tests() 
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        test_options = TestOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options).test(env_sessions, test_options)
        self.assertEqual(len(result.suite_report.entries), 0)
        self.assertEqual(len(result.sub_reports), 1)
        sub_report = result.sub_reports[0]
        self.assertEqual(len(sub_report.suite_report.entries), 3)
        test1_entry = None
        test2_entry = None
        test3_entry = None
        for entry in sub_report.suite_report.entries:
            if entry.test_name == 'test':
                test1_entry = entry
            elif entry.test_name == 'test2':
                test2_entry = entry
            elif entry.test_name == 'test3':
                test3_entry = entry
        self.assertEqual(test1_entry.test_name, 'test')
        self.assertEqual(test1_entry.result, TEST_STATUS_PASSED)
        self.assertIsNone(test1_entry.detail)
        self.assertEqual(test2_entry.test_name, 'test2')
        self.assertEqual(test2_entry.result, TEST_STATUS_PASSED)
        self.assertIsNone(test2_entry.detail)
        self.assertEqual(test3_entry.test_name, 'test3')
        self.assertEqual(test3_entry.result, TEST_STATUS_PASSED)
        self.assertIsNone(test3_entry.detail)
        scenarios_on_project = lm_sim.get_scenarios_on_project('assembly::sub_with_behaviour_multi_tests-contains_with_behaviour_multi_tests::1.0')
        expected_calls = []
        for scenario in scenarios_on_project:
            if scenario['name'] != 'runtime':
                expected_calls.append(call(scenario['id']))
        lm_session.behaviour_driver.execute_scenario.assert_has_calls(expected_calls)