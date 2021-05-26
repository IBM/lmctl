import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import ProcessesAPI
from lmctl.client.client_request import TNCOClientRequest

class TestProcessesAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.processes = ProcessesAPI(self.mock_client)

    def test_get(self):
        mock_response = {'id': '123'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.processes.get('123')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/processes/123'))

    def test_get_shallow(self):
        mock_response = {'id': '123'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.processes.get('123', shallow=True)
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/processes/123', query_params={'shallow': True}))

    def test_query(self):
        mock_response = [{'id': '123'}, {'id': '456'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.processes.query(assemblyName='Abc', intentTypes='healAssembly')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/processes', query_params={'assemblyName': 'Abc', 'intentTypes': 'healAssembly'}))
