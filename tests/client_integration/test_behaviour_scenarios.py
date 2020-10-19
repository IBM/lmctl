from .client_integration_test_base import ClientIntegrationTest

class TestBehaviourScenariosAPI(ClientIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add Assembly descriptor - this creates a project for us
        assembly_descriptor = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'))
        tester.default_client.descriptors.create(assembly_descriptor)
        cls.test_case_props['dummy_assembly_descriptor_name'] = assembly_descriptor['name']

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.descriptors.delete(cls.test_case_props['dummy_assembly_descriptor_name'])
    
    def test_crud(self):
        scenario = {
            'name': 'scenario-crud',
            'projectId': self.test_case_props['dummy_assembly_descriptor_name']
        }
        ## Create
        create_response = self.tester.default_client.behaviour_scenarios.create(scenario)
        self.assertIn('id', create_response)
        scenario_id = create_response['id']
        ## Read
        get_response = self.tester.default_client.behaviour_scenarios.get(scenario_id)
        self.assertIsNotNone(get_response)
        self.assertEqual(get_response['name'], scenario['name'])
        ## Update
        updated_scenario = get_response.copy()
        updated_scenario['description'] = 'Adding a description'
        update_response = self.tester.default_client.behaviour_scenarios.update(updated_scenario)
        self.assertIsNone(update_response)
        ## Read
        get_response = self.tester.default_client.behaviour_scenarios.get(scenario_id)
        self.assertEqual(get_response['description'], 'Adding a description')
        ## Delete
        delete_response = self.tester.default_client.behaviour_scenarios.delete(scenario_id)
        self.assertIsNone(delete_response)

    def test_all_in_project(self):
        project_id = self.test_case_props['dummy_assembly_descriptor_name']
        scenario_A = {
            'name': 'all-in-project-A',
            'projectId': project_id
        }
        scenario_B = {
            'name': 'all-in-project-B',
            'projectId': project_id
        }
        create_A_response = self.tester.default_client.behaviour_scenarios.create(scenario_A)
        scenario_A_id = create_A_response['id']
        create_B_response = self.tester.default_client.behaviour_scenarios.create(scenario_B)
        scenario_B_id = create_B_response['id']
        get_response = self.tester.default_client.behaviour_scenarios.all_in_project(project_id)
        self.assertEqual(len(get_response), 2)
        ids = []
        for conf in get_response:
            ids.append(conf['id'])
        self.assertIn(scenario_A_id, ids)
        self.assertIn(scenario_B_id, ids)