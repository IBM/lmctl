from tests.integration.integration_test_base import IntegrationTest

class TestAuthenticationAPI(IntegrationTest):

    def test_request_client_access(self):
        if not self.tester.get_default_env().tnco.is_using_oauth:
            self.skipTest('auth_mode != oauth')
            return
        client_id = self.tester.test_properties.auth_testing.client_credentials.client_id
        client_secret = self.tester.test_properties.auth_testing.client_credentials.client_secret
        auth_response = self.tester.default_client.auth.request_client_access(client_id, client_secret)
        self.assertIn('access_token', auth_response)
        self.assertIn('expires_in', auth_response)
    
    def test_request_user_access(self):
        if not self.tester.get_default_env().tnco.is_using_oauth:
            self.skipTest('auth_mode != oauth')
            return
        client_id = self.tester.test_properties.auth_testing.user_pass.client_id
        client_secret = self.tester.test_properties.auth_testing.user_pass.client_secret
        username = self.tester.test_properties.auth_testing.user_pass.username
        password = self.tester.test_properties.auth_testing.user_pass.password
        auth_response = self.tester.default_client.auth.request_user_access(client_id, client_secret, username, password)
        self.assertIn('access_token', auth_response)
        self.assertIn('expires_in', auth_response)
    
    def test_legacy_login(self):
        if not self.tester.get_default_env().tnco.is_using_oauth:
            self.skipTest('auth_mode != oauth')
            return
        username = self.tester.test_properties.auth_testing.legacy_user_pass.username
        password = self.tester.test_properties.auth_testing.legacy_user_pass.password
        auth_response = self.tester.default_client.auth.legacy_login(username, password)
        self.assertIn('accessToken', auth_response)
        self.assertIn('expiresIn', auth_response)
    
    def test_zen_api_key_auth(self):
        if not self.tester.get_default_env().tnco.is_using_zen_auth:
            self.skipTest('auth_mode != zen')
            return
        username = self.tester.test_properties.auth_testing.zen_api_key.username
        api_key = self.tester.test_properties.auth_testing.zen_api_key.password
        auth_response = self.tester.default_client.auth.request_zen_api_key_access(username, api_key)
        self.assertIn('token', auth_response)
