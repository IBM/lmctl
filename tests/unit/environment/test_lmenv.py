import unittest
import unittest.mock as mock
import os
from pydantic import ValidationError
from lmctl.environment import TNCOEnvironment, LmSessionConfig, LmSession, ALLOW_ALL_SCHEMES_ENV_VAR
from lmctl.client import TNCOClient, LegacyUserPassAuth, UserPassAuth, ClientCredentialsAuth, JwtTokenAuth, ZenAPIKeyAuth, OktaUserPassAuth

class TestTNCOEnvironment(unittest.TestCase):
    maxDiff = None

    def test_minimum_init(self):
        config = TNCOEnvironment(address='testing')
        self.assertEqual(config.address, 'https://testing')
        self.assertEqual(config.secure, False)
        # Defaults
        self.assertEqual(config.brent_name, 'brent')
        self.assertEqual(config.protocol, 'https')
        self.assertEqual(config.auth_protocol, 'https')
        self.assertEqual(config.kami_port, '31289')
        self.assertEqual(config.kami_protocol, 'http')
        
    def test_init_fails_when_address_and_host_are_none(self):
        with self.assertRaises(ValidationError) as context:
            config = TNCOEnvironment(host=None)
        self.assertEqual(str(context.exception).split('[type=value_error')[0].strip(), '1 validation error for TNCOEnvironment\n  Value error, TNCO environment cannot be configured without "address" property or "host" property')

    def test_init_fails_when_secure_and_credentials_not_set(self):
        with self.assertRaises(ValidationError) as context:
            config = TNCOEnvironment(host='test', port=80, secure=True)
        self.assertEqual(str(context.exception).split('[type=value_error')[0].strip(), '1 validation error for TNCOEnvironment\n  Value error, Secure TNCO environment must be configured with either "client_id" or "username" property when using "auth_mode=oauth". If the TNCO environment is not secure then set "secure" to False')

    def test_init_defaults_port_and_protocol_and_path(self):
        config = TNCOEnvironment(host='test')
        self.assertEqual(config.address, 'https://test')

    def test_init_auth_defaults_auth_address(self):
        config = TNCOEnvironment(host='test', port=80, secure=True, username='test')
        self.assertEqual(config.auth_address, 'https://test:80')

    def test_init_auth_defaults_auth_mode(self):
        config = TNCOEnvironment(host='test', port=80, secure=True, username='test')
        self.assertEqual(config.auth_mode, 'oauth')

    def test_init_with_password(self):
        config = TNCOEnvironment(host='test', port=80, secure=True, username='test', password='secret')
        self.assertEqual(config.username, 'test')
        self.assertEqual(config.password, 'secret')

    def test_init_with_all_as_parts(self):
        config = TNCOEnvironment(host='test', port=80, protocol='https', path='gateway', secure=True, username='user', password='secret', auth_host='auth', auth_port=81, auth_protocol='https', brent_name='alt_brent')
        
        self.assertEqual(config.address, 'https://test:80/gateway')
        self.assertEqual(config.auth_address, 'https://auth:81')
        self.assertEqual(config.secure, True)
        self.assertEqual(config.username, 'user')
        self.assertEqual(config.brent_name, 'alt_brent')

    def test_init_with_address(self):
        config = TNCOEnvironment(address='https://test:8080/api')
        self.assertEqual(config.address, 'https://test:8080/api')
        self.assertEqual(config.auth_address, 'https://test:8080/api')
        self.assertEqual(config.kami_address, 'http://test:31289')

    def test_init_with_http_address_fails(self):
        with self.assertRaises(ValueError) as ctx:
            TNCOEnvironment(address='http://cp4na-o-ishtar.example.com')
        self.assertEqual(str(ctx.exception).split('[type=value_error')[0].strip(), '1 validation error for TNCOEnvironment\n  Value error, Use of "http" scheme is not encouraged by lmctl, use "https" instead (http://cp4na-o-ishtar.example.com)')
        with self.assertRaises(ValueError) as ctx:
            TNCOEnvironment(host='cp4na-o-ishtar.example.com', port=80, protocol='http')
        self.assertEqual(str(ctx.exception).split('[type=value_error')[0].strip(), '1 validation error for TNCOEnvironment\n  Value error, Use of "http" scheme is not encouraged by lmctl, use "https" instead (http://cp4na-o-ishtar.example.com:80)')
    
    def test_init_with_http_auth_address_fails(self):
        with self.assertRaises(ValueError) as ctx:
            TNCOEnvironment(address='https://cp4na-o-ishtar.example.com', auth_address='http://cp4na-o-auth.example.com')
        self.assertEqual(str(ctx.exception).split('[type=value_error')[0].strip(), '1 validation error for TNCOEnvironment\n  Value error, Use of "http" scheme is not encouraged by lmctl, use "https" instead (http://cp4na-o-auth.example.com)')
        with self.assertRaises(ValueError) as ctx:
            TNCOEnvironment(host='cp4na-o-ishtar.example.com', port=80, protocol='https', auth_host='cp4na-o-auth.example.com', auth_protocol='http')
        self.assertEqual(str(ctx.exception).split('[type=value_error')[0].strip(), '1 validation error for TNCOEnvironment\n  Value error, Use of "http" scheme is not encouraged by lmctl, use "https" instead (http://cp4na-o-auth.example.com)')
    
    def test_init_with_http_address_allowed_when_env_var_set(self):
        previous_env_var_value = os.environ.get(ALLOW_ALL_SCHEMES_ENV_VAR, '')
        os.environ[ALLOW_ALL_SCHEMES_ENV_VAR] = 'true'
        try:
            env = TNCOEnvironment(address='http://cp4na-o-ishtar.example.com')
            self.assertEqual(env.address, 'http://cp4na-o-ishtar.example.com')
            
            env = TNCOEnvironment(host='cp4na-o-ishtar.example.com', port=80, protocol='http')
            self.assertEqual(env.address, 'http://cp4na-o-ishtar.example.com:80')
        finally:
            os.environ[ALLOW_ALL_SCHEMES_ENV_VAR] = previous_env_var_value

    def test_init_with_http_auth_address_allowed_when_env_var_set(self):
        previous_env_var_value = os.environ.get(ALLOW_ALL_SCHEMES_ENV_VAR, '')
        os.environ[ALLOW_ALL_SCHEMES_ENV_VAR] = 'true'
        try:
            env = TNCOEnvironment(address='https://cp4na-o-ishtar.example.com', auth_address='http://cp4na-o-auth.example.com')
            self.assertEqual(env.address, 'https://cp4na-o-ishtar.example.com')
            self.assertEqual(env.auth_address, 'http://cp4na-o-auth.example.com')
            
            env = TNCOEnvironment(host='cp4na-o-ishtar.example.com', port=80, protocol='https', auth_host='cp4na-o-auth.example.com', auth_protocol='http')
            self.assertEqual(env.address, 'https://cp4na-o-ishtar.example.com:80')
            self.assertEqual(env.auth_address, 'http://cp4na-o-auth.example.com')
        finally:
            os.environ[ALLOW_ALL_SCHEMES_ENV_VAR] = previous_env_var_value

    def test_is_secure(self):
        insecure_env = TNCOEnvironment(host='test', port=80)
        self.assertFalse(insecure_env.secure)
        secure_env = TNCOEnvironment(host='test', port=80, secure=True, username='user')
        self.assertTrue(secure_env.secure)

    def test_address_from_parts(self):
        env = TNCOEnvironment(host='test')
        self.assertEqual(env.address, 'https://test')
        env = TNCOEnvironment(host='test', port=32455)
        self.assertEqual(env.address, 'https://test:32455')
        env = TNCOEnvironment(host='test', port=32455, protocol='https')
        self.assertEqual(env.address, 'https://test:32455')
        env = TNCOEnvironment(host='test', port=None, protocol='https')
        self.assertEqual(env.address, 'https://test')
        env = TNCOEnvironment(host='test', port=None, protocol='https', path='gateway')
        self.assertEqual(env.address, 'https://test/gateway')
        env = TNCOEnvironment(host='test', port=32455, protocol='https', path='gateway')
        self.assertEqual(env.address, 'https://test:32455/gateway')

    def test_auth_address_from_parts(self):
        env = TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port='82', auth_protocol='https')
        print("************env", env)
        self.assertEqual(env.auth_address, 'https://auth:82')

    def test_kami_address_from_parts(self):
        env = TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port='82', auth_protocol='https')
        self.assertEqual(env.kami_address, 'http://test:31289')

    def test_kami_address_override_port(self):
        env = TNCOEnvironment(address='https://test:8080', kami_port=5678)
        self.assertEqual(env.kami_address, 'http://test:5678')

    def test_kami_address_override_protocol(self):
        env = TNCOEnvironment(address='https://test:8080', kami_protocol='https')
        self.assertEqual(env.kami_address, 'https://test:31289')

    def test_zen_auth_mode(self):
        env = TNCOEnvironment(address='https://test:8080', secure=True, auth_mode='zen', username='Zenny', api_key='12345', auth_address='https://zen:8000/api')
        self.assertEqual(env.auth_mode, 'zen')
        self.assertEqual(env.username, 'Zenny')
        self.assertEqual(env.api_key, '12345')
        self.assertEqual(env.auth_address, 'https://zen:8000/api')
        
    def test_zen_auth_missing_username(self):
        with self.assertRaises(ValidationError) as context:
            TNCOEnvironment(address='https://test:8080', secure=True, auth_mode='zen', auth_address='https://zen:8000/api')
        self.assertEqual(str(context.exception).split('[type=value_error')[0].strip(), '1 validation error for TNCOEnvironment\n  Value error, Secure TNCO environment must be configured with a "username" property when using "auth_mode=zen". If the TNCO environment is not secure then set "secure" to False')

    def test_zen_auth_missing_auth_address(self):
        with self.assertRaises(ValidationError) as context:
            TNCOEnvironment(address='https://test:8080', secure=True, auth_mode='zen', username='user', api_key='API')
        self.assertEqual(str(context.exception).split('[type=value_error')[0].strip(), '1 validation error for TNCOEnvironment\n  Value error, Secure TNCO environment must be configured with Zen authentication address on the "auth_address" property (or "auth_host"/"auth_port"/"auth_protocol") when using "auth_mode=zen". If the TNCO environment is not secure then set "secure" to False')

    def test_invalid_use_of_api_key_when_in_oauth_mode(self):
        with self.assertRaises(ValidationError) as context:
            TNCOEnvironment(address='https://test:8080', secure=True, auth_mode='oauth', username='user', api_key='API')
        self.assertEqual(str(context.exception).split('[type=value_error')[0].strip(), '1 validation error for TNCOEnvironment\n  Value error, Secure TNCO environment cannot be configured with "api_key" when using "auth_mode=oauth". Use "client_id/client_secret" or "username/password" combination or set "auth_mode" to "zen". If the TNCO environment is not secure then set "secure" to False')
    
    def test_token_auth_mode(self):
        env = TNCOEnvironment(address='https://test:8080', secure=True, auth_mode='token', token='123')
        self.assertEqual(env.auth_mode, 'token')
        self.assertEqual(env.token, '123')

    def test_create_session_config(self):
        env = TNCOEnvironment(address='https://test')
        session_config = env.create_session_config()
        self.assertIsInstance(session_config, LmSessionConfig)
        self.assertEqual(session_config.env, env)
        self.assertEqual(session_config.username, None)
        self.assertEqual(session_config.password, None)

    def test_create_session_config_with_username_password(self):
        env = TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user')
        session_config = env.create_session_config()
        self.assertEqual(session_config.username, 'user')
        self.assertEqual(session_config.password, None)
        env = TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', password='secret')
        session_config = env.create_session_config()
        self.assertEqual(session_config.username, 'user')
        self.assertEqual(session_config.password, 'secret')
        self.assertEqual(session_config.auth_mode, 'oauth')

    def test_create_session_config_with_client_credentials(self):
        env = TNCOEnvironment(host='test', port=80, protocol='https', secure=True, client_id='client', client_secret='secret')
        session_config = env.create_session_config()
        self.assertEqual(session_config.client_id, 'client')
        self.assertEqual(session_config.client_secret, 'secret')
        self.assertEqual(session_config.auth_mode, 'oauth')

    def test_create_session_config_with_zen_auth(self):
        env = TNCOEnvironment(name='lm', host='test', port=80, protocol='https', secure=True, username='user', api_key='key', auth_address='https://zen:80', auth_mode='zen')
        session_config = env.create_session_config()
        self.assertEqual(session_config.username, 'user')
        self.assertEqual(session_config.api_key, 'key')
        self.assertEqual(session_config.auth_mode, 'zen')
    
    def test_create_session_config_with_token_auth(self):
        env = TNCOEnvironment(host='test', port=80, protocol='https', secure=True, auth_mode='token', token='123')
        session_config = env.create_session_config()
        self.assertEqual(session_config.token, '123')
        self.assertEqual(session_config.auth_mode, 'token')

    def test_build_client_sets_address(self):
        config = TNCOEnvironment(
                         host='test', 
                         port=80, 
                         protocol='https', 
                         path='gateway', 
                         secure=True, 
                         username='user', 
                         password='secret', 
                         auth_host='auth', 
                         auth_port=81, 
                         auth_protocol='https'
                         )
        client = config.build_client()
        self.assertIsInstance(client, TNCOClient)
        self.assertEqual(client.address, 'https://test:80/gateway')
        self.assertEqual(client.kami_address, 'http://test:31289')

    def test_build_client_legacy_auth(self):
        config = TNCOEnvironment(
                         address='https://testing',
                         secure=True, 
                         username='user', 
                         password='secret', 
                         auth_host='auth', 
                         auth_port=81, 
                         auth_protocol='https'
                         )
        client = config.build_client()
        self.assertIsInstance(client, TNCOClient)
        self.assertIsInstance(client.auth_type, LegacyUserPassAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.password, 'secret')
        self.assertEqual(client.auth_type.legacy_auth_address, 'https://auth:81')

    def test_build_client_user_pass_auth(self):
        config = TNCOEnvironment(
                         address='https://testing',
                         secure=True, 
                         client_id='TNCOClient',
                         client_secret='sosecret',
                         username='user', 
                         password='secret'
                         )
        client = config.build_client()
        self.assertIsInstance(client, TNCOClient)
        self.assertIsInstance(client.auth_type, UserPassAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.password, 'secret')
        self.assertEqual(client.auth_type.client_id, 'TNCOClient')
        self.assertEqual(client.auth_type.client_secret, 'sosecret')

    def test_build_client_okta_user_pass_auth(self):
        config = TNCOEnvironment(
                         address='https://testing',
                         secure=True,
                         client_id='TNCOClient',
                         client_secret='sosecret',
                         username='user',
                         password='secret',
                         auth_mode='okta',
                         auth_server_id='default',
                         scope='test'
                         )
        client = config.build_client()
        self.assertIsInstance(client, TNCOClient)
        self.assertIsInstance(client.auth_type, OktaUserPassAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.password, 'secret')
        self.assertEqual(client.auth_type.client_id, 'TNCOClient')
        self.assertEqual(client.auth_type.client_secret, 'sosecret')

    def test_build_client_credentials_auth(self):
        config = TNCOEnvironment(
                         address='https://testing',
                         secure=True, 
                         client_id='TNCOClient',
                         client_secret='sosecret'
                         )
        client = config.build_client()
        self.assertIsInstance(client, TNCOClient)
        self.assertIsInstance(client.auth_type, ClientCredentialsAuth)
        self.assertEqual(client.auth_type.client_id, 'TNCOClient')
        self.assertEqual(client.auth_type.client_secret, 'sosecret')
    
    def test_build_client_zen_auth(self):
        config = TNCOEnvironment(
                         address='https://testing',
                         secure=True, 
                         auth_mode='zen',
                         username='user', 
                         api_key='secret', 
                         auth_host='auth', 
                         auth_port=81, 
                         auth_protocol='https'
                         )
        client = config.build_client()
        self.assertIsInstance(client, TNCOClient)
        self.assertIsInstance(client.auth_type, ZenAPIKeyAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.api_key, 'secret')
        self.assertEqual(client.auth_type.zen_auth_address, 'https://auth:81')

    def test_build_client_token_auth(self):
        config = TNCOEnvironment(
                         address='https://testing',
                         secure=True, 
                         auth_mode='token',
                         token='123'
                         )
        client = config.build_client()
        self.assertIsInstance(client, TNCOClient)
        self.assertIsInstance(client.auth_type, JwtTokenAuth)
        self.assertEqual(client.auth_type.token, '123')


