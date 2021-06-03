from tests.integration.integration_test_base import IntegrationTest

class TestAuthenticationAPI(IntegrationTest):

    def test_request_client_access(self):
        client_id = self.tester.test_properties.auth_testing.client_credentials.client_id
        client_secret = self.tester.test_properties.auth_testing.client_credentials.client_secret
        auth_response = self.tester.default_client.auth.request_client_access(client_id, client_secret)
        self.assertIn('access_token', auth_response)
        self.assertIn('expires_in', auth_response)
    
    def test_request_user_access(self):
        client_id = self.tester.test_properties.auth_testing.user_pass.client_id
        client_secret = self.tester.test_properties.auth_testing.user_pass.client_secret
        username = self.tester.test_properties.auth_testing.user_pass.username
        password = self.tester.test_properties.auth_testing.user_pass.password
        auth_response = self.tester.default_client.auth.request_user_access(client_id, client_secret, username, password)
        self.assertIn('access_token', auth_response)
        self.assertIn('expires_in', auth_response)
    
    def test_legacy_login(self):
        username = self.tester.test_properties.auth_testing.legacy_user_pass.username
        password = self.tester.test_properties.auth_testing.legacy_user_pass.password
        auth_response = self.tester.default_client.auth.legacy_login(username, password)
        self.assertIn('accessToken', auth_response)
        self.assertIn('expiresIn', auth_response)
    
    def test_token(self):
        client = self.tester.build_client()
        # Switch to Token Auth
        client.auth_type = self.tester.test_properties.auth_testing.token_auth

        # Exec request to confirm auth
        response = client.descriptors.all()
        self.assertIsInstance(response, list)
