import unittest
import json
from unittest.mock import patch, MagicMock
from lmctl.client.api import DeploymentLocationAPI
from lmctl.client.client_request import TNCOClientRequest

class TestDeploymentLocationAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.deployment_locations = DeploymentLocationAPI(self.mock_client)

    def test_all(self):
        all_locations = [{'id': 'Test', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = all_locations
        response = self.deployment_locations.all()
        self.assertEqual(response, all_locations)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/deploymentLocations'))

    def test_all_with_name(self):
        mock_response = [{'id': 'Test', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.deployment_locations.all_with_name('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/deploymentLocations', query_params={'name': 'Test'}))

    def test_get(self):
        mock_response = {'id': 'Test', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.deployment_locations.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/deploymentLocations/Test'))

    def test_create(self):
        location = {'name': 'Test'}
        body = json.dumps(location)
        mock_response = MagicMock(headers={'Location': '/api/deploymentLocations/123'})
        self.mock_client.make_request.return_value = mock_response
        response = self.deployment_locations.create(location)
        self.assertEqual(response, {'id': '123', 'name': 'Test'})
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/deploymentLocations', headers={'Content-Type': 'application/json'}, body=body))

    def test_update(self):
        location = {'id': '123', 'name': 'Test'}
        body = json.dumps(location)
        response = self.deployment_locations.update(location)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='PUT', endpoint='api/deploymentLocations/123', headers={'Content-Type': 'application/json'}, body=body))

    def test_delete(self):
        response = self.deployment_locations.delete('123')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='DELETE', endpoint='api/deploymentLocations/123'))
    

