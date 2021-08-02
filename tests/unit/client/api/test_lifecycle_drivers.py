import unittest
import json
from unittest.mock import patch, MagicMock
from lmctl.client.api import LifecycleDriversAPI
from lmctl.client.client_request import TNCOClientRequest

class TestLifecycleDriversAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.resource_drivers = LifecycleDriversAPI(self.mock_client)

    def test_get(self):
        mock_response = {'id': 'Test', 'type': 'Ansible'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.resource_drivers.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/v1/resource-manager/lifecycle-drivers/Test'))
    
    def test_get_by_type(self):
        mock_response = {'id': 'Test', 'type': 'Ansible'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.resource_drivers.get_by_type('Ansible')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/v1/resource-manager/lifecycle-drivers', query_params={'type': 'Ansible'}))

    def test_create(self):
        test_obj = {'type': 'Ansible'}
        body = json.dumps(test_obj)
        mock_response = MagicMock(headers={'Location': '/api/v1/resource-manager/lifecycle-drivers/123'})
        self.mock_client.make_request.return_value = mock_response
        response = self.resource_drivers.create(test_obj)
        self.assertEqual(response, {'id': '123', 'type': 'Ansible'})
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/v1/resource-manager/lifecycle-drivers', headers={'Content-Type': 'application/json'}, body=body))

    def test_delete(self):
        response = self.resource_drivers.delete('123')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='DELETE', endpoint='api/v1/resource-manager/lifecycle-drivers/123'))
    

