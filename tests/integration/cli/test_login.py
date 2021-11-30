from .cli_test_base import CLIIntegrationTest
from lmctl.cli.entry import cli

class TestLogin(CLIIntegrationTest):

    def test_login_with_client_credentials(self):
        if not self.tester.get_default_env().tnco.is_using_oauth:
            self.skipTest('auth_mode != oauth')
            return
        client_id = self.tester.test_properties.auth_testing.client_credentials.client_id
        client_secret = self.tester.test_properties.auth_testing.client_credentials.client_secret
        address = self.tester.config.environments.get('default').tnco.address

        result = self.cli_runner.invoke(cli, ['login', address, '--client', client_id, '--client-secret', client_secret, '--name', 'env1'])
        self.assert_no_errors(result)
        expected_output = 'Login success'
        expected_output += f'\nUpdating config at: {self.tester.config_path}'
        self.assert_output(result, expected_output)

        config = self.tester.read_latest_copy_of_config()
        self.assertEqual(config.active_environment, 'env1')
        self.assertIn('env1', config.environments)
        tnco = config.environments['env1'].tnco
        self.assertEqual(tnco.address, self.tester.config.environments.get('default').tnco.address)
        self.assertIsNone(tnco.client_id)
        self.assertIsNone(tnco.client_secret)
        self.assertIsNotNone(tnco.token)
        self.assertTrue(tnco.is_using_token_auth)
    
    def test_login_with_client_credentials_save_creds(self):
        if not self.tester.get_default_env().tnco.is_using_oauth:
            self.skipTest('auth_mode != oauth')
            return
        client_id = self.tester.test_properties.auth_testing.client_credentials.client_id
        client_secret = self.tester.test_properties.auth_testing.client_credentials.client_secret
        address = self.tester.config.environments.get('default').tnco.address

        result = self.cli_runner.invoke(cli, ['login', address, '--client', client_id, '--client-secret', client_secret, '--save-creds', '--name', 'env2'])
        self.assert_no_errors(result)
        expected_output = 'Login success'
        expected_output += f'\nUpdating config at: {self.tester.config_path}'
        self.assert_output(result, expected_output)

        config = self.tester.read_latest_copy_of_config()
        self.assertEqual(config.active_environment, 'env2')
        self.assertIn('env2', config.environments)
        tnco = config.environments['env2'].tnco
        self.assertEqual(tnco.address, self.tester.config.environments.get('default').tnco.address)
        self.assertEqual(tnco.client_id, client_id)
        self.assertEqual(tnco.client_secret, client_secret)
        self.assertIsNone(tnco.token)
        self.assertTrue(tnco.is_using_oauth)
    
    def test_login_with_legacy_username_password(self):
        if not self.tester.get_default_env().tnco.is_using_oauth:
            self.skipTest('auth_mode != oauth')
            return
        username = self.tester.test_properties.auth_testing.legacy_user_pass.username
        password = self.tester.test_properties.auth_testing.legacy_user_pass.password
        auth_address = self.tester.test_properties.auth_testing.legacy_user_pass.legacy_auth_address
        existing_tnco = self.tester.config.environments.get('default').tnco
        address = existing_tnco.address
        if auth_address is None:
            if existing_tnco.auth_address is not None:
                auth_address = existing_tnco.auth_address 
            else:
                auth_address = address

        result = self.cli_runner.invoke(cli, ['login', address, '--username', username, '--password', password, '--auth-address', auth_address, '--name', 'env3'])
        self.assert_no_errors(result)
        expected_output = 'Login success'
        expected_output += f'\nUpdating config at: {self.tester.config_path}'
        self.assert_output(result, expected_output)

        config = self.tester.read_latest_copy_of_config()
        self.assertEqual(config.active_environment, 'env3')
        self.assertIn('env3', config.environments)
        tnco = config.environments['env3'].tnco
        self.assertEqual(tnco.address, existing_tnco.address)
        self.assertIsNone(tnco.username)
        self.assertIsNone(tnco.password)
        self.assertIsNotNone(tnco.token)
        self.assertTrue(tnco.is_using_token_auth)

    def test_login_with_legacy_username_password_save_creds(self):
        if not self.tester.get_default_env().tnco.is_using_oauth:
            self.skipTest('auth_mode != oauth')
            return
        username = self.tester.test_properties.auth_testing.legacy_user_pass.username
        password = self.tester.test_properties.auth_testing.legacy_user_pass.password
        auth_address = self.tester.test_properties.auth_testing.legacy_user_pass.legacy_auth_address
        existing_tnco = self.tester.config.environments.get('default').tnco
        address = existing_tnco.address
        if auth_address is None:
            if existing_tnco.auth_address is not None:
                auth_address = existing_tnco.auth_address 
            else:
                auth_address = address

        result = self.cli_runner.invoke(cli, ['login', address, '--username', username, '--password', password, '--auth-address', auth_address, '--save-creds', '--name', 'env4'])
        self.assert_no_errors(result)
        expected_output = 'Login success'
        expected_output += f'\nUpdating config at: {self.tester.config_path}'
        self.assert_output(result, expected_output)

        config = self.tester.read_latest_copy_of_config()
        self.assertEqual(config.active_environment, 'env4')
        self.assertIn('env4', config.environments)
        tnco = config.environments['env4'].tnco
        self.assertEqual(tnco.address, existing_tnco.address)
        self.assertEqual(tnco.username, username)
        self.assertEqual(tnco.password, password)
        self.assertIsNone(tnco.token)
        self.assertTrue(tnco.is_using_oauth)
    
    def test_login_with_username_password_and_client(self):
        if not self.tester.get_default_env().tnco.is_using_oauth:
            self.skipTest('auth_mode != oauth')
            return
        client_id = self.tester.test_properties.auth_testing.user_pass.client_id
        client_secret = self.tester.test_properties.auth_testing.user_pass.client_secret
        username = self.tester.test_properties.auth_testing.user_pass.username
        password = self.tester.test_properties.auth_testing.user_pass.password
        existing_tnco = self.tester.config.environments.get('default').tnco
        address = existing_tnco.address

        result = self.cli_runner.invoke(cli, ['login', address, '--username', username, '--password', password, '--client', client_id, '--client-secret', client_secret, '--name', 'env5'])
        self.assert_no_errors(result)
        expected_output = 'Login success'
        expected_output += f'\nUpdating config at: {self.tester.config_path}'
        self.assert_output(result, expected_output)

        config = self.tester.read_latest_copy_of_config()
        self.assertEqual(config.active_environment, 'env5')
        self.assertIn('env5', config.environments)
        tnco = config.environments['env5'].tnco
        self.assertEqual(tnco.address, existing_tnco.address)
        self.assertIsNone(tnco.client_id)
        self.assertIsNone(tnco.client_secret)
        self.assertIsNone(tnco.username)
        self.assertIsNone(tnco.password)
        self.assertIsNotNone(tnco.token)
        self.assertTrue(tnco.is_using_token_auth)
    
    def test_login_with_username_password_and_client_save_creds(self):
        if not self.tester.get_default_env().tnco.is_using_oauth:
            self.skipTest('auth_mode != oauth')
            return
        client_id = self.tester.test_properties.auth_testing.user_pass.client_id
        client_secret = self.tester.test_properties.auth_testing.user_pass.client_secret
        username = self.tester.test_properties.auth_testing.user_pass.username
        password = self.tester.test_properties.auth_testing.user_pass.password
        existing_tnco = self.tester.config.environments.get('default').tnco
        address = existing_tnco.address

        result = self.cli_runner.invoke(cli, ['login', address, '--username', username, '--password', password, '--client', client_id, '--client-secret', client_secret, '--save-creds', '--name', 'env6'])
        self.assert_no_errors(result)
        expected_output = 'Login success'
        expected_output += f'\nUpdating config at: {self.tester.config_path}'
        self.assert_output(result, expected_output)

        config = self.tester.read_latest_copy_of_config()
        self.assertEqual(config.active_environment, 'env6')
        self.assertIn('env6', config.environments)
        tnco = config.environments['env6'].tnco
        self.assertEqual(tnco.address, existing_tnco.address)
        self.assertEqual(tnco.client_id, client_id)
        self.assertEqual(tnco.client_secret, client_secret)
        self.assertEqual(tnco.username, username)
        self.assertEqual(tnco.password, password)
        self.assertIsNone(tnco.token)
        self.assertTrue(tnco.is_using_oauth)

    def test_login_with_token(self):
        token = self.tester.test_properties.auth_testing.token_auth.token
        existing_tnco = self.tester.config.environments.get('default').tnco
        address = existing_tnco.address

        result = self.cli_runner.invoke(cli, ['login', address, '--token', token, '--name', 'env7'])
        self.assert_no_errors(result)
        expected_output = 'Login success'
        expected_output += f'\nUpdating config at: {self.tester.config_path}'
        self.assert_output(result, expected_output)

        config = self.tester.read_latest_copy_of_config()
        self.assertEqual(config.active_environment, 'env7')
        self.assertIn('env7', config.environments)
        tnco = config.environments['env7'].tnco
        self.assertEqual(tnco.address, existing_tnco.address)
        self.assertIsNotNone(tnco.token)
        self.assertTrue(tnco.is_using_token_auth)

    def test_login_with_zen_username_api_key(self):
        if not self.tester.get_default_env().tnco.is_using_zen_auth:
            self.skipTest('auth_mode != zen')
            return
        username = self.tester.test_properties.auth_testing.zen_api_key.username
        api_key = self.tester.test_properties.auth_testing.zen_api_key.api_key
        zen_auth_address = self.tester.test_properties.auth_testing.zen_api_key.zen_auth_address
        existing_tnco = self.tester.config.environments.get('default').tnco
        address = existing_tnco.address
        if zen_auth_address is None:
            if existing_tnco.auth_address is not None:
                zen_auth_address = existing_tnco.auth_address 
            else:
                zen_auth_address = address

        result = self.cli_runner.invoke(cli, ['login', address, '--zen', '--username', username, '--api-key', api_key, '--auth-address', zen_auth_address, '--name', 'env8'])
        self.assert_no_errors(result)
        expected_output = 'Login success'
        expected_output += f'\nUpdating config at: {self.tester.config_path}'
        self.assert_output(result, expected_output)

        config = self.tester.read_latest_copy_of_config()
        self.assertEqual(config.active_environment, 'env8')
        self.assertIn('env8', config.environments)
        tnco = config.environments['env8'].tnco
        self.assertEqual(tnco.address, existing_tnco.address)
        self.assertIsNone(tnco.username)
        self.assertIsNone(tnco.api_key)
        self.assertIsNone(tnco.auth_address)
        self.assertIsNotNone(tnco.token)
        self.assertTrue(tnco.is_using_token_auth)

    def test_login_with_zen_username_api_key_save_creds(self):
        if not self.tester.get_default_env().tnco.is_using_zen_auth:
            self.skipTest('auth_mode != zen')
            return
        username = self.tester.test_properties.auth_testing.zen_api_key.username
        api_key = self.tester.test_properties.auth_testing.zen_api_key.api_key
        zen_auth_address = self.tester.test_properties.auth_testing.zen_api_key.zen_auth_address
        existing_tnco = self.tester.config.environments.get('default').tnco
        address = existing_tnco.address
        if zen_auth_address is None:
            if existing_tnco.auth_address is not None:
                zen_auth_address = existing_tnco.auth_address 
            else:
                zen_auth_address = address

        result = self.cli_runner.invoke(cli, ['login', address, '--zen', '--username', username, '--api-key', api_key, '--auth-address', zen_auth_address, '--save-creds', '--name', 'env9'])
        self.assert_no_errors(result)
        expected_output = 'Login success'
        expected_output += f'\nUpdating config at: {self.tester.config_path}'
        self.assert_output(result, expected_output)

        config = self.tester.read_latest_copy_of_config()
        self.assertEqual(config.active_environment, 'env9')
        self.assertIn('env9', config.environments)
        tnco = config.environments['env9'].tnco
        self.assertEqual(tnco.address, existing_tnco.address)
        self.assertEqual(tnco.username, username)
        self.assertEqual(tnco.api_key, api_key)
        self.assertIsNone(tnco.token)
        self.assertTrue(tnco.is_using_zen)