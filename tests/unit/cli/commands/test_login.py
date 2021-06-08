import tests.unit.cli.commands.command_testing as command_testing
from unittest.mock import patch
from lmctl.cli.controller import clear_global_controller
from lmctl.cli.commands.login import login
from lmctl.config import ConfigFinder, Config
from lmctl.environment import EnvironmentGroup

class TestLoginCommands(command_testing.CommandTestCase):

    def setUp(self):
        super().setUp()
        self.tnco_env_client_patcher = patch('lmctl.environment.lmenv.TNCOClientBuilder')
        self.mock_tnco_client_builder_class = self.tnco_env_client_patcher.start()
        self.addCleanup(self.tnco_env_client_patcher.stop)
        self.mock_tnco_client_builder = self.mock_tnco_client_builder_class.return_value
        self.mock_tnco_client = self.mock_tnco_client_builder.build.return_value
        self.mock_tnco_client.get_access_token.return_value = '123'

        self.config_parser_patcher = patch('lmctl.cli.commands.login.ConfigParser')
        self.mock_config_parser_class = self.config_parser_patcher.start()
        self.addCleanup(self.mock_config_parser_class.stop)
        self.mock_config_parser = self.mock_config_parser_class.return_value
        self.mock_config_parser.from_file_as_dict.return_value = {
            'environments': {}
        }

        self.default_config_path = ConfigFinder().get_default_config_path()

        self.global_config_patcher = patch('lmctl.cli.controller.get_global_config_with_path')
        self.mock_get_global_config = self.global_config_patcher.start()
        self.addCleanup(self.global_config_patcher.stop)
        self.mock_get_global_config.return_value = (Config(), self.default_config_path)


    def test_login_without_args_prompts_for_client_and_user(self):
        result = self.runner.invoke(login, ['http://mock.example.com'], input='TestClient\nTestSecret\nTestUser\nTestPass')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.user_pass_auth.assert_called_once_with(client_id='TestClient', client_secret='TestSecret', username='TestUser', password='TestPass')

        self.mock_config_parser.write_config_from_dict.assert_called_once_with({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'token': '123',
                        'auth_mode': 'token'
                    }
                }
            }
        }, self.default_config_path)
    
    def test_login_without_args_prompts_for_client_and_user_save_creds(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--save-creds'], input='TestClient\nTestSecret\nTestUser\nTestPass')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.user_pass_auth.assert_called_once_with(client_id='TestClient', client_secret='TestSecret', username='TestUser', password='TestPass')

        self.mock_config_parser.write_config_from_dict.assert_called_once_with({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'auth_mode': 'oauth',
                        'client_id': 'TestClient',
                        'client_secret': 'TestSecret',
                        'username': 'TestUser',
                        'password': 'TestPass'
                    }
                }
            }
        }, self.default_config_path)

    def test_login_without_args_prompts_for_client_and_user_then_print_token(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--print'], input='TestClient\nTestSecret\nTestUser\nTestPass')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.user_pass_auth.assert_called_once_with(client_id='TestClient', client_secret='TestSecret', username='TestUser', password='TestPass')
        # Output will include prompt inputs so grab last line
        self.assertEqual(result.output.splitlines()[-1], '123')
        self.mock_config_parser.write_config_from_dict.assert_not_called()

    def test_login_with_client_id_prompts_for_secret(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--client', 'TestClient'], input='TestSecret')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.client_credentials_auth.assert_called_once_with(client_id='TestClient', client_secret='TestSecret')

        self.mock_config_parser.write_config_from_dict.assert_called_once_with({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'token': '123',
                        'auth_mode': 'token'
                    }
                }
            }
        }, self.default_config_path)
    
    def test_login_with_client_id_prompts_for_secret_save_creds(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--client', 'TestClient', '--save-creds'], input='TestSecret')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.client_credentials_auth.assert_called_once_with(client_id='TestClient', client_secret='TestSecret')

        self.mock_config_parser.write_config_from_dict.assert_called_once_with({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'auth_mode': 'oauth',
                        'client_id': 'TestClient',
                        'client_secret': 'TestSecret'
                    }
                }
            }
        }, self.default_config_path)
    
    def test_login_with_client_id_prompts_for_secret_then_print_token(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--client', 'TestClient', '--print'], input='TestSecret')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.client_credentials_auth.assert_called_once_with(client_id='TestClient', client_secret='TestSecret')
        
        # Output will include prompt inputs so grab last line
        self.assertEqual(result.output.splitlines()[-1], '123')
        self.mock_config_parser.write_config_from_dict.assert_not_called()
    
    def test_login_with_client_id_and_secret(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--client', 'TestClient', '--client-secret', 'TestSecret'])
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.client_credentials_auth.assert_called_once_with(client_id='TestClient', client_secret='TestSecret')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'token': '123',
                        'auth_mode': 'token'
                    }
                }
            }
        }, self.default_config_path)

    def test_login_with_client_id_and_secret_save_creds(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--client', 'TestClient', '--client-secret', 'TestSecret', '--save-creds'])
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.client_credentials_auth.assert_called_once_with(client_id='TestClient', client_secret='TestSecret')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'client_id': 'TestClient',
                        'client_secret': 'TestSecret'
                    }
                }
            }
        }, self.default_config_path)

    def test_login_with_client_id_and_secret_then_print_token(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--client', 'TestClient', '--client-secret', 'TestSecret', '--print'])
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.client_credentials_auth.assert_called_once_with(client_id='TestClient', client_secret='TestSecret')

        self.assert_output(result, '123')
        self.mock_config_parser.write_config_from_dict.assert_not_called()

    def test_login_with_username_prompts_for_pwd(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--username', 'TestUser'], input='TestPass')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.legacy_user_pass_auth.assert_called_once_with(username='TestUser', password='TestPass', legacy_auth_address='http://auth.example.com')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'token': '123',
                        'auth_mode': 'token'
                    }
                }
            }
        }, self.default_config_path)
    
    def test_login_with_username_prompts_for_pwd_save_creds(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--username', 'TestUser', '--save-creds'], input='TestPass')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.legacy_user_pass_auth.assert_called_once_with(username='TestUser', password='TestPass', legacy_auth_address='http://auth.example.com')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'username': 'TestUser',
                        'password': 'TestPass',
                        'auth_address': 'http://auth.example.com'
                    }
                }
            }
        }, self.default_config_path)
    
    def test_login_with_username_prompts_for_pwd_then_print_token(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--username', 'TestUser', '--print'], input='TestPass')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.legacy_user_pass_auth.assert_called_once_with(username='TestUser', password='TestPass', legacy_auth_address='http://auth.example.com')

        # Output will include prompt inputs so grab last line
        self.assertEqual(result.output.splitlines()[-1], '123')
        self.mock_config_parser.write_config_from_dict.assert_not_called()
    
    def test_login_with_username_and_pwd(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--username', 'TestUser', '--pwd', 'TestPass'])
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.legacy_user_pass_auth.assert_called_once_with(username='TestUser', password='TestPass', legacy_auth_address='http://auth.example.com')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'token': '123',
                        'auth_mode': 'token'
                    }
                }
            }
        }, self.default_config_path)
    
    def test_login_with_username_and_pwd_save_creds(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--username', 'TestUser', '--pwd', 'TestPass', '--save-creds'], input='TestPass')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.legacy_user_pass_auth.assert_called_once_with(username='TestUser', password='TestPass', legacy_auth_address='http://auth.example.com')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'username': 'TestUser',
                        'password': 'TestPass',
                        'auth_address': 'http://auth.example.com'
                    }
                }
            }
        }, self.default_config_path)
    
    def test_login_with_username_and_pwd_then_print_token(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--username', 'TestUser', '--pwd', 'TestPass', '--print'])
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.legacy_user_pass_auth.assert_called_once_with(username='TestUser', password='TestPass', legacy_auth_address='http://auth.example.com')

        self.assert_output(result, '123')
        self.mock_config_parser.write_config_from_dict.assert_not_called()

    def test_login_with_username_and_no_auth_address_raises_error(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--username', 'TestUser'])
        
        self.assert_has_system_exit(result)
        expected_output = 'Usage: login [OPTIONS] ADDRESS'
        expected_output += '\nTry \'login --help\' for help.'
        expected_output += '\n'
        expected_output += '\nError: Must specify "--auth-address" option when attempting to authenticate with username/password/api_key but without client/client-secret'
        self.assert_output(result, expected_output)

        self.mock_tnco_client_builder.address.assert_not_called()
        self.mock_tnco_client_builder.legacy_user_pass_auth.assert_not_called()
        self.mock_config_parser.write_config_from_dict.assert_not_called()

    def test_login_with_token(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--token', '123'])
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.token_auth.assert_called_once_with(token='123')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'token': '123',
                        'auth_mode': 'token'
                    }
                }
            }
        }, self.default_config_path)
    
    def test_login_with_token_save_creds(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--token', '123', '--save-creds'])
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.token_auth.assert_called_once_with(token='123')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'token': '123',
                        'auth_mode': 'token'
                    }
                }
            }
        }, self.default_config_path)
    
    def test_login_with_token_then_print_token(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--token', '123', '--print'])
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.token_auth.assert_called_once_with(token='123')

        self.assert_output(result, '123')
        self.mock_config_parser.write_config_from_dict.assert_not_called()

    def test_login_with_name(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--token', '123', '--name', 'testenv'])
        self.assert_no_errors(result)

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'testenv',
            'environments': {
                'testenv': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'token': '123',
                        'auth_mode': 'token'
                    }
                }
            }
        }, self.default_config_path)

    def test_login_with_name_already_exists_prompts_override_confirmation(self):
        self.mock_config_parser.from_file_as_dict.return_value = {
            'environments': {
                'testenv': {}
            }
        }

        result = self.runner.invoke(login, ['http://mock.example.com', '--token', '123', '--name', 'testenv'], input='y')
        self.assert_no_errors(result)

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'testenv',
            'environments': {
                'testenv': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'token': '123',
                        'auth_mode': 'token'
                    }
                }
            }
        }, self.default_config_path)

    def test_login_with_name_already_exists_prompts_override_confirmation_abort_on_no(self):
        clear_global_controller()
        self.mock_config_parser.from_file_as_dict.return_value = {
            'environments': {
                'testenv': {}
            }
        }
        self.mock_get_global_config.return_value = (Config(environments={'testenv': EnvironmentGroup('testenv')}), self.default_config_path)

        result = self.runner.invoke(login, ['http://mock.example.com', '--token', '123', '--name', 'testenv'], input='n')
        self.assert_has_system_exit(result)
        self.mock_config_parser.write_config_from_dict.assert_not_called()

    def test_login_with_zen_username_prompts_for_api_key(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--zen', '--username', 'TestUser'], input='TestApiKey')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.zen_api_key_auth.assert_called_once_with(username='TestUser', api_key='TestApiKey', zen_auth_address='http://auth.example.com')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'token': '123',
                        'auth_mode': 'token'
                    }
                }
            }
        }, self.default_config_path)

    def test_login_with_zen_username_prompts_for_api_key_save_creds(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--zen', '--username', 'TestUser', '--save-creds'], input='TestApiKey')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.zen_api_key_auth.assert_called_once_with(username='TestUser', api_key='TestApiKey', zen_auth_address='http://auth.example.com')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'username': 'TestUser',
                        'api_key': 'TestApiKey',
                        'auth_mode': 'zen',
                        'auth_address': 'http://auth.example.com'
                    }
                }
            }
        }, self.default_config_path)
    
    def test_login_with_zen_username_prompts_for_api_key_then_print_token(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--zen', '--username', 'TestUser', '--print'], input='TestApiKey')
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.zen_api_key_auth.assert_called_once_with(username='TestUser', api_key='TestApiKey', zen_auth_address='http://auth.example.com')

        # Output will include prompt inputs so grab last line
        self.assertEqual(result.output.splitlines()[-1], '123')
        self.mock_config_parser.write_config_from_dict.assert_not_called()

    def test_login_with_zen_username_and_api_key(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--zen', '--username', 'TestUser', '--api-key', 'TestApiKey'])
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.zen_api_key_auth.assert_called_once_with(username='TestUser', api_key='TestApiKey', zen_auth_address='http://auth.example.com')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'token': '123',
                        'auth_mode': 'token'
                    }
                }
            }
        }, self.default_config_path)

    def test_login_with_zen_username_and_api_key_save_creds(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--zen', '--username', 'TestUser', '--api-key', 'TestApiKey', '--save-creds'])
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.zen_api_key_auth.assert_called_once_with(username='TestUser', api_key='TestApiKey', zen_auth_address='http://auth.example.com')

        self.mock_config_parser.write_config_from_dict({
            'active_environment': 'default',
            'environments': {
                'default': {
                    'tnco': {
                        'address': 'http://mock.example.com',
                        'secure': True,
                        'username': 'TestUser',
                        'api_key': 'TestApiKey',
                        'auth_mode': 'zen',
                        'auth_address': 'http://auth.example.com'
                    }
                }
            }
        }, self.default_config_path)
    
    def test_login_with_zen_username_prompts_and_api_key_then_print_token(self):
        result = self.runner.invoke(login, ['http://mock.example.com', '--auth-address', 'http://auth.example.com', '--zen', '--username', 'TestUser', '--api-key', 'TestApiKey', '--print'])
        self.assert_no_errors(result)
        self.mock_tnco_client_builder.address.assert_called_once_with('http://mock.example.com')
        self.mock_tnco_client_builder.zen_api_key_auth.assert_called_once_with(username='TestUser', api_key='TestApiKey', zen_auth_address='http://auth.example.com')

        # Output will include prompt inputs so grab last line
        self.assertEqual(result.output.splitlines()[-1], '123')
        self.mock_config_parser.write_config_from_dict.assert_not_called()
    
    