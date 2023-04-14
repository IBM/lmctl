import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import ObjectgroupsAPI
from lmctl.client.client_request import TNCOClientRequest

class TestObjectgroupsAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.objectgroups = ObjectgroupsAPI(self.mock_client)

    def test_get(self):
        mock_response = [{'id': '59799459-0067-4901-8265-a173196d3928', 'name': 'Domain1', 'description': 'Orchestration for Domain 1', 'isDefault': False}, {'id': 'b01844f2-3446-494f-84a9-37441ae4829c', 'name': 'Mahesh', 'description': 'Orchestration for Domain Mahesh', 'isDefault': False}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.objectgroups.get('59799459-0067-4901-8265-a173196d3928')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/v1/object-groups/59799459-0067-4901-8265-a173196d3928'))

    def test_get_shallow(self):
        mock_response = {'id': '123'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.objectgroups.get('59799459-0067-4901-8265-a173196d3928', shallow=True)
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/v1/object-groups/59799459-0067-4901-8265-a173196d3928', query_params={'shallow': True}))

    def test_query(self):
        mock_response = [{'id': '59799459-0067-4901-8265-a173196d3928', 'name': 'Domain1', 'description': 'Orchestration for Domain 1', 'isDefault': False}, {'id': 'b01844f2-3446-494f-84a9-37441ae4829c', 'name': 'Mahesh', 'description': 'Orchestration for Domain Mahesh', 'isDefault': False}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.objectgroups.query(id='59799459-0067-4901-8265-a173196d3928')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/v1/object-groups', query_params={'id': '59799459-0067-4901-8265-a173196d3928'}))
