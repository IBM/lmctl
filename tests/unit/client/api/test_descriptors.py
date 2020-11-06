import unittest
import yaml
from unittest.mock import patch, MagicMock
from lmctl.client.api import DescriptorsAPI

class TestDescriptorsAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.descriptors = DescriptorsAPI(self.mock_client)

    def test_all(self):
        mock_response = '- name: assembly::Test::1.0'
        self.mock_client.make_request.return_value = MagicMock(text=mock_response)
        response = self.descriptors.all()
        self.assertEqual(response, [{'name': 'assembly::Test::1.0'}])
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/catalog/descriptors', headers={'Accept': 'application/yaml,application/json'})

    def test_get(self):
        mock_response = 'name: assembly::Test::1.0'
        self.mock_client.make_request.return_value = MagicMock(text=mock_response)
        response = self.descriptors.get('assembly::Test::1.0')
        self.assertEqual(response, {'name': 'assembly::Test::1.0'})
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/catalog/descriptors/assembly::Test::1.0', headers={'Accept': 'application/yaml,application/json'})

    def test_create(self):
        obj = {'name': 'assembly::Test::1.0'}
        response = self.descriptors.create(obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/catalog/descriptors', data=yaml.safe_dump(obj), headers={'Content-Type': 'application/yaml'})

    def test_update(self):
        obj = {'name': 'assembly::Test::1.0'}
        response = self.descriptors.update(obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='PUT', endpoint='api/catalog/descriptors/assembly::Test::1.0', data=yaml.safe_dump(obj), headers={'Content-Type': 'application/yaml'})

    def test_delete(self):
        response = self.descriptors.delete('assembly::Test::1.0')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='DELETE', endpoint='api/catalog/descriptors/assembly::Test::1.0')
    

