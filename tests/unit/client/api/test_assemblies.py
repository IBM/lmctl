import unittest
import json
from unittest.mock import patch, MagicMock
from lmctl.client.api import AssembliesAPI
from lmctl.client.models import (CreateAssemblyIntent, UpgradeAssemblyIntent, ChangeAssemblyStateIntent, 
                                    DeleteAssemblyIntent, ScaleAssemblyIntent, HealAssemblyIntent,
                                    AdoptAssemblyIntent, CreateOrUpgradeAssemblyIntent, CancelAssemblyIntent,
                                    RetryAssemblyIntent, RollbackAssemblyIntent)
from lmctl.client.client_request import TNCOClientRequest

class TestAssembliesAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.assemblies = AssembliesAPI(self.mock_client)

    def test_get(self):
        mock_response = {'id': '123', 'name': 'Test'}
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.assemblies.get('123')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/topology/assemblies/123'))
    
    def test_get_by_name(self):
        mock_response = [{'id': '123', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.assemblies.get_by_name('Test')
        self.assertEqual(response, mock_response[0])
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/topology/assemblies', query_params={'name': 'Test'}))
   
    def test_get_topN(self):
        mock_response = [{'id': '123', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.assemblies.get_topN()
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/topology/assemblies'))
    
    def test_all_with_name(self):
        mock_response = [{'id': '123', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.assemblies.all_with_name('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/topology/assemblies', query_params={'name': 'Test'}))
   
    def test_all_with_name_containing(self):
        mock_response = [{'id': '123', 'name': 'Test'}]
        self.mock_client.make_request.return_value.json.return_value = mock_response
        response = self.assemblies.all_with_name_containing('Test')
        self.assertEqual(response, mock_response)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest.build_request_for_json(method='GET', endpoint='api/topology/assemblies', query_params={'nameContains': 'Test'}))

    def test_intent(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'descriptorName': 'assembly::Test::1.0', 'assemblyName': 'Test', 'intendedState': 'Active'}
        response = self.assemblies.intent('createAssembly', intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/createAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps(intent)))
    
    def test_intent_create(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = CreateAssemblyIntent(descriptor_name='assembly::Test::1.0', assembly_name='Test', intended_state='Active') 
        response = self.assemblies.intent_create(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', 
                                                            endpoint='api/intent/createAssembly', 
                                                            headers={'Content-Type': 'application/json'}, 
                                                            body=json.dumps({
                                                                'assemblyName': 'Test', 
                                                                'descriptorName': 'assembly::Test::1.0', 
                                                                'properties': {},
                                                                'intendedState': 'Active'
                                                            })))

    def test_intent_create_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'descriptorName': 'assembly::Test::1.0', 'assemblyName': 'Test', 'intendedState': 'Active'}
        response = self.assemblies.intent_create(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/createAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps(intent)))
    
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
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', 
                                                            endpoint='api/intent/createOrUpgradeAssembly', 
                                                            headers={'Content-Type': 'application/json'}, 
                                                            body=json.dumps({
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
                                                            })))

    def test_intent_upgrade(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = UpgradeAssemblyIntent(assembly_name='Test', descriptor_name='assembly::Test::1.0', intended_state='Active')
        response = self.assemblies.intent_upgrade(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', 
                                                            endpoint='api/intent/upgradeAssembly',
                                                            headers={'Content-Type': 'application/json'},  
                                                            body=json.dumps({
                                                                'assemblyName': 'Test', 
                                                                'descriptorName': 'assembly::Test::1.0', 
                                                                'properties': {},
                                                                'intendedState': 'Active'
                                                            })))

    def test_intent_upgrade_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'descriptorName': 'assembly::Test::1.0', 'assemblyName': 'Test', 'intendedState': 'Active'}
        response = self.assemblies.intent_upgrade(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/upgradeAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps(intent)))
    
    def test_intent_delete(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = DeleteAssemblyIntent(assembly_name='Test')
        response = self.assemblies.intent_delete(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/deleteAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps({'assemblyName': 'Test'})))
    
    def test_intent_delete_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test'}
        response = self.assemblies.intent_delete(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/deleteAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps(intent)))
    
    def test_intent_change_state(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = ChangeAssemblyStateIntent(assembly_name='Test', intended_state='Active')
        response = self.assemblies.intent_change_state(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/changeAssemblyState', headers={'Content-Type': 'application/json'}, body=json.dumps({'assemblyName': 'Test', 'intendedState': 'Active'})))
    
    def test_intent_change_state_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test', 'intendedState': 'Active'}
        response = self.assemblies.intent_change_state(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/changeAssemblyState', headers={'Content-Type': 'application/json'}, body=json.dumps(intent)))
    
    def test_intent_scale_out(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = ScaleAssemblyIntent(assembly_name='Test', cluster_name='A')
        response = self.assemblies.intent_scale_out(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/scaleOutAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps({'assemblyName': 'Test', 'clusterName': 'A'})))

    def test_intent_scale_out_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test', 'clusterName': 'A'}
        response = self.assemblies.intent_scale_out(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/scaleOutAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps(intent)))
    
    def test_intent_scale_in(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = ScaleAssemblyIntent(assembly_name='Test', cluster_name='A')
        response = self.assemblies.intent_scale_in(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/scaleInAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps({'assemblyName': 'Test', 'clusterName': 'A'})))

    def test_intent_scale_in_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test', 'clusterName': 'A'}
        response = self.assemblies.intent_scale_in(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/scaleInAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps(intent)))
    
    def test_intent_heal(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = HealAssemblyIntent(assembly_name='Test', broken_component_name='A')
        response = self.assemblies.intent_heal(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/healAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps({'assemblyName': 'Test', 'brokenComponentName': 'A'})))
    
    def test_intent_heal_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test', 'brokenComponentName': 'A'}
        response = self.assemblies.intent_heal(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/healAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps(intent)))
    
    def test_intent_adopt(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = AdoptAssemblyIntent(assembly_name='Test', descriptor_name='assembly::Test::1.0', clusters={'B': 1})
        response = self.assemblies.intent_adopt(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', 
                                                        endpoint='api/intent/adoptAssembly', 
                                                        headers={'Content-Type': 'application/json'}, 
                                                        body=json.dumps({
                                                            'assemblyName': 'Test',
                                                            'descriptorName': 'assembly::Test::1.0',
                                                            'properties': {},
                                                            'clusters': {'B': 1,}
                                                        })))
    
    def test_intent_adopt_with_dict(self):
        mock_response = MagicMock(headers={'Location': '/api/processes/123'})
        self.mock_client.make_request.return_value = mock_response
        intent = {'assemblyName': 'Test', 'descriptorName': 'assembly::Test::1.0', 'clusters': {'B': 1}}
        response = self.assemblies.intent_adopt(intent)
        self.assertEqual(response, '123')
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST', endpoint='api/intent/adoptAssembly', headers={'Content-Type': 'application/json'}, body=json.dumps(intent)))

    def test_intent_cancel(self):
        mock_response = MagicMock(status_code=200)
        self.mock_client.make_request.return_value = mock_response
        intent = CancelAssemblyIntent(process_id='8475f402-cb6f-4ef1-a379-77c7e20cdf72')
        response = self.assemblies.intent_cancel(intent)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST',
                                                        endpoint='api/intent/cancel',
                                                        headers={'Content-Type': 'application/json'},
                                                        body=json.dumps({
                                                            'process_id': '8475f402-cb6f-4ef1-a379-77c7e20cdf72'
                                                        })))

    def test_intent_cancel_with_dict(self):
        mock_response = MagicMock(status_code=200)
        self.mock_client.make_request.return_value = mock_response
        intent = {'process_id' : '8475f402-cb6f-4ef1-a379-77c7e20cdf72'}
        response = self.assemblies.intent_cancel(intent)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST',
                                                        endpoint='api/intent/cancel',
                                                        headers={'Content-Type': 'application/json'},
                                                        body=json.dumps({
                                                            'process_id': '8475f402-cb6f-4ef1-a379-77c7e20cdf72'
                                                        })))

    def test_intent_retry(self):
        mock_response = MagicMock(status_code=200)
        self.mock_client.make_request.return_value = mock_response
        intent = RetryAssemblyIntent(process_id='8475f402-cb6f-4ef1-a379-77c7e20cdf72')
        response = self.assemblies.intent_retry(intent)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST',
                                                        endpoint='api/intent/retry',
                                                        headers={'Content-Type': 'application/json'},
                                                        body=json.dumps({
                                                            'process_id': '8475f402-cb6f-4ef1-a379-77c7e20cdf72'
                                                        })))

    def test_intent_retry_with_dict(self):
        mock_response = MagicMock(status_code=200)
        self.mock_client.make_request.return_value = mock_response
        intent = {'process_id' : '8475f402-cb6f-4ef1-a379-77c7e20cdf72'}
        response = self.assemblies.intent_retry(intent)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST',
                                                        endpoint='api/intent/retry',
                                                        headers={'Content-Type': 'application/json'},
                                                        body=json.dumps({
                                                            'process_id': '8475f402-cb6f-4ef1-a379-77c7e20cdf72'
                                                        })))

    def test_intent_rollback(self):
        mock_response = MagicMock(status_code=200)
        self.mock_client.make_request.return_value = mock_response
        intent = RollbackAssemblyIntent(process_id='8475f402-cb6f-4ef1-a379-77c7e20cdf72')
        response = self.assemblies.intent_rollback(intent)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST',
                                                        endpoint='api/intent/rollback',
                                                        headers={'Content-Type': 'application/json'},
                                                        body=json.dumps({
                                                            'process_id': '8475f402-cb6f-4ef1-a379-77c7e20cdf72'
                                                        })))

    def test_intent_rollback_with_dict(self):
        mock_response = MagicMock(status_code=200)
        self.mock_client.make_request.return_value = mock_response
        intent = {'process_id' : '8475f402-cb6f-4ef1-a379-77c7e20cdf72'}
        response = self.assemblies.intent_rollback(intent)
        self.mock_client.make_request.assert_called_with(TNCOClientRequest(method='POST',
                                                        endpoint='api/intent/rollback',
                                                        headers={'Content-Type': 'application/json'},
                                                        body=json.dumps({
                                                            'process_id': '8475f402-cb6f-4ef1-a379-77c7e20cdf72'
                                                        })))