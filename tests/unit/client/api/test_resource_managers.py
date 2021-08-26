import unittest
import json
from unittest.mock import patch, MagicMock
from lmctl.client.api import ResourceManagersAPI
from lmctl.client.client_request import TNCOClientRequest

class TestResourceManagersAPI(unittest.TestCase):
    apiendpoint='api/v1'
    
    def setUp(self):
        self.mock_client = MagicMock()
        self.resource_managers = ResourceManagersAPI(self.mock_client)

    def test_all(self):
        all_objects = [{'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = all_objects
        response = self.resource_managers.all()
        self.assertEqual(response, all_objects)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint=self.apiendpoint + '/resource-managers'))

    def test_get(self):
        mock_response = {'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.resource_managers.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint=self.apiendpoint + '/resource-managers/Test'))

    def test_create(self):
        test_obj = {'name': 'Test'}
        body = json.dumps(test_obj)
        mock_response = MagicMock(headers={'Location': self.apiendpoint + '/resource-managers/123'})
        mock_onboarding_report = {'resourceManagerOperation': 'ADD'}
        mock_response.json.return_value = mock_onboarding_report
        self.mock_client.make_request.return_value = mock_response
        response = self.resource_managers.create(test_obj)
        self.assertEqual(response, mock_onboarding_report)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint=self.apiendpoint + '/resource-managers', headers={'Content-Type': 'application/json'}, body=body))

    def test_update(self):
        test_obj = {'name': 'Test'}
        body = json.dumps(test_obj)
        mock_onboarding_report = {'resourceManagerOperation': 'UPDATE'}
        self.mock_client.make_request.return_value.json.return_value = mock_onboarding_report
        response = self.resource_managers.update(test_obj)
        self.assertEqual(response, mock_onboarding_report)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='PUT', endpoint=self.apiendpoint + '/resource-managers/Test', headers={'Content-Type': 'application/json'}, body=body))

    def test_delete(self):
        response = self.resource_managers.delete('Test')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='DELETE', endpoint=self.apiendpoint + '/resource-managers/Test'))
    

