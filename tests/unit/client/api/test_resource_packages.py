import unittest
from unittest.mock import patch, MagicMock, mock_open
from lmctl.client.api import ResourcePackagesAPI
from lmctl.client.client_request import TNCOClientRequest

class TestResourcePackagesAPI(unittest.TestCase):
    apiendpoint='api/v1'
    
    def setUp(self):
        self.mock_client = MagicMock()
        self.resource_packages = ResourcePackagesAPI(self.mock_client)

    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_create(self, mock_file):
        mock_response = MagicMock(headers={'Location': '/self.apiendpoint + '/resource-manager/resource-packages/123'})
        self.mock_client.make_request.return_value = mock_response
        response = self.resource_packages.create('/some/test/file')
        self.assertEqual(response, '123')
        mock_file.assert_called_with('/some/test/file', 'rb')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='self.apiendpoint + '/resource-manager/resource-packages', files={'file': mock_file.return_value}))
    
    @patch("builtins.open", new_callable=mock_open, read_data="data")
    def test_update(self, mock_file):
        response = self.resource_packages.update('Test', '/some/test/file')
        self.assertIsNone(response)
        mock_file.assert_called_with('/some/test/file', 'rb')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='PUT', endpoint='self.apiendpoint + '/resource-manager/resource-packages/Test', files={'file': mock_file.return_value}))
   
    def test_delete(self):
        response = self.resource_packages.delete('Test')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='DELETE', endpoint='self.apiendpoint + '/resource-manager/resource-packages/Test'))
    