import os
import time
from typing import Dict, Any
from tests.integration.integration_test_base import IntegrationTest
from lmctl.client.models import (CreateAssemblyIntent, UpgradeAssemblyIntent, ChangeAssemblyStateIntent, 
                                    DeleteAssemblyIntent, ScaleAssemblyIntent, HealAssemblyIntent,
                                    AdoptAssemblyIntent)

class TestAssembliesAPI(IntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add deployment location
        cls.test_case_props['deployment_location_name'] = tester.exec_prepended_name('assembly-tests')
        deployment_location_result = tester.default_client.deployment_locations.create({
            'name': cls.test_case_props['deployment_location_name'],
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        })
        cls.test_case_props['deployment_location_id'] = deployment_location_result['id']
        ## Upload Resource package
        res_pkg_path = tester.tmp_file('dummy_resource.zip')
        tester.build_resource_package_from(tester.test_file('dummy_resource'), res_pkg_path, suffix='assembly-tests')
        cls.test_case_props['dummy_res_pkg_id'] = tester.default_client.resource_packages.create(res_pkg_path)
        ## Get Resource descriptor 
        resource_descriptor = tester.load_descriptor_from(tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='assembly-tests')
        cls.test_case_props['dummy_resource_descriptor_name'] = resource_descriptor['name']
        ## Add Assembly descriptor
        assembly_descriptor = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='assembly-tests')
        tester.default_client.descriptors.create(assembly_descriptor)
        cls.test_case_props['dummy_assembly_descriptor_name'] = assembly_descriptor['name']

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.deployment_locations.delete(cls.test_case_props['deployment_location_id'])
        tester.default_client.resource_packages.delete(cls.test_case_props['dummy_res_pkg_id'])
        tester.default_client.descriptors.delete(cls.test_case_props['dummy_assembly_descriptor_name'])
        tester.default_client.descriptors.delete(cls.test_case_props['dummy_resource_descriptor_name'])

    def _check_process_success(self, process_id: str) -> bool:
        process = self.tester.default_client.processes.get(process_id)
        status = process.get('status')
        if status in ['Completed']:
            return True
        elif status in ['Cancelled', 'Failed']:
            reason = process.get('statusReason')
            self.fail(f'Process failed with status {status}, reason: {reason}')
        else:
            return False

    def _check_property_value(self, assembly: Dict, prop_name: str, expected_value: Any):
        found = False
        for prop in assembly['properties']:
            if prop.get('name') == prop_name:
                self.assertEqual(prop.get('value'), expected_value)
                found = True
        self.assertTrue(found, f'Did not find property: {prop_name}')

    def _delete_and_wait(self, assembly_name: str):
        delete_process_id = self.tester.default_client.assemblies.intent_delete(DeleteAssemblyIntent(assembly_name=assembly_name))
        self.assertIsNotNone(delete_process_id)
        self.tester.wait_until(self._check_process_success, delete_process_id)

    def _get_child(self, assembly: Dict, child_name: str) -> Dict:
        for child in assembly.get('children'):
            name_parts = child.get('name').split('__')
            direct_name = name_parts[-1]
            if direct_name == child_name:
                return child
        raise Exception(f'Could not find child named "{child_name}" in Assembly: {assembly}')

    def test_crud(self):
        assemblies_api = self.tester.default_client.assemblies
        processes_api = self.tester.default_client.processes
        assembly_name = self.tester.exec_prepended_name('test-crud')
        ## Create
        create_process_id = assemblies_api.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_name,
                descriptor_name=self.test_case_props['dummy_assembly_descriptor_name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        self.assertIsNotNone(create_process_id)
        process = processes_api.get(create_process_id)
        self.tester.wait_until(self._check_process_success, create_process_id)
        time.sleep(0.05)
        ## Read
        assembly_id = process['assemblyId']
        get_response = assemblies_api.get(assembly_id)
        self.assertIsNotNone(get_response)
        self.assertEqual(get_response['name'], assembly_name)
        self._check_property_value(get_response, 'dummyProp', 'A')
        ## Upgrade
        upgrade_process_id = assemblies_api.intent_upgrade(
            UpgradeAssemblyIntent(
                assembly_name=assembly_name,
                properties={
                    'dummyProp': 'B'
                }
            )
        )
        self.assertIsNotNone(upgrade_process_id)
        self.tester.wait_until(self._check_process_success, upgrade_process_id)
        time.sleep(0.05)
        get_response = assemblies_api.get(assembly_id)
        self._check_property_value(get_response, 'dummyProp', 'B')
        ## Delete
        self._delete_and_wait(assembly_name)

    def test_change_state(self):
        assemblies_api = self.tester.default_client.assemblies
        processes_api = self.tester.default_client.processes
        assembly_name = self.tester.exec_prepended_name('test-change-state')
        ## Create
        create_process_id = assemblies_api.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_name,
                descriptor_name=self.test_case_props['dummy_assembly_descriptor_name'],
                intended_state='Inactive',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        self.assertIsNotNone(create_process_id)
        process = processes_api.get(create_process_id)
        self.tester.wait_until(self._check_process_success, create_process_id)
        time.sleep(0.05)
        assembly_id = process['assemblyId']
        ## Check State
        get_response = assemblies_api.get(assembly_id)
        self.assertEqual(get_response['state'], 'Inactive')
        ## Change State
        change_state_process_id = assemblies_api.intent_change_state(
            ChangeAssemblyStateIntent(
                assembly_name=assembly_name,
                intended_state='Active'
            )
        )
        self.assertIsNotNone(change_state_process_id)
        self.tester.wait_until(self._check_process_success, change_state_process_id)
        time.sleep(0.05)
        ## Check State
        get_response = assemblies_api.get(assembly_id)
        self.assertEqual(get_response['state'], 'Active')
        ## Delete
        self._delete_and_wait(assembly_name)

    def test_scale(self):
        assemblies_api = self.tester.default_client.assemblies
        processes_api = self.tester.default_client.processes
        assembly_name = self.tester.exec_prepended_name('test-scale')
        ## Create
        create_process_id = assemblies_api.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_name,
                descriptor_name=self.test_case_props['dummy_assembly_descriptor_name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        self.assertIsNotNone(create_process_id)
        process = processes_api.get(create_process_id)
        self.tester.wait_until(self._check_process_success, create_process_id)
        time.sleep(0.05)
        assembly_id = process['assemblyId']
        ## Scale Out
        scale_out_process_id = assemblies_api.intent_scale_out(
            ScaleAssemblyIntent(
                assembly_name=assembly_name,
                cluster_name='B'
            )
        )
        self.assertIsNotNone(scale_out_process_id)
        self.tester.wait_until(self._check_process_success, scale_out_process_id)
        time.sleep(0.05)
        ## Check Cluster
        get_response = assemblies_api.get(assembly_id)
        cluster = self._get_child(get_response, 'B')
        self.assertEqual(len(cluster.get('instances')), 2)
        ## Scale In
        scale_in_process_id = assemblies_api.intent_scale_in(
            ScaleAssemblyIntent(
                assembly_name=assembly_name,
                cluster_name='B'
            )
        )
        self.assertIsNotNone(scale_in_process_id)
        self.tester.wait_until(self._check_process_success, scale_in_process_id)
        time.sleep(0.05)
        ## Check Cluster
        get_response = assemblies_api.get(assembly_id)
        cluster = self._get_child(get_response, 'B')
        self.assertEqual(len(cluster.get('instances')), 1)
        ## Delete
        self._delete_and_wait(assembly_name)

    def test_heal(self):
        assemblies_api = self.tester.default_client.assemblies
        processes_api = self.tester.default_client.processes
        assembly_name = self.tester.exec_prepended_name('test-heal')
        ## Create
        create_process_id = assemblies_api.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_name,
                descriptor_name=self.test_case_props['dummy_assembly_descriptor_name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        self.assertIsNotNone(create_process_id)
        process = processes_api.get(create_process_id)
        self.tester.wait_until(self._check_process_success, create_process_id)
        time.sleep(0.05)
        assembly_id = process['assemblyId']
        ## Heal
        heal_process_id = assemblies_api.intent_heal(
            HealAssemblyIntent(
                assembly_name=assembly_name,
                broken_component_name=assembly_name + '__A'
            )
        )
        self.assertIsNotNone(heal_process_id)
        self.tester.wait_until(self._check_process_success, heal_process_id)
        time.sleep(0.05)
        ## Delete
        self._delete_and_wait(assembly_name)

    def test_all_with_name_containing(self):
        assemblies_api = self.tester.default_client.assemblies
        processes_api = self.tester.default_client.processes
        assembly_A1_name = self.tester.exec_prepended_name('with-namec-A1')
        assembly_A2_name = self.tester.exec_prepended_name('with-namec-A2')
        assembly_B_name = self.tester.exec_prepended_name('with-namec-B')
        ## Create
        create_A1_process_id = assemblies_api.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_A1_name,
                descriptor_name=self.test_case_props['dummy_assembly_descriptor_name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        create_A2_process_id = assemblies_api.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_A2_name,
                descriptor_name=self.test_case_props['dummy_assembly_descriptor_name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        create_B_process_id = assemblies_api.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_B_name,
                descriptor_name=self.test_case_props['dummy_assembly_descriptor_name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        process_A1 = processes_api.get(create_A1_process_id)
        process_A2 = processes_api.get(create_A2_process_id)
        process_B = processes_api.get(create_B_process_id)
        self.tester.wait_until(self._check_process_success, create_A1_process_id)
        self.tester.wait_until(self._check_process_success, create_A2_process_id)
        self.tester.wait_until(self._check_process_success, create_B_process_id)
        time.sleep(0.05)
        ## Get all with name
        search_string = self.tester.exec_prepended_name('with-namec-A')
        search_result = assemblies_api.all_with_name_containing(search_string)
        self.assertEqual(len(search_result['assemblies']), 2)
        ids = []
        for assembly in search_result['assemblies']:
            ids.append(assembly['id'])
        self.assertIn(process_A1['assemblyId'], ids)
        self.assertIn(process_A2['assemblyId'], ids)
        ## Delete
        self._delete_and_wait(assembly_A1_name)
        self._delete_and_wait(assembly_A2_name)
        self._delete_and_wait(assembly_B_name)

    def test_all_with_name(self):
        assemblies_api = self.tester.default_client.assemblies
        processes_api = self.tester.default_client.processes
        assembly_A1_name = self.tester.exec_prepended_name('with-name-A1')
        assembly_A2_name = self.tester.exec_prepended_name('with-name-A2')
        ## Create
        create_A1_process_id = assemblies_api.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_A1_name,
                descriptor_name=self.test_case_props['dummy_assembly_descriptor_name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        create_A2_process_id = assemblies_api.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_A2_name,
                descriptor_name=self.test_case_props['dummy_assembly_descriptor_name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        process_A1 = processes_api.get(create_A1_process_id)
        process_A2 = processes_api.get(create_A2_process_id)
        self.tester.wait_until(self._check_process_success, create_A1_process_id)
        self.tester.wait_until(self._check_process_success, create_A2_process_id)
        time.sleep(0.05)
        ## Get all with name
        search_string = self.tester.exec_prepended_name('with-name-A2')
        search_result = assemblies_api.all_with_name_containing(search_string)
        self.assertEqual(len(search_result['assemblies']), 1)
        self.assertEqual(search_result['assemblies'][0]['id'], process_A2['assemblyId'])
        ## Delete
        self._delete_and_wait(assembly_A1_name)
        self._delete_and_wait(assembly_A2_name)
    
    def test_get_topN(self):
        assemblies_api = self.tester.default_client.assemblies
        processes_api = self.tester.default_client.processes
        assembly_A1_name = self.tester.exec_prepended_name('test-topN-A1')
        assembly_A2_name = self.tester.exec_prepended_name('test-topN-A2')
        ## Create
        create_A1_process_id = assemblies_api.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_A1_name,
                descriptor_name=self.test_case_props['dummy_assembly_descriptor_name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        create_A2_process_id = assemblies_api.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_A2_name,
                descriptor_name=self.test_case_props['dummy_assembly_descriptor_name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        process_A1 = processes_api.get(create_A1_process_id)
        process_A2 = processes_api.get(create_A2_process_id)
        self.tester.wait_until(self._check_process_success, create_A1_process_id)
        self.tester.wait_until(self._check_process_success, create_A2_process_id)
        time.sleep(0.05)
        ## Get top N
        search_result = assemblies_api.get_topN()
        self.assertTrue(len(search_result)>0)
        ids = []
        for assembly in search_result:
            ids.append(assembly['id'])
        self.assertIn(process_A1['assemblyId'], ids)
        self.assertIn(process_A2['assemblyId'], ids)
        ## Delete
        self._delete_and_wait(assembly_A1_name)
        self._delete_and_wait(assembly_A2_name)