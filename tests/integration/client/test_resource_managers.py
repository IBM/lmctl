from tests.integration.integration_test_base import IntegrationTest
from lmctl.client import TNCOClientHttpError
import os

class TestResourceManagersAPI(IntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Preload Brent with a deployment location and Resource descriptor
        ## Add deployment location
        cls.test_case_props['deployment_location_name'] = tester.exec_prepended_name('rm-tests')
        deployment_location_result = tester.default_client.deployment_locations.create({
            'name': cls.test_case_props['deployment_location_name'],
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        })
        cls.test_case_props['deployment_location_id'] = deployment_location_result['id']
        ## Upload Resource package
        res_pkg_path = tester.tmp_file('dummy_resource.zip')
        tester.build_resource_package_from(tester.test_file('dummy_resource'), res_pkg_path, suffix='rm-tests')
        cls.test_case_props['dummy_res_pkg_id'] = tester.default_client.resource_packages.create(res_pkg_path)
        resource_descriptor = tester.load_descriptor_from(tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='rm-tests')
        cls.test_case_props['dummy_resource_descriptor_name'] = resource_descriptor['name']

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.deployment_locations.delete(cls.test_case_props['deployment_location_id'])
        tester.default_client.resource_packages.delete(cls.test_case_props['dummy_res_pkg_id'])
        try:
            tester.default_client.descriptors.get(cls.test_case_props['dummy_resource_descriptor_name'])
        except TNCOClientHttpError as e:
            ## Ignore not found error
            if e.status_code != 404:
                raise
        else:
            tester.default_client.descriptors.delete(cls.test_case_props['dummy_resource_descriptor_name'])

    def test_crud(self):
        resource_manager = {
            'name': self.tester.exec_prepended_name('rm-crud'),
            'url': 'https://cp4na-o-brent:8291/api/resource-manager'
        }
        ## Create
        create_response = self.tester.default_client.resource_managers.create(resource_manager)
        self.assertIsNotNone(create_response)
        self.assertEqual(create_response['resourceManagerOperation'], 'ADD')
        self.assertTrue(len(create_response['deploymentLocations']) > 0)
        self.assertTrue(len(create_response['resourceTypes']) > 0)
        resource_manager_id = resource_manager['name']
        ## Read
        get_response = self.tester.default_client.resource_managers.get(resource_manager_id)
        self.assertIsNotNone(get_response)
        self.assertEqual(get_response['name'], resource_manager['name'])
        self.assertEqual(get_response['url'], resource_manager['url'])
        ## Update - no attribute changes but re-triggers onboarding
        update_response = self.tester.default_client.resource_managers.update(resource_manager)
        self.assertIsNotNone(update_response)
        self.assertEqual(update_response['resourceManagerOperation'], 'UPDATE')
        self.assertTrue(len(update_response['deploymentLocations']) > 0)
        self.assertTrue(len(update_response['resourceTypes']) > 0)
        ## Delete
        delete_response = self.tester.default_client.resource_managers.delete(resource_manager_id)
        self.assertIsNone(delete_response)

    def test_all(self):
        resource_managers_A = {
            'name': self.tester.exec_prepended_name('rm-all-A'),
            'url': 'https://cp4na-o-brent:8291/api/resource-manager'
        }
        self.tester.default_client.resource_managers.create(resource_managers_A)
        resource_managers_B = {
            'name': self.tester.exec_prepended_name('rm-all-B'),
            'url': 'https://cp4na-o-brent:8291/api/resource-manager'
        }
        self.tester.default_client.resource_managers.create(resource_managers_B)
        all_response = self.tester.default_client.resource_managers.all()
        # Might be other RMs
        self.assertTrue(len(all_response) > 0)
        names = []
        for rm in all_response:
            names.append(rm['name'])
        self.assertIn(resource_managers_A['name'], names)
        self.assertIn(resource_managers_B['name'], names)
        self.tester.default_client.resource_managers.delete(resource_managers_A['name'])
        self.tester.default_client.resource_managers.delete(resource_managers_B['name'])



