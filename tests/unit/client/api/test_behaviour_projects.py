import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import BehaviourProjectsAPI

class TestBehaviourProjectsAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.behaviour_projects = BehaviourProjectsAPI(self.mock_client)

    def test_all(self):
        all_objects = [{'id': 'Test', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = all_objects
        response = self.behaviour_projects.all()
        self.assertEqual(response, all_objects)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/projects')

    def test_get(self):
        mock_response = {'id': 'Test', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_projects.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/behaviour/projects/Test')

    def test_create(self):
        test_obj = {'name': 'Test'}
        mock_response = MagicMock(headers={'Location': '/api/behaviour/projects/123'})
        self.mock_client.make_request.return_value = mock_response
        response = self.behaviour_projects.create(test_obj)
        self.assertEqual(response, {'id': '123', 'name': 'Test'})
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/behaviour/projects', json=test_obj)

    def test_update(self):
        test_obj = {'id': '123', 'name': 'Test'}
        response = self.behaviour_projects.update(test_obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='PUT', endpoint='api/behaviour/projects/123', json=test_obj)

    def test_delete(self):
        response = self.behaviour_projects.delete('123')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='DELETE', endpoint='api/behaviour/projects/123')
    

