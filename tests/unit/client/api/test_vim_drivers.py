import unittest
import json
from unittest.mock import patch, MagicMock
from lmctl.client.api import VIMDriversAPI
from lmctl.client.client_request import TNCOClientRequest

class TestVIMDriversAPI(unittest.TestCase):
    apiendpoint='api/v1'
    
    def setUp(self):
        self.mock_client = MagicMock()
        self.resource_drivers = VIMDriversAPI(self.mock_client)

    def test_get(self):
        mock_response = {'id': 'Test', 'type': 'Openstack'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.resource_drivers.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint=self.apiendpoint + '/resource-manager/vim-drivers/Test'))
    
    def test_get_by_type(self):
        mock_response = {'id': 'Test', 'type': 'Openstack'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.resource_drivers.get_by_type('Openstack')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint=self.apiendpoint + '/resource-manager/vim-drivers', query_params={'type': 'Openstack'}))

    def test_create(self):
        test_obj = {'type': 'Openstack'}
        body = json.dumps(test_obj)
        mock_response = MagicMock(headers={'Location': self.apiendpoint + '/resource-manager/vim-drivers/123'})
        self.mock_client.make_request.return_value = mock_response
        response = self.resource_drivers.create(test_obj)
        self.assertEqual(response, {'id': '123', 'type': 'Openstack'})
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint=self.apiendpoint + '/resource-manager/vim-drivers', headers={'Content-Type': 'application/json'}, body=body))

    def test_delete(self):
        response = self.resource_drivers.delete('123')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='DELETE', endpoint=self.apiendpoint + '/resource-manager/vim-drivers/123'))
    

