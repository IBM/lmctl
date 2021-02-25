import unittest
import unittest.mock as mock
from lmctl.environment import EnvironmentConfigError, EnvironmentRuntimeError, LmEnvironment, LmSessionConfig, LmSession
from lmctl.client import TNCOClient, LegacyUserPassAuth, UserPassAuth, ClientCredentialsAuth, ZenAPIKeyAuth

class TestLmEnvironment(unittest.TestCase):

    def test_init_fails_when_name_is_none(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            LmEnvironment(None, host='', port=80)
        self.assertEqual(str(context.exception), 'LM environment must be configured with "name" property')

    def test_init_fails_when_address_and_host_are_none(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            LmEnvironment('lm')
        self.assertEqual(str(context.exception), 'LM environment must be configured with either "address" or "host" property ("port" and "protocol" will be used to build up the full address when using "host")')

    def test_init_fails_when_secure_and_credentials_not_set(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            LmEnvironment('lm', host='test', port=80, secure=True)
        self.assertEqual(str(context.exception), 'Secure LM environment must be configured with either "client_id" or "username" property when using "auth_mode=oauth". If the LM environment is not secure then set "secure" to False')

    def test_init_defaults_port_and_protocol_and_path(self):
        config = LmEnvironment('lm', host='test')
        self.assertEqual(config.address, 'https://test')

    def test_init_auth_defaults_auth_address(self):
        config = LmEnvironment('lm', 'test', 80, secure=True, username='test')
        self.assertEqual(config.auth_address, 'https://test:80')

    def test_init_auth_defaults_auth_mode(self):
        config = LmEnvironment('lm', 'test', 80, secure=True, username='test')
        self.assertEqual(config.auth_mode, 'oauth')

    def test_init_with_password(self):
        config = LmEnvironment('lm', host='test', port=80, secure=True, username='test', password='secret')
        self.assertEqual(config.username, 'test')
        self.assertEqual(config.password, 'secret')

    def test_init_with_all_as_parts(self):
        config = LmEnvironment('lm', host='test', port=80, protocol='http', path='gateway', secure=True, username='user', password='secret', auth_host='auth', auth_port=81, auth_protocol='https', brent_name='alt_brent')
        self.assertEqual(config.name, 'lm')
        self.assertEqual(config.address, 'http://test:80/gateway')
        self.assertEqual(config.auth_address, 'https://auth:81')
        self.assertEqual(config.secure, True)
        self.assertEqual(config.username, 'user')
        self.assertEqual(config.brent_name, 'alt_brent')

    def test_set_defaults_when_none(self):
        config = LmEnvironment('lm', host='test', port=None, protocol=None, path=None, secure=True, username='user', auth_host=None, auth_port=None, auth_protocol=None, brent_name=None)
        self.assertEqual(config.name, 'lm')
        self.assertEqual(config.address, 'https://test')
        self.assertEqual(config.secure, True)
        self.assertEqual(config.username, 'user')
        self.assertEqual(config.auth_address, 'https://test')
        self.assertEqual(config.brent_name, 'brent')

    def test_set_defaults_when_empty(self):
        config = LmEnvironment('lm', host='test', port=' ', protocol=' ', path=' ', secure=True, username='user', auth_host=' ', auth_port=' ', auth_protocol=' ', brent_name=' ')
        self.assertEqual(config.name, 'lm')
        self.assertEqual(config.address, 'https://test')
        self.assertEqual(config.auth_address, 'https://test')
        self.assertEqual(config.secure, True)
        self.assertEqual(config.username, 'user')
        self.assertEqual(config.brent_name, 'brent')

    def test_init_with_address(self):
        config = LmEnvironment('lm', address='https://test:8080/api')
        self.assertEqual(config.address, 'https://test:8080/api')
        self.assertEqual(config.auth_address, 'https://test:8080/api')
        self.assertEqual(config.kami_address, 'http://test:31289')

    def test_is_secure(self):
        insecure_env = LmEnvironment('lm', host='test', port=80)
        self.assertFalse(insecure_env.is_secure)
        secure_env = LmEnvironment('lm', host='test', port=80, secure=True, username='user')
        self.assertTrue(secure_env.is_secure)

    def test_address_from_parts(self):
        env = LmEnvironment('lm', host='test')
        self.assertEqual(env.address, 'https://test')
        env = LmEnvironment('lm', host='test', port=32455)
        self.assertEqual(env.address, 'https://test:32455')
        env = LmEnvironment('lm', host='test', port=32455, protocol='http')
        self.assertEqual(env.address, 'http://test:32455')
        env = LmEnvironment('lm', host='test', port=None, protocol='http')
        self.assertEqual(env.address, 'http://test')
        env = LmEnvironment('lm', host='test', port=None, protocol='http', path='gateway')
        self.assertEqual(env.address, 'http://test/gateway')
        env = LmEnvironment('lm', host='test', port=32455, protocol='http', path='gateway')
        self.assertEqual(env.address, 'http://test:32455/gateway')

    def test_auth_address_from_parts(self):
        env = LmEnvironment('lm', host='test', port=80, protocol='http', secure=True, username='user', auth_host='auth', auth_port=82, auth_protocol='https')
        self.assertEqual(env.auth_address, 'https://auth:82')

    def test_kami_address_from_parts(self):
        env = LmEnvironment('lm', host='test', port=80, protocol='http', secure=True, username='user', auth_host='auth', auth_port=82, auth_protocol='https')
        self.assertEqual(env.kami_address, 'http://test:31289')

    def test_kami_address_override_port(self):
        env = LmEnvironment('lm', address='http://test:8080', kami_port=5678)
        self.assertEqual(env.kami_address, 'http://test:5678')

    def test_kami_address_override_protocol(self):
        env = LmEnvironment('lm', address='http://test:8080', kami_protocol='https')
        self.assertEqual(env.kami_address, 'https://test:31289')

    def test_zen_auth_mode(self):
        env = LmEnvironment('lm', address='http://test:8080', secure=True, auth_mode='zen', username='Zenny', api_key='12345', auth_address='http://zen:8000/api')
        self.assertEqual(env.auth_mode, 'zen')
        self.assertEqual(env.username, 'Zenny')
        self.assertEqual(env.api_key, '12345')
        self.assertEqual(env.auth_address, 'http://zen:8000/api')
        
    def test_zen_auth_missing_username(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            LmEnvironment('lm', address='http://test:8080', secure=True, auth_mode='zen', auth_address='http://zen:8000/api')
        self.assertEqual(str(context.exception), 'Secure LM environment must be configured with a "username" property when using "auth_mode=zen". If the LM environment is not secure then set "secure" to False')

    def test_zen_auth_missing_auth_address(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            LmEnvironment('lm', address='http://test:8080', secure=True, auth_mode='zen', username='user', api_key='API')
        self.assertEqual(str(context.exception), 'Secure LM environment must be configured with Zen authentication address on the "auth_address" property (or "auth_host"/"auth_port"/"auth_protocol") when using "auth_mode=zen". If the LM environment is not secure then set "secure" to False')

    def test_invalid_use_of_api_key_when_in_oauth_mode(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            LmEnvironment('lm', address='http://test:8080', secure=True, auth_mode='oauth', username='user', api_key='API')
        self.assertEqual(str(context.exception), 'Secure LM environment cannot be configured with "api_key" when using "auth_mode=oauth". If the LM environment is not secure then set "secure" to False')

    def test_create_session_config(self):
        env = LmEnvironment('lm', address='http://test')
        session_config = env.create_session_config()
        self.assertIsInstance(session_config, LmSessionConfig)
        self.assertEqual(session_config.env, env)
        self.assertEqual(session_config.username, None)
        self.assertEqual(session_config.password, None)

    def test_create_session_config_with_username_password(self):
        env = LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, username='user')
        session_config = env.create_session_config()
        self.assertEqual(session_config.username, 'user')
        self.assertEqual(session_config.password, None)
        env = LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, username='user', password='secret')
        session_config = env.create_session_config()
        self.assertEqual(session_config.username, 'user')
        self.assertEqual(session_config.password, 'secret')
        self.assertEqual(session_config.auth_mode, 'oauth')

    def test_create_session_config_with_client_credentials(self):
        env = LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, client_id='client', client_secret='secret')
        session_config = env.create_session_config()
        self.assertEqual(session_config.client_id, 'client')
        self.assertEqual(session_config.client_secret, 'secret')
        self.assertEqual(session_config.auth_mode, 'oauth')

    def test_create_session_config_with_zen_auth(self):
        env = LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, username='user', api_key='key', auth_address='http://zen:80', auth_mode='zen')
        session_config = env.create_session_config()
        self.assertEqual(session_config.username, 'user')
        self.assertEqual(session_config.api_key, 'key')
        self.assertEqual(session_config.auth_mode, 'zen')

    def test_build_client_sets_address(self):
        config = LmEnvironment('lm',
                         host='test', 
                         port=80, 
                         protocol='http', 
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
        self.assertEqual(client.address, 'http://test:80/gateway')
        self.assertEqual(client.kami_address, 'http://test:31289')

    def test_build_client_legacy_auth(self):
        config = LmEnvironment('lm',
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
        config = LmEnvironment('lm',
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
    
    def test_build_client_credentials_auth(self):
        config = LmEnvironment('lm',
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
        config = LmEnvironment('lm',
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

class TestLmSessionConfig(unittest.TestCase):

    def test_create(self):
        env = LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, username='user', password='secret')
        session_config = env.create_session_config()
        session = session_config.create()
        self.assertIsInstance(session, LmSession)
        self.assertEqual(session.env, env)
        self.assertEqual(session.username, 'user')
        self.assertEqual(session.password, 'secret')

class TestLmSession(unittest.TestCase):

    def test_init(self):
        env = LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, username='user', password='secret')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        self.assertEqual(session.env, env)
        self.assertEqual(session.username, 'user')
        self.assertEqual(session.password, 'secret')

    def test_init_fails_without_config(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            LmSession(None)
        self.assertEqual(str(context.exception), 'config not provided to session')

    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_legacy_auth(self, mock_client_builder_init):
        env = LmEnvironment('lm', address='http://api:80', secure=True, username='user', password='secret', auth_address='http://auth:81')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.legacy_user_pass_auth.assert_called_once_with(username='user', password='secret', legacy_auth_address='http://auth:81')
        mock_client_builder.user_pass_auth.assert_not_called()
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.zen_api_key_auth.assert_not_called()
    
    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_legacy_auth_on_default_address(self, mock_client_builder_init):
        env = LmEnvironment('lm', address='http://api:80', secure=True, username='user', password='secret')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.legacy_user_pass_auth.assert_called_once_with(username='user', password='secret', legacy_auth_address='http://api:80')
        mock_client_builder.user_pass_auth.assert_not_called()
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.zen_api_key_auth.assert_not_called()
    
    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_user_pass_auth(self, mock_client_builder_init):
        env = LmEnvironment('lm', address='http://api:80', secure=True, username='user', password='secret', client_id='UserClient', client_secret='c_secret', auth_address='http://auth:81')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('http://auth:81')
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.user_pass_auth.assert_called_once_with(username='user', password='secret', client_id='UserClient', client_secret='c_secret')
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.zen_api_key_auth.assert_not_called()

    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_user_pass_auth_on_default_address(self, mock_client_builder_init):
        env = LmEnvironment('lm', address='http://api:80', secure=True, username='user', password='secret', client_id='UserClient', client_secret='c_secret')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('http://api:80')
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.user_pass_auth.assert_called_once_with(username='user', password='secret', client_id='UserClient', client_secret='c_secret')
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.zen_api_key_auth.assert_not_called()
    
    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_client_auth(self, mock_client_builder_init):
        env = LmEnvironment('lm', address='http://api:80', secure=True, client_id='UserClient', client_secret='c_secret', auth_address='http://auth:81')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('http://auth:81')
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.user_pass_auth.assert_not_called()
        mock_client_builder.client_credentials_auth.assert_called_once_with(client_id='UserClient', client_secret='c_secret')
        mock_client_builder.zen_api_key_auth.assert_not_called()

    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_client_auth_on_default_address(self, mock_client_builder_init):
        env = LmEnvironment('lm', address='http://api:80', secure=True, client_id='UserClient', client_secret='c_secret')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('http://api:80')
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.user_pass_auth.assert_not_called()
        mock_client_builder.client_credentials_auth.assert_called_once_with(client_id='UserClient', client_secret='c_secret')
        mock_client_builder.zen_api_key_auth.assert_not_called()

    @mock.patch('lmctl.environment.lmenv.lm_drivers.security.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_zen_auth(self, mock_client_builder_init):
        env = LmEnvironment('lm', address='http://api:80', secure=True, username='user', api_key='123', auth_mode='zen', auth_address='http://zen:81')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('http://zen:81')
        mock_client_builder.legacy_user_pass_auth.assert_not_called()
        mock_client_builder.user_pass_auth.assert_not_called()
        mock_client_builder.client_credentials_auth.assert_not_called()
        mock_client_builder.zen_api_key_auth.assert_called_once_with(username='user', api_key='123', zen_auth_address='http://zen:81')

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDescriptorDriver')
    def test_descriptor_driver(self, descriptor_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https'), None, auth_mode='oauth'))
        driver = session.descriptor_driver
        descriptor_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, descriptor_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDescriptorDriver')
    def test_descriptor_driver_with_security(self, descriptor_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret', auth_mode='oauth'))
        driver = session.descriptor_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', username='user', password='secret', client_id=None, client_secret=None, api_key=None, auth_mode='oauth')
        descriptor_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, descriptor_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmOnboardRmDriver')
    def test_onboard_rm_driver(self, onboard_rm_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https'), None))
        driver = session.onboard_rm_driver
        onboard_rm_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, onboard_rm_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmOnboardRmDriver')
    def test_onboard_rm_driver_with_security(self, onboard_rm_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret', auth_mode='oauth'))
        driver = session.onboard_rm_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', username='user', password='secret', client_id=None, client_secret=None, api_key=None, auth_mode='oauth')
        onboard_rm_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, onboard_rm_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmTopologyDriver')
    def test_topology_driver(self, topology_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https'), None))
        driver = session.topology_driver
        topology_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, topology_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmTopologyDriver')
    def test_topology_driver_with_security(self, topology_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret', auth_mode='oauth'))
        driver = session.topology_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', username='user', password='secret', client_id=None, client_secret=None, api_key=None, auth_mode='oauth')
        topology_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, topology_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmBehaviourDriver')
    def test_behaviour_driver(self, behaviour_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https'), None))
        driver = session.behaviour_driver
        behaviour_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, behaviour_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmBehaviourDriver')
    def test_behaviour_driver_with_security(self, behaviour_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret', auth_mode='oauth'))
        driver = session.behaviour_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', username='user', password='secret', client_id=None, client_secret=None, api_key=None, auth_mode='oauth')
        behaviour_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, behaviour_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDeploymentLocationDriver')
    def test_deployment_location_driver(self, deployment_location_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https'), None))
        driver = session.deployment_location_driver
        deployment_location_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, deployment_location_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDeploymentLocationDriver')
    def test_deployment_location_driver_with_security(self, deployment_location_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret', auth_mode='oauth'))
        driver = session.deployment_location_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', username='user', password='secret', client_id=None, client_secret=None, api_key=None, auth_mode='oauth')
        deployment_location_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, deployment_location_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmInfrastructureKeysDriver')
    def test_infrastructure_keys_driver(self, infrastructure_keys_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https'), None))
        driver = session.infrastructure_keys_driver
        infrastructure_keys_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, infrastructure_keys_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmInfrastructureKeysDriver')
    def test_infrastructure_keys_driver_with_security(self, infrastructure_keys_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret', auth_mode='oauth'))
        driver = session.infrastructure_keys_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', username='user', password='secret', client_id=None, client_secret=None, api_key=None, auth_mode='oauth')
        infrastructure_keys_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, infrastructure_keys_driver_init.return_value)
