import time
from tests.integration.integration_test_base import IntegrationTest

class TestBehaviourScenarioExecutionsAPI(IntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add Assembly descriptor - this creates a project for us
        assembly_descriptor = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='scenarioexec-tests')
        tester.default_client.descriptors.create(assembly_descriptor)
        cls.test_case_props['dummy_assembly_descriptor_name'] = assembly_descriptor['name']
        
    @classmethod
    def after_test_case(cls, tester):
        ## Deletes project and all scenarios
        tester.default_client.descriptors.delete(cls.test_case_props['dummy_assembly_descriptor_name'])
   
    def _create_scenario(self, name_suffix: str):
        ## Add Scenario - need a unique scenario for each test 
        # so we don't have to worry about execution names (based on current time, precise to seconds) colliding
        scenario = self.tester.load_behaviour_scenario_from(self.tester.test_file('metric_scenario.json'), suffix='scenarioexec-tests')
        scenario['name'] = self.tester.exec_prepended_name(name_suffix)
        scenario['projectId'] = self.test_case_props['dummy_assembly_descriptor_name']
        create_scenario_response = self.tester.default_client.behaviour_scenarios.create(scenario)
        return create_scenario_response['id']

    def _check_exec_success(self, execution_id: str) -> bool:
        execution = self.tester.default_client.behaviour_scenario_execs.get(execution_id)
        status = execution.get('status')
        if status in ['PASS']:
            return True
        elif status in ['ABORTED', 'FAIL']:
            reason = execution.get('error')
            self.fail(f'Execution failed with status {status}, reason: {reason}')
        else:
            return False

    def test_execute_and_get(self):
        scenario_id = self._create_scenario('test-execute-and-get')
        executions_api = self.tester.default_client.behaviour_scenario_execs
        execution_id = executions_api.execute({'scenarioId': scenario_id})
        ## Get
        get_response = executions_api.get(execution_id)
        self.assertIsNotNone(get_response)
        self.assertEqual(get_response['scenarioId'], scenario_id)
        self.assertIsNone(get_response['scenarioSummary'])
        ## Get - include scenario
        get_response = executions_api.get(execution_id, include_scenario=True)
        self.assertIsNotNone(get_response['scenarioSummary'])
        ## Get progress
        get_progress_response = executions_api.get_progress(execution_id)
        self.assertIsNotNone(get_progress_response)
        self.assertEqual(get_progress_response['id'], get_response['id'])
        self.assertTrue(len(get_progress_response['stageReports']) > 0)
        ## Wait for execution to finish
        self.tester.wait_until(self._check_exec_success, execution_id)
        time.sleep(0.05)
        ## Get Metrics
        get_metrics_response = executions_api.get_metrics(execution_id)
        self.assertIsNotNone(get_metrics_response)
        self.assertEqual(len(get_metrics_response), 1)
        self.assertEqual(get_metrics_response[0]['name'], 'test-metric-heartbeat')
        ## Get Metric
        get_metric_response = executions_api.get_metric(execution_id, get_metrics_response[0]['id'])
        self.assertIsNotNone(get_metric_response)
        self.assertEqual(get_metric_response['name'], 'test-metric-heartbeat')
    
    def test_cancel(self):
        scenario_id = self._create_scenario('test-cancel')
        executions_api = self.tester.default_client.behaviour_scenario_execs
        execution_id = executions_api.execute({'scenarioId': scenario_id})
        ## Cancel
        cancel_response = executions_api.cancel(execution_id)
        self.assertTrue(cancel_response['success'])

    def test_all_in_project_and_scenario(self):
        executions_api = self.tester.default_client.behaviour_scenario_execs
        scenario_A_id = self._create_scenario('test-all-in-A')
        execution_A_id = executions_api.execute({'scenarioId': scenario_A_id})
        scenario_B_id = self._create_scenario('test-all-in-B')
        execution_B_id = executions_api.execute({'scenarioId': scenario_B_id})
        ## All in project
        all_in_project_response = executions_api.all_in_project(self.test_case_props['dummy_assembly_descriptor_name'])
        self.assertEqual(len(all_in_project_response), 2)
        ids = []
        for execution in all_in_project_response:
            ids.append(execution['id'])
        self.assertIn(execution_A_id, ids)
        self.assertIn(execution_B_id, ids)
        ## All of Scenario
        all_of_scenario_response = executions_api.all_of_scenario(scenario_B_id)
        self.assertEqual(len(all_of_scenario_response), 1)
        self.assertEqual(all_of_scenario_response[0]['id'], execution_B_id)