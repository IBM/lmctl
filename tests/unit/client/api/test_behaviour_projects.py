import unittest
import json
from unittest.mock import patch, MagicMock
from lmctl.client.api import BehaviourProjectsAPI
from lmctl.client.client_request import TNCOClientRequest

class TestBehaviourProjectsAPI(unittest.TestCase):
    
    behaviourendpoint='api/v1'
    
    def setUp(self):
        self.mock_client = MagicMock()
        self.behaviour_projects = BehaviourProjectsAPI(self.mock_client)

    def test_all(self):
        all_objects = [{'id': 'Test', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = all_objects
        response = self.behaviour_projects.all()
        self.assertEqual(response, all_objects)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint=self.behaviourendpoint + '/behaviour/projects'))

    def test_get(self):
        mock_response = {'id': 'Test', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.behaviour_projects.get('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint=self.behaviourendpoint + '/behaviour/projects/Test'))

    def test_create(self):
        test_obj = {'name': 'Test'}
        body = json.dumps(test_obj)
        mock_response = MagicMock(headers={'Location': self.behaviourendpoint + '/behaviour/projects/123'})
        self.mock_client.make_request.return_value = mock_response
        response = self.behaviour_projects.create(test_obj)
        self.assertEqual(response, {'id': '123', 'name': 'Test'})
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint=self.behaviourendpoint + '/behaviour/projects', headers={'Content-Type': 'application/json'}, body=body))

    def test_update(self):
        test_obj = {'id': '123', 'name': 'Test'}
        body = json.dumps(test_obj)
        response = self.behaviour_projects.update(test_obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='PUT', endpoint=self.behaviourendpoint + '/behaviour/projects/123', headers={'Content-Type': 'application/json'}, body=body))

    def test_delete(self):
        response = self.behaviour_projects.delete('123')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='DELETE', endpoint=self.behaviourendpoint + '/behaviour/projects/123'))
    

