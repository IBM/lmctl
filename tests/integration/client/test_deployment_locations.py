from tests.integration.integration_test_base import IntegrationTest

class TestDeploymentLocationsAPI(IntegrationTest):

    def test_crud(self):
        deployment_location = {
            'name': self.tester.exec_prepended_name('dl-crud'),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        }
        ## Create
        create_response = self.tester.default_client.deployment_locations.create(deployment_location)
        self.assertIn('id', create_response)
        deployment_location_id = create_response['id']
        ## Read
        get_response = self.tester.default_client.deployment_locations.get(deployment_location_id)
        self.assertIsNotNone(get_response)
        self.assertEqual(get_response['name'], deployment_location['name'])
        self.assertEqual(get_response['infrastructureType'], deployment_location['infrastructureType'])
        self.assertEqual(get_response['resourceManager'], deployment_location['resourceManager'])
        #Properties are not returned
        ## Update
        updated_deployment_location = get_response.copy()
        updated_deployment_location['properties'] = {'new_prop': 'test'}
        update_response = self.tester.default_client.deployment_locations.update(updated_deployment_location)
        self.assertIsNone(update_response)
        #Cannot confirm update as properties are not returned in GET
        ## Delete
        delete_response = self.tester.default_client.deployment_locations.delete(deployment_location_id)
        self.assertIsNone(delete_response)

    def test_all(self):
        deployment_location_A = {
            'name': self.tester.exec_prepended_name('dl-all-A'),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        }
        deployment_location_A = self.tester.default_client.deployment_locations.create(deployment_location_A)
        deployment_location_B = {
            'name': self.tester.exec_prepended_name('dl-all-B'),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        }
        deployment_location_B = self.tester.default_client.deployment_locations.create(deployment_location_B)
        all_response = self.tester.default_client.deployment_locations.all()
        # Might be other locations
        self.assertTrue(len(all_response) > 0)
        ids = []
        for dl in all_response:
            ids.append(dl['id'])
        self.assertIn(deployment_location_A['id'], ids)
        self.assertIn(deployment_location_B['id'], ids)
        self.tester.default_client.deployment_locations.delete(deployment_location_A['id'])
        self.tester.default_client.deployment_locations.delete(deployment_location_B['id'])




    
