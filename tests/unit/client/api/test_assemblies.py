import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.api import AssembliesAPI
from lmctl.client.models import (CreateAssemblyIntent, UpgradeAssemblyIntent, ChangeAssemblyStateIntent, 
                                    DeleteAssemblyIntent, ScaleAssemblyIntent, HealAssemblyIntent,
                                    AdoptAssemblyIntent, CreateOrUpgradeAssemblyIntent)

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
    
    def test_get_by_name(self):
        mock_response = [{'id': '123', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.assemblies.get_by_name('Test')
        self.assertEqual(response, mock_response[0])
        self.mock_client.make_request.assert_called_with(method='GET', endpoint='api/topology/assemblies?name=Test')
   
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

    def test_intent(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'descriptorName': 'assembly::Test::1.0', 'assemblyName': 'Test', 'intendedState': 'Active'}
        response = self.assemblies.intent('createAssembly', intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/createAssembly', json=intent)
    
    def test_intent_create(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = CreateAssemblyIntent(descriptor_name='assembly::Test::1.0', assembly_name='Test', intended_state='Active') 
        response = self.assemblies.intent_create(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', 
                                                            endpoint='api/intent/createAssembly', 
                                                            json={
                                                                'descriptorName': 'assembly::Test::1.0', 
                                                                'assemblyName': 'Test', 
                                                                'intendedState': 'Active',
                                                                'properties': {}
                                                            })

    def test_intent_create_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'descriptorName': 'assembly::Test::1.0', 'assemblyName': 'Test', 'intendedState': 'Active'}
        response = self.assemblies.intent_create(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/createAssembly', json=intent)
    
    def test_intent_create_or_upgrade(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = CreateOrUpgradeAssemblyIntent(descriptor_name='assembly::Test::1.0', assembly_name='Test', intended_state='Active',
            tags={
                'tag1': 'value1',
                'tag2': 'value2'
            },
            properties={
                'prop1': 'val1',
                'prop2': 'val2'
            })
        response = self.assemblies.intent_create_or_upgrade(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', 
                                                            endpoint='api/intent/createOrUpgradeAssembly', 
                                                            json={
                                                                'assemblyName': 'Test', 
                                                                'descriptorName': 'assembly::Test::1.0', 
                                                                'properties': {
                                                                    'prop1': 'val1',
                                                                    'prop2': 'val2'
                                                                },
                                                                'tags': {
                                                                    'tag1': 'value1',
                                                                    'tag2': 'value2'
                                                                },
                                                                'intendedState': 'Active',
                                                            })

    def test_intent_upgrade(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = UpgradeAssemblyIntent(assembly_name='Test', descriptor_name='assembly::Test::1.0', intended_state='Active')
        response = self.assemblies.intent_upgrade(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', 
                                                            endpoint='api/intent/upgradeAssembly', 
                                                            json={
                                                                'descriptorName': 'assembly::Test::1.0', 
                                                                'assemblyName': 'Test', 
                                                                'intendedState': 'Active',
                                                                'properties': {}
                                                            })

    def test_intent_upgrade_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'descriptorName': 'assembly::Test::1.0', 'assemblyName': 'Test', 'intendedState': 'Active'}
        response = self.assemblies.intent_upgrade(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/upgradeAssembly', json=intent)
    
    def test_intent_delete(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = DeleteAssemblyIntent(assembly_name='Test')
        response = self.assemblies.intent_delete(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/deleteAssembly', json={'assemblyName': 'Test'})
    
    def test_intent_delete_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test'}
        response = self.assemblies.intent_delete(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/deleteAssembly', json=intent)
    
    def test_intent_change_state(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = ChangeAssemblyStateIntent(assembly_name='Test', intended_state='Active')
        response = self.assemblies.intent_change_state(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/changeAssemblyState', json={'assemblyName': 'Test', 'intendedState': 'Active'})
    
    def test_intent_change_state_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test', 'intendedState': 'Active'}
        response = self.assemblies.intent_change_state(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/changeAssemblyState', json=intent)
    
    def test_intent_scale_out(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = ScaleAssemblyIntent(assembly_name='Test', cluster_name='A')
        response = self.assemblies.intent_scale_out(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/scaleOutAssembly', json={'assemblyName': 'Test', 'clusterName': 'A'})

    def test_intent_scale_out_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test', 'clusterName': 'A'}
        response = self.assemblies.intent_scale_out(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/scaleOutAssembly', json=intent)
    
    def test_intent_scale_in(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = ScaleAssemblyIntent(assembly_name='Test', cluster_name='A')
        response = self.assemblies.intent_scale_in(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/scaleInAssembly', json={'assemblyName': 'Test', 'clusterName': 'A'})

    def test_intent_scale_in_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test', 'clusterName': 'A'}
        response = self.assemblies.intent_scale_in(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/scaleInAssembly', json=intent)
    
    def test_intent_heal(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = HealAssemblyIntent(assembly_name='Test', broken_component_name='A')
        response = self.assemblies.intent_heal(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/healAssembly', json={'assemblyName': 'Test', 'brokenComponentName': 'A'})
    
    def test_intent_heal_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test', 'brokenComponentName': 'A'}
        response = self.assemblies.intent_heal(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/healAssembly', json=intent)
    
    def test_intent_adopt(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = AdoptAssemblyIntent(assembly_name='Test', descriptor_name='assembly::Test::1.0', clusters={'B': 1})
        response = self.assemblies.intent_adopt(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', 
                                                        endpoint='api/intent/adoptAssembly', 
                                                        json={
                                                            'assemblyName': 'Test',
                                                            'descriptorName': 'assembly::Test::1.0',
                                                            'clusters': {'B': 1},
                                                            'properties': {}
                                                        })
    
    def test_intent_adopt_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test', 'descriptorName': 'assembly::Test::1.0', 'clusters': {'B': 1}}
        response = self.assemblies.intent_adopt(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(method='POST', endpoint='api/intent/adoptAssembly', json=intent)
