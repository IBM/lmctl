import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import SharedInfrastructureKeysAPI

class TestSharedInfrastructureKeysAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.inf_keys = SharedInfrastructureKeysAPI(self.mock_client)

    def test_all(self):
        all_objects = [{'id': 'Test', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = all_objects
        response = self.inf_keys.all()
        self.assertEqual(response, all_objects)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/resource-manager/infrastructure-keys/shared')

    def test_get(self):
        mock_response = {'id': 'Test', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.inf_keys.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/resource-manager/infrastructure-keys/shared/Test')

    def test_create(self):
        test_obj = {'name': 'Test'}
        mock_response = MagicMock(headers={'Location': '/api/resource-manager/infrastructure-keys/shared/Test'})
        self.mock_client.make_request.return_value = mock_response
        response = self.inf_keys.create(test_obj)
        self.assertEqual(response, {'name': 'Test'})
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/resource-manager/infrastructure-keys/shared', json=test_obj)

    def test_update(self):
        test_obj = {'id': '123', 'name': 'Test'}
        response = self.inf_keys.update(test_obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='PUT', endpoint='api/resource-manager/infrastructure-keys/shared/Test', json=test_obj)

    def test_delete(self):
        response = self.inf_keys.delete('Test')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='DELETE', endpoint='api/resource-manager/infrastructure-keys/shared/Test')
    

