import os
import time
from tests.integration.integration_test_base import IntegrationTest
from lmctl.client.models import CreateAssemblyIntent, DeleteAssemblyIntent

class TestProcessesAPI(IntegrationTest):

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
        tester.build_resource_package_from(tester.test_file('dummy_resource'), res_pkg_path, suffix='process-tests')
        cls.test_case_props['dummy_res_pkg_id'] = tester.default_client.resource_packages.create(res_pkg_path)
        ## Add Resource descriptor 
        resource_descriptor = tester.load_descriptor_from(tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='process-tests')
        tester.default_client.descriptors.create(resource_descriptor)
        cls.test_case_props['dummy_resource_descriptor_name'] = resource_descriptor['name']
        ## Add Assembly descriptor
        assembly_descriptor = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='process-tests')
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

    def _delete_and_wait(self, assembly_name: str):
        delete_process_id = self.tester.default_client.assemblies.intent_delete(DeleteAssemblyIntent(assembly_name=assembly_name))
        self.assertIsNotNone(delete_process_id)
        self.tester.wait_until(self._check_process_success, delete_process_id)

    def test_read(self):
        assemblies_api = self.tester.default_client.assemblies
        processes_api = self.tester.default_client.processes
        assembly_name = self.tester.exec_prepended_name('test-process-read')
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
        self.assertIsNotNone(process)
        self.assertEqual(process['assemblyName'], assembly_name)
        self.assertEqual(process['assemblyType'], self.test_case_props['dummy_assembly_descriptor_name'])
        self.tester.wait_until(self._check_process_success, create_process_id)
        time.sleep(0.05)
        ## Delete
        self._delete_and_wait(assembly_name)
