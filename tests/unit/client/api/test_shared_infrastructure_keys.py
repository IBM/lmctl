import unittest
import json
from unittest.mock import patch, MagicMock
from lmctl.client.api import SharedInfrastructureKeysAPI
from lmctl.client.client_request import TNCOClientRequest

class TestSharedInfrastructureKeysAPI(unittest.TestCase):
    apiendpoint='api/v1'
    
    def setUp(self):
        self.mock_client = MagicMock()
        self.inf_keys = SharedInfrastructureKeysAPI(self.mock_client)

    def test_all(self):
        all_objects = [{'id': 'Test', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = all_objects
        response = self.inf_keys.all()
        self.assertEqual(response, all_objects)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='self.apiendpoint + '/resource-manager/infrastructure-keys/shared'))

    def test_get(self):
        mock_response = {'id': 'Test', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.inf_keys.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='self.apiendpoint + '/resource-manager/infrastructure-keys/shared/Test'))

    def test_create(self):
        test_obj = {'name': 'Test'}
        body = json.dumps(test_obj)
        mock_response = MagicMock(headers={'Location': '/self.apiendpoint + '/resource-manager/infrastructure-keys/shared/Test'})
        self.mock_client.make_request.return_value = mock_response
        response = self.inf_keys.create(test_obj)
        self.assertEqual(response, {'name': 'Test'})
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='self.apiendpoint + '/resource-manager/infrastructure-keys/shared', headers={'Content-Type': 'application/json'}, body=body))

    def test_update(self):
        test_obj = {'id': '123', 'name': 'Test'}
        body = json.dumps(test_obj)
        response = self.inf_keys.update(test_obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='PUT', endpoint='self.apiendpoint + '/resource-manager/infrastructure-keys/shared/Test', headers={'Content-Type': 'application/json'}, body=body))

    def test_delete(self):
        response = self.inf_keys.delete('Test')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='DELETE', endpoint='self.apiendpoint + '/resource-manager/infrastructure-keys/shared/Test'))
    

