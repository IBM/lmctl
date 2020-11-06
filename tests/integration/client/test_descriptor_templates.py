from tests.integration.integration_test_base import IntegrationTest
import yaml

class TestDescriptorTemplatesAPI(IntegrationTest):

    def test_all(self):
        templates_api = self.tester.default_client.descriptor_templates
        descriptor_template_A = self.tester.load_descriptor_from(self.tester.test_file('dummy_template.yaml'), suffix='descriptortmpl-tests')
        name_part = self.tester.exec_prepended_name('test-all-A')
        descriptor_template_A['name'] = f'assembly-template::{name_part}::1.0'
        descriptor_template_B = self.tester.load_descriptor_from(self.tester.test_file('dummy_template.yaml'), suffix='descriptortmpl-tests')
        name_part = self.tester.exec_prepended_name('test-all-B')
        descriptor_template_B['name'] = f'assembly-template::{name_part}::1.0'
        templates_api.create(descriptor_template_A)
        templates_api.create(descriptor_template_B)
        all_response = templates_api.all()
        names = []
        for template in all_response:
            names.append(template['name'])
        self.assertIn(descriptor_template_A['name'], names)
        self.assertIn(descriptor_template_B['name'], names)
        templates_api.delete(descriptor_template_A['name'])
        templates_api.delete(descriptor_template_B['name'])

    def test_crud(self):
        descriptor_template = self.tester.load_descriptor_from(self.tester.test_file('dummy_template.yaml'), suffix='descriptortmpl-test-crud')
        templates_api = self.tester.default_client.descriptor_templates
        ## Create
        create_response = templates_api.create(descriptor_template)
        self.assertIsNone(create_response)
        ## Read
        get_response = templates_api.get(descriptor_template['name'])
        self.assertIsNotNone(get_response)
        self.assertEqual(get_response, descriptor_template)
        ## Update
        updated_template = get_response.copy()
        updated_template['description'] = 'Updated description'
        update_response = templates_api.update(updated_template)
        self.assertIsNone(update_response)
        get_response = templates_api.get(descriptor_template['name'])
        self.assertEqual(get_response['description'], 'Updated description')
        ## Delete
        delete_response = templates_api.delete(descriptor_template['name'])
        self.assertIsNone(delete_response)
    
    def test_render(self):
        descriptor_template = self.tester.load_descriptor_from(self.tester.test_file('dummy_template.yaml'), suffix='descriptortmpl-test-render')
        name_part = self.tester.exec_prepended_name('test-render')
        descriptor_template['name'] = f'assembly-template::{name_part}::1.0'
        templates_api = self.tester.default_client.descriptor_templates
        templates_api.create(descriptor_template)
        render_result = templates_api.render(descriptor_template['name'], {'properties': {'dummyProp': 'A'}})
        self.assertEqual(render_result['description'], 'Adding a value from template properties -> A')
        templates_api.delete(descriptor_template['name'])
    
    def test_render_raw(self):
        descriptor_template = self.tester.load_descriptor_from(self.tester.test_file('dummy_template.yaml'), suffix='descriptortmpl-test-render-raw')
        name_part = self.tester.exec_prepended_name('test-render-raw')
        descriptor_template['name'] = f'assembly-template::{name_part}::1.0'
        templates_api = self.tester.default_client.descriptor_templates
        templates_api.create(descriptor_template)
        render_result = templates_api.render_raw(descriptor_template['name'], {'properties': {'dummyProp': 'A'}})
        self.assertEqual(type(render_result), str)
        parsed_render_result = yaml.safe_load(render_result)
        self.assertEqual(parsed_render_result['description'], 'Adding a value from template properties -> A')
        templates_api.delete(descriptor_template['name'])
    