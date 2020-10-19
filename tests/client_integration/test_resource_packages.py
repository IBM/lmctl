from .client_integration_test_base import ClientIntegrationTest
from lmctl.client import LmClientHttpError
import os

class TestResourcePackagesAPI(ClientIntegrationTest):

    def test_cud(self):
        res_pkgs_api = self.tester.default_client.resource_packages
        res_pkg_path = self.tester.tmp_file('dummy_resource.zip')
        self.tester.build_resource_package_from(self.tester.test_file('dummy_resource'), res_pkg_path)
        resource_descriptor = self.tester.load_descriptor_from(self.tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')))
        ## Create
        create_response = res_pkgs_api.create(res_pkg_path)
        self.assertIsNotNone(create_response)
        self.assertEqual(create_response, resource_descriptor['name'])
        ## Update
        update_response = res_pkgs_api.update(resource_descriptor['name'], res_pkg_path)
        self.assertIsNone(update_response)
        ## Delete 
        delete_response = res_pkgs_api.delete(resource_descriptor['name'])
        self.assertIsNone(delete_response)