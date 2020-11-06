from tests.integration.integration_test_base import IntegrationTest
import yaml
import json

class TestBehaviourAssemblyConfigurationsAPI(IntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add Assembly descriptor
        assembly_descriptor = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='assemblyconf-tests')
        tester.default_client.descriptors.create(assembly_descriptor)
        cls.test_case_props['dummy_assembly_descriptor_name'] = assembly_descriptor['name']

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.descriptors.delete(cls.test_case_props['dummy_assembly_descriptor_name'])

    def test_crud(self):
        assembly_configuration = {
            'name': 'assembly-config-crud',
            'projectId': self.test_case_props['dummy_assembly_descriptor_name'],
            'descriptorName': self.test_case_props['dummy_assembly_descriptor_name'],
            'properties': {
                'dummyProp': 'A'
            }
        }
        ## Create
        create_response = self.tester.default_client.behaviour_assembly_confs.create(assembly_configuration)
        self.assertIn('id', create_response)
        assembly_configuration_id = create_response['id']
        ## Read
        get_response = self.tester.default_client.behaviour_assembly_confs.get(assembly_configuration_id)
        self.assertIsNotNone(get_response)
        self.assertEqual(get_response['name'], assembly_configuration['name'])
        self.assertEqual(get_response['descriptorName'], assembly_configuration['descriptorName'])
        self.assertEqual(get_response['properties'], assembly_configuration['properties'])
        ## Update
        updated_assembly_configuration = get_response.copy()
        updated_assembly_configuration['properties'] = {'dummyProp': 'B'}
        update_response = self.tester.default_client.behaviour_assembly_confs.update(updated_assembly_configuration)
        self.assertIsNone(update_response)
        ## Read
        get_response = self.tester.default_client.behaviour_assembly_confs.get(assembly_configuration_id)
        self.assertEqual(get_response['properties']['dummyProp'], 'B')
        ## Delete
        delete_response = self.tester.default_client.behaviour_assembly_confs.delete(assembly_configuration_id)
        self.assertIsNone(delete_response)

    def test_all_in_project(self):
        project_id = self.test_case_props['dummy_assembly_descriptor_name']
        assembly_configuration_A = {
            'name': 'assembly-config-all-in-project-A',
            'projectId': project_id,
            'descriptorName': self.test_case_props['dummy_assembly_descriptor_name'],
            'properties': {}
        }
        assembly_configuration_B = {
            'name': 'assembly-config-all-in-project-B',
            'projectId': project_id,
            'descriptorName': self.test_case_props['dummy_assembly_descriptor_name'],
            'properties': {}
        }
        create_A_response = self.tester.default_client.behaviour_assembly_confs.create(assembly_configuration_A)
        assembly_configuration_A_id = create_A_response['id']
        create_B_response = self.tester.default_client.behaviour_assembly_confs.create(assembly_configuration_B)
        assembly_configuration_B_id = create_B_response['id']
        get_response = self.tester.default_client.behaviour_assembly_confs.all_in_project(project_id)
        self.assertEqual(len(get_response), 2)
        ids = []
        for conf in get_response:
            ids.append(conf['id'])
        self.assertIn(assembly_configuration_A_id, ids)
        self.assertIn(assembly_configuration_B_id, ids)
        