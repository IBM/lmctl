from .client_integration_test_base import ClientIntegrationTest

class TestBehaviourProjectsAPI(ClientIntegrationTest):

    def test_crud(self):
        project = {
            'name': self.tester.exec_prepended_name('project-crud')
        }
        ## Create
        create_response = self.tester.default_client.behaviour_projects.create(project)
        self.assertIn('id', create_response)
        project_id = create_response['id']
        ## Read
        get_response = self.tester.default_client.behaviour_projects.get(project_id)
        self.assertIsNotNone(get_response)
        self.assertEqual(get_response['name'], project['name'])
        ## Update
        updated_project = get_response.copy()
        updated_project['description'] = 'Adding a description'
        update_response = self.tester.default_client.behaviour_projects.update(updated_project)
        self.assertIsNone(update_response)
        ## Read
        get_response = self.tester.default_client.behaviour_projects.get(project_id)
        self.assertEqual(get_response['description'], 'Adding a description')
        ## Delete
        delete_response = self.tester.default_client.behaviour_projects.delete(project_id)
        self.assertIsNone(delete_response)

    def test_all(self):
        project_A = {
            'name': self.tester.exec_prepended_name('all-A')
        }
        project_A = self.tester.default_client.behaviour_projects.create(project_A)
        project_B = {
            'name': self.tester.exec_prepended_name('all-B')
        }
        project_B = self.tester.default_client.behaviour_projects.create(project_B)
        all_response = self.tester.default_client.behaviour_projects.all()
        # Might be other locations
        self.assertTrue(len(all_response) > 0)
        ids = []
        for dl in all_response:
            ids.append(dl['id'])
        self.assertIn(project_A['id'], ids)
        self.assertIn(project_B['id'], ids)
