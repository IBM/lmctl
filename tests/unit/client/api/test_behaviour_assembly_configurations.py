import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import BehaviourAssemblyConfigurationsAPI

class TestBehaviourAssemblyConfigurationsAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.behaviour_assembly_configurations = BehaviourAssemblyConfigurationsAPI(self.mock_client)

    def test_all(self):
        all_objects = [{'id': 'Test', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = all_objects
        response = self.behaviour_assembly_configurations.all()
        self.assertEqual(response, all_objects)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/assemblyConfigurations')
    
    def test_all_in_project(self):
        mock_response = [{'id': 'Test', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_assembly_configurations.all_in_project('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/assemblyConfigurations?projectId=Test')

    def test_get(self):
        mock_response = {'id': 'Test', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_assembly_configurations.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/assemblyConfigurations/Test')

    def test_create(self):
        test_obj = {'name': 'Test'}
        mock_response = MagicMock(headers={'Location': '/api/behaviour/assemblyConfigurations/123'})
        self.mock_client.make_request.return_value = mock_response
        response = self.behaviour_assembly_configurations.create(test_obj)
        self.assertEqual(response, {'id': '123', 'name': 'Test'})
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/behaviour/assemblyConfigurations', json=test_obj)

    def test_update(self):
        test_obj = {'id': '123', 'name': 'Test'}
        response = self.behaviour_assembly_configurations.update(test_obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='PUT', endpoint='api/behaviour/assemblyConfigurations/123', json=test_obj)

    def test_delete(self):
        response = self.behaviour_assembly_configurations.delete('123')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='DELETE', endpoint='api/behaviour/assemblyConfigurations/123')
    