class TestLmSessionConfig(unittest.TestCase):

    def test_create(self):
        env = TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', password='secret')
        session_config = env.create_session_config()
        session = session_config.create()
        self.assertIsInstance(session, LmSession)
        self.assertEqual(session.env, env)
        self.assertEqual(session.username, 'user')
        self.assertEqual(session.password, 'secret')

class TestLmSession(unittest.TestCase):

    def test_init(self):
        env = TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', password='secret')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        self.assertEqual(session.env, env)
        self.assertEqual(session.username, 'user')
        self.assertEqual(session.password, 'secret')

    def test_init_fails_without_config(self):
        with self.assertRaises(ValueError) as context:
            LmSession(None)
        self.assertEqual(str(context.exception), 'config not provided to session')

    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_legacy_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='https://api:80', secure=True, username='user', password='secret', auth_address='https://auth:81')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.legacy_user_pass_auth.assert_called_once_with(username='user', password='secret', legacy_auth_address='https://auth:81')
        mock_client_builder.user_pass_auth.assert_not_called()
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.zen_api_key_auth.assert_not_called()
    
    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_legacy_auth_on_default_address(self, mock_client_builder_init):
        env = TNCOEnvironment(address='https://api:80', secure=True, username='user', password='secret')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.legacy_user_pass_auth.assert_called_once_with(username='user', password='secret', legacy_auth_address='https://api:80')
        mock_client_builder.user_pass_auth.assert_not_called()
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.zen_api_key_auth.assert_not_called()
    
    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_user_pass_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='https://api:80', secure=True, username='user', password='secret', client_id='UserClient', client_secret='c_secret', auth_address='https://auth:81')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('https://auth:81')
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.user_pass_auth.assert_called_once_with(username='user', password='secret', client_id='UserClient', client_secret='c_secret')
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.zen_api_key_auth.assert_not_called()

    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_okta_user_pass_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='https://api:80', secure=True, username='user', password='secret', client_id='UserClient', client_secret='c_secret', auth_address='https://auth:81', scope='test', auth_server_id='default', auth_mode = 'okta')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value
        mock_client_builder.address.assert_called_once_with('https://auth:81')
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.okta_user_pass_auth.assert_called_once_with(username='user', password='secret', client_id='UserClient', client_secret='c_secret', scope='test', auth_server_id='default', okta_server='https://auth:81')
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.zen_api_key_auth.assert_not_called()

    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_user_pass_auth_on_default_address(self, mock_client_builder_init):
        env = TNCOEnvironment(address='https://api:80', secure=True, username='user', password='secret', client_id='UserClient', client_secret='c_secret')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('https://api:80')
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.user_pass_auth.assert_called_once_with(username='user', password='secret', client_id='UserClient', client_secret='c_secret')
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.zen_api_key_auth.assert_not_called()
    
    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_client_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='https://api:80', secure=True, client_id='UserClient', client_secret='c_secret', auth_address='https://auth:81')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('https://auth:81')
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.user_pass_auth.assert_not_called()
        mock_client_builder.client_credentials_auth.assert_called_once_with(client_id='UserClient', client_secret='c_secret')
        mock_client_builder.zen_api_key_auth.assert_not_called()

    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_client_auth_on_default_address(self, mock_client_builder_init):
        env = TNCOEnvironment(address='https://api:80', secure=True, client_id='UserClient', client_secret='c_secret')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('https://api:80')
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.user_pass_auth.assert_not_called()
        mock_client_builder.client_credentials_auth.assert_called_once_with(client_id='UserClient', client_secret='c_secret')
        mock_client_builder.zen_api_key_auth.assert_not_called()

    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_token_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='https://api:80', secure=True, auth_mode='token', token='123')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with(None)
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.user_pass_auth.assert_not_called()
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.token_auth.assert_called_once_with(token='123')

    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_zen_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='https://api:80', secure=True, username='user', api_key='123', auth_mode='zen', auth_address='https://zen:81')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('https://zen:81')
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.user_pass_auth.assert_not_called()
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.zen_api_key_auth.assert_called_once_with(username='user', api_key='123', zen_auth_address='https://zen:81')

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDescriptorDriver')
    def test_descriptor_driver(self, descriptor_driver_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https'), None, auth_mode='oauth'))
        driver = session.descriptor_driver
        descriptor_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, descriptor_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDescriptorDriver')
    def test_descriptor_driver_with_security(self, descriptor_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='https'), 'user', 'secret', auth_mode='oauth'))
        driver = session.descriptor_driver
        mock_security_ctrl_init.assert_called_once_with('https://auth:81', username='user', password='secret', client_id=None, client_secret=None, token=None, api_key=None, auth_mode='oauth', scope=None, auth_server_id=None)
        descriptor_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, descriptor_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmOnboardRmDriver')
    def test_onboard_rm_driver(self, onboard_rm_driver_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https'), None))
        driver = session.onboard_rm_driver
        onboard_rm_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, onboard_rm_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmOnboardRmDriver')
    def test_onboard_rm_driver_with_security(self, onboard_rm_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='https'), 'user', 'secret', auth_mode='oauth'))
        driver = session.onboard_rm_driver
        mock_security_ctrl_init.assert_called_once_with('https://auth:81', username='user', password='secret', client_id=None, client_secret=None, token=None, api_key=None, auth_mode='oauth', scope=None, auth_server_id=None)
        onboard_rm_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, onboard_rm_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmTopologyDriver')
    def test_topology_driver(self, topology_driver_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https'), None))
        driver = session.topology_driver
        topology_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, topology_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmTopologyDriver')
    def test_topology_driver_with_security(self, topology_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='https'), 'user', 'secret', auth_mode='oauth'))
        driver = session.topology_driver
        mock_security_ctrl_init.assert_called_once_with('https://auth:81', username='user', password='secret', client_id=None, client_secret=None, token=None, api_key=None, auth_mode='oauth', scope=None, auth_server_id=None)
        topology_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, topology_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmBehaviourDriver')
    def test_behaviour_driver(self, behaviour_driver_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https'), None))
        driver = session.behaviour_driver
        behaviour_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, behaviour_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmBehaviourDriver')
    def test_behaviour_driver_with_security(self, behaviour_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='https'), 'user', 'secret', auth_mode='oauth'))
        driver = session.behaviour_driver
        mock_security_ctrl_init.assert_called_once_with('https://auth:81', username='user', password='secret', client_id=None, client_secret=None, token=None, api_key=None, auth_mode='oauth', scope=None, auth_server_id=None)
        behaviour_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, behaviour_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDeploymentLocationDriver')
    def test_deployment_location_driver(self, deployment_location_driver_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https'), None))
        driver = session.deployment_location_driver
        deployment_location_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, deployment_location_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDeploymentLocationDriver')
    def test_deployment_location_driver_with_security(self, deployment_location_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='https'), 'user', 'secret', auth_mode='oauth'))
        driver = session.deployment_location_driver
        mock_security_ctrl_init.assert_called_once_with('https://auth:81', username='user', password='secret', client_id=None, client_secret=None, token=None, api_key=None, auth_mode='oauth', scope=None, auth_server_id=None)
        deployment_location_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, deployment_location_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmInfrastructureKeysDriver')
    def test_infrastructure_keys_driver(self, infrastructure_keys_driver_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https'), None))
        driver = session.infrastructure_keys_driver
        infrastructure_keys_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, infrastructure_keys_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmInfrastructureKeysDriver')
    def test_infrastructure_keys_driver_with_security(self, infrastructure_keys_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='https'), 'user', 'secret', auth_mode='oauth'))
        driver = session.infrastructure_keys_driver
        mock_security_ctrl_init.assert_called_once_with('https://auth:81', username='user', password='secret', client_id=None, client_secret=None, token=None, api_key=None, auth_mode='oauth', scope=None, auth_server_id=None)
        infrastructure_keys_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, infrastructure_keys_driver_init.return_value)
