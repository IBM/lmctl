import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import BehaviourScenarioExecutionsAPI

class TestBehaviourScenarioExecutionsAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.behaviour_scenario_execs = BehaviourScenarioExecutionsAPI(self.mock_client)

    def test_execute_with_scenario_id(self):
        mock_response = MagicMock(headers={'Location': '/api/behaviour/executions/789'})
        self.mock_client.make_request.return_value = mock_response
        response = self.behaviour_scenario_execs.execute(scenario_id='Test')
        self.assertEqual(response, '789')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/behaviour/executions', json={'scenarioId': 'Test'})
    
    def test_execute_with_scenario_id_and_request(self):
        mock_response = MagicMock(headers={'Location': '/api/behaviour/executions/789'})
        self.mock_client.make_request.return_value = mock_response
        response = self.behaviour_scenario_execs.execute(scenario_id='Test', execution_request={'assemblyId': 'assemblyA'})
        self.assertEqual(response, '789')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/behaviour/executions', json={'scenarioId': 'Test', 'assemblyId': 'assemblyA'})
    
    def test_execute_with_request(self):
        mock_response = MagicMock(headers={'Location': '/api/behaviour/executions/789'})
        self.mock_client.make_request.return_value = mock_response
        response = self.behaviour_scenario_execs.execute(execution_request={'scenarioId': 'scenarioA', 'assemblyId': 'assemblyA'})
        self.assertEqual(response, '789')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/behaviour/executions', json={'scenarioId': 'scenarioA', 'assemblyId': 'assemblyA'})

    def test_cancel(self):
        mock_response = {'success': True}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_scenario_execs.cancel('Test')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/behaviour/executions/Test/cancel')
        self.assertEqual(response, mock_response)

    def test_get(self):
        mock_response = {'id': 'Test', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_scenario_execs.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/executions/Test')

    def test_get_include_scenarios(self):
        mock_response = {'id': 'Test', 'name': 'Test', 'scenario': {}}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_scenario_execs.get('Test', include_scenario=True)
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/executions/Test?includeScenario=True')

    def test_delete(self):
        response = self.behaviour_scenario_execs.delete('Test')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='DELETE', endpoint='api/behaviour/executions/Test')
    
    def test_all_in_project(self):
        mock_response = [{'id': 'Test', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_scenario_execs.all_in_project('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/executions?projectId=Test')
    
    def test_all_of_scenario(self):
        mock_response = [{'id': 'Test', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_scenario_execs.all_of_scenario('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/executions?scenarioId=Test')

    def test_get_progress(self):
        mock_response = {'id': 'Test', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_scenario_execs.get_progress('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/executions/Test/progress')
    
    def test_get_metrics(self):
        mock_response = [{'id': 'Test', 'name': 'TestMetric'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_scenario_execs.get_metrics('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/executions/Test/metrics')
    
    def test_get_metric(self):
        mock_response = {'id': 'Test', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_scenario_execs.get_metric('Test', 'TestMetric')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/executions/Test/metrics/TestMetric')
