import unittest
import yaml
from unittest.mock import patch, MagicMock
from lmctl.client.api import DescriptorsAPI
from lmctl.client.client_request import TNCOClientRequest

class TestDescriptorsAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.descriptors = DescriptorsAPI(self.mock_client)

    def test_all(self):
        mock_response = '- name: assembly::Test::1.0'
        self.mock_client.make_request.return_value = MagicMock(text=mock_response)
        response = self.descriptors.all()
        self.assertEqual(response, [{'name': 'assembly::Test::1.0'}])
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='GET', endpoint='api/v1/catalog/descriptors', headers={'Accept': 'application/yaml,application/json'}))

    def test_get(self):
        mock_response = 'name: assembly::Test::1.0'
        self.mock_client.make_request.return_value = MagicMock(text=mock_response)
        response = self.descriptors.get('assembly::Test::1.0')
        self.assertEqual(response, {'name': 'assembly::Test::1.0'})
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='GET', endpoint='api/v1/catalog/descriptors/assembly::Test::1.0', headers={'Accept': 'application/yaml,application/json'}))

    def test_get_effective(self):
        mock_response = 'name: assembly::Test::1.0'
        self.mock_client.make_request.return_value = MagicMock(text=mock_response)
        response = self.descriptors.get('assembly::Test::1.0', effective=True)
        self.assertEqual(response, {'name': 'assembly::Test::1.0'})
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='GET', endpoint='api/v1/catalog/descriptors/assembly::Test::1.0', query_params={'effective': True}, headers={'Accept': 'application/yaml,application/json'}))

    def test_create(self):
        obj = {'name': 'assembly::Test::1.0'}
        response = self.descriptors.create(obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/v1/catalog/descriptors', body=yaml.safe_dump(obj), headers={'Content-Type': 'application/yaml'}))

    def test_update(self):
        obj = {'name': 'assembly::Test::1.0'}
        response = self.descriptors.update(obj)
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='PUT', endpoint='api/v1/catalog/descriptors/assembly::Test::1.0', body=yaml.safe_dump(obj), headers={'Content-Type': 'application/yaml'}))

    def test_delete(self):
        response = self.descriptors.delete('assembly::Test::1.0')
        self.assertIsNone(response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='DELETE', endpoint='api/v1/catalog/descriptors/assembly::Test::1.0'))
    

