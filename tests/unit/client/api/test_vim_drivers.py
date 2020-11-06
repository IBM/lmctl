import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import VIMDriversAPI

class TestVIMDriversAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.resource_drivers = VIMDriversAPI(self.mock_client)

    def test_get(self):
        mock_response = {'id': 'Test', 'type': 'Openstack'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.resource_drivers.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/resource-manager/vim-drivers/Test')
    
    def test_get_by_type(self):
        mock_response = {'id': 'Test', 'type': 'Openstack'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.resource_drivers.get_by_type('Openstack')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/resource-manager/vim-drivers?type=Openstack')

    def test_create(self):
        test_obj = {'type': 'Openstack'}
        mock_response = MagicMock(headers={'Location': '/api/resource-manager/vim-drivers/123'})
        self.mock_client.make_request.return_value = mock_response
        response = self.resource_drivers.create(test_obj)
        self.assertEqual(response, {'id': '123', 'type': 'Openstack'})
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/resource-manager/vim-drivers', json=test_obj)

    def test_delete(self):
        response = self.resource_drivers.delete('123')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='DELETE', endpoint='api/resource-manager/vim-drivers/123')
    

