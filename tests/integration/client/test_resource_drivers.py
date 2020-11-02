from tests.integration.integration_test_base import IntegrationTest

class TestResourceDriversAPI(IntegrationTest):

    def test_crd(self):
        drivers_api = self.tester.default_client.resource_drivers
        resource_driver = {
            'type': self.tester.exec_prepended_name('crd-test'),
            'baseUri': 'http://ansible-lifecycle-driver:8292'
        }
        ## Create
        create_response = drivers_api.create(resource_driver)
        self.assertIn('id', create_response)
        resource_driver_id = create_response['id']
        ## Read
        get_response = drivers_api.get(resource_driver_id)
        self.assertIsNotNone(get_response)
        self.assertEqual(get_response['type'], resource_driver['type'])
        self.assertEqual(get_response['baseUri'], resource_driver['baseUri'])
        ## Delete
        delete_response = drivers_api.delete(resource_driver_id)
        self.assertIsNone(delete_response)

    def test_get_by_type(self):
        drivers_api = self.tester.default_client.resource_drivers
        type_value = self.tester.exec_prepended_name('get-by-type')
        resource_driver = {
            'type': type_value,
            'baseUri': 'http://ansible-lifecycle-driver:8292'
        }
        drivers_api.create(resource_driver)
        get_by_type_response = drivers_api.get_by_type(type_value)
        self.assertIsNotNone(get_by_type_response)
        self.assertEqual(get_by_type_response['type'], resource_driver['type'])
        self.assertEqual(get_by_type_response['baseUri'], resource_driver['baseUri'])
        drivers_api.delete(get_by_type_response['id'])