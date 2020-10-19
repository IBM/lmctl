from .client_integration_test_base import ClientIntegrationTest

class TestDescriptorsAPI(ClientIntegrationTest):
    
    def test_all(self):
        descriptors_api = self.tester.default_client.descriptors
        descriptor_A = self.tester.load_descriptor_from(self.tester.test_file('dummy_assembly.yaml'))
        name_part = self.tester.exec_prepended_name('test-all-A')
        descriptor_A['name'] = f'assembly::{name_part}::1.0'
        descriptor_B = self.tester.load_descriptor_from(self.tester.test_file('dummy_assembly.yaml'))
        name_part = self.tester.exec_prepended_name('test-all-B')
        descriptor_B['name'] = f'assembly::{name_part}::1.0'
        descriptors_api.create(descriptor_A)
        descriptors_api.create(descriptor_B)
        all_response = descriptors_api.all()
        names = []
        for template in all_response:
            names.append(template['name'])
        self.assertIn(descriptor_A['name'], names)
        self.assertIn(descriptor_B['name'], names)

    def test_crud(self):
        descriptor = self.tester.load_descriptor_from(self.tester.test_file('dummy_assembly.yaml'))
        name_part = self.tester.exec_prepended_name('test-crud')
        descriptor['name'] = f'assembly::{name_part}::1.0'
        descriptors_api = self.tester.default_client.descriptors
        ## Create
        create_response = descriptors_api.create(descriptor)
        self.assertIsNone(create_response)
        ## Read
        get_response = descriptors_api.get(descriptor['name'])
        self.assertIsNotNone(get_response)
        self.assertEqual(get_response, descriptor)
        ## Update
        updated_template = get_response.copy()
        updated_template['description'] = 'Updated description'
        update_response = descriptors_api.update(updated_template)
        self.assertIsNone(update_response)
        get_response = descriptors_api.get(descriptor['name'])
        self.assertEqual(get_response['description'], 'Updated description')
        ## Delete
        delete_response = descriptors_api.delete(descriptor['name'])
        self.assertIsNone(delete_response)
    