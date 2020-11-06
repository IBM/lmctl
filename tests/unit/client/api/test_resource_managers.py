import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import ResourceManagersAPI

class TestResourceManagersAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.resource_managers = ResourceManagersAPI(self.mock_client)

    def test_all(self):
        all_objects = [{'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = all_objects
        response = self.resource_managers.all()
        self.assertEqual(response, all_objects)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/resource-managers')

    def test_get(self):
        mock_response = {'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.resource_managers.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/resource-managers/Test')

    def test_create(self):
        test_obj = {'name': 'Test'}
        mock_response = MagicMock(headers={'Location': '/api/resource-managers/123'})
        mock_onboarding_report = {'resourceManagerOperation': 'ADD'}
        mock_response.json.return_value = mock_onboarding_report
        self.mock_client.make_request.return_value = mock_response
        response = self.resource_managers.create(test_obj)
        self.assertEqual(response, mock_onboarding_report)
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/resource-managers', json=test_obj)

    def test_update(self):
        test_obj = {'name': 'Test'}
        mock_onboarding_report = {'resourceManagerOperation': 'UPDATE'}
        self.mock_client.make_request.return_value.json.return_value = mock_onboarding_report
        response = self.resource_managers.update(test_obj)
        self.assertEqual(response, mock_onboarding_report)
        self.mock_client.make_request.assert_called_with(method='PUT', endpoint='api/resource-managers/Test', json=test_obj)

    def test_delete(self):
        response = self.resource_managers.delete('Test')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='DELETE', endpoint='api/resource-managers/Test')
    

