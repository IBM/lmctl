import unittest
import yaml
from unittest.mock import patch, MagicMock
from lmctl.client.api import DescriptorTemplatesAPI

class TestDescriptorTemplatesAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.descriptor_templates = DescriptorTemplatesAPI(self.mock_client)

    def test_all(self):
        mock_response = '- name: assembly-template::Test::1.0'
        self.mock_client.make_request.return_value = MagicMock(text=mock_response)
        response = self.descriptor_templates.all()
        self.assertEqual(response, [{'name': 'assembly-template::Test::1.0'}])
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/catalog/descriptorTemplates', headers={'Accept': 'application/yaml,application/json'})

    def test_get(self):
        mock_response = 'name: assembly-template::Test::1.0'
        self.mock_client.make_request.return_value = MagicMock(text=mock_response)
        response = self.descriptor_templates.get('assembly-template::Test::1.0')
        self.assertEqual(response, {'name': 'assembly-template::Test::1.0'})
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/catalog/descriptorTemplates/assembly-template::Test::1.0', headers={'Accept': 'application/yaml,application/json'})

    def test_create(self):
        obj = {'name': 'assembly-template::Test::1.0'}
        response = self.descriptor_templates.create(obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/catalog/descriptorTemplates', data=yaml.safe_dump(obj), headers={'Content-Type': 'application/yaml'})

    def test_update(self):
        obj = {'name': 'assembly-template::Test::1.0'}
        response = self.descriptor_templates.update(obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='PUT', endpoint='api/catalog/descriptorTemplates/assembly-template::Test::1.0', data=yaml.safe_dump(obj), headers={'Content-Type': 'application/yaml'})

    def test_delete(self):
        response = self.descriptor_templates.delete('assembly-template::Test::1.0')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(method='DELETE', endpoint='api/catalog/descriptorTemplates/assembly-template::Test::1.0')
    

