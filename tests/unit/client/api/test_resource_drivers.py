import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import ResourceDriversAPI

class TestResourceDriversAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.resource_drivers = ResourceDriversAPI(self.mock_client)

    def test_get(self):
        mock_response = {'id': 'Test', 'type': 'Kubernetes'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.resource_drivers.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/resource-manager/resource-drivers/Test')
    
    def test_get_by_type(self):
        mock_response = {'id': 'Test', 'type': 'Kubernetes'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.resource_drivers.get_by_type('Kubernetes')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/resource-manager/resource-drivers?type=Kubernetes')

    def test_create(self):
        test_obj = {'type': 'Kubernetes'}
        mock_response = MagicMock(headers={'Location': '/api/resource-manager/resource-drivers/123'})
        self.mock_client.make_request.return_value = mock_response
        response = self.resource_drivers.create(test_obj)
        self.assertEqual(response, {'id': '123', 'type': 'Kubernetes'})
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/resource-manager/resource-drivers', json=test_obj)

    def test_delete(self):
        response = self.resource_drivers.delete('123')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='DELETE', endpoint='api/resource-manager/resource-drivers/123')
    

