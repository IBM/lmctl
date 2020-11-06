import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import BehaviourScenariosAPI

class TestBehaviourScenariosAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.behaviour_scenarios = BehaviourScenariosAPI(self.mock_client)

    def test_all_in_project(self):
        mock_response = [{'id': 'Test', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_scenarios.all_in_project('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/scenarios?projectId=Test')

    def test_get(self):
        mock_response = {'id': 'Test', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_scenarios.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/scenarios/Test')

    def test_create(self):
        test_obj = {'name': 'Test'}
        mock_response = MagicMock(headers={'Location': '/api/behaviour/scenarios/123'})
        self.mock_client.make_request.return_value = mock_response
        response = self.behaviour_scenarios.create(test_obj)
        self.assertEqual(response, {'id': '123', 'name': 'Test'})
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/behaviour/scenarios', json=test_obj)

    def test_update(self):
        test_obj = {'id': '123', 'name': 'Test'}
        response = self.behaviour_scenarios.update(test_obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='PUT', endpoint='api/behaviour/scenarios/123', json=test_obj)

    def test_delete(self):
        response = self.behaviour_scenarios.delete('123')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='DELETE', endpoint='api/behaviour/scenarios/123')
    

