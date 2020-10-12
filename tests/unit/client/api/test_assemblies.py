import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import AssembliesAPI

class TestAssembliesAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.assemblies = AssembliesAPI(self.mock_client)

    def test_get(self):
        mock_response = {'id': '123', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.assemblies.get('123')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/topology/assemblies/123')
    
    def test_get_topN(self):
        mock_response = [{'id': '123', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.assemblies.get_topN()
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/topology/assemblies')
    
    def test_all_with_name(self):
        mock_response = [{'id': '123', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.assemblies.all_with_name('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/topology/assemblies?name=Test')
   
    def test_all_with_name_containing(self):
        mock_response = [{'id': '123', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.assemblies.all_with_name_containing('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/topology/assemblies?nameContains=Test')
    