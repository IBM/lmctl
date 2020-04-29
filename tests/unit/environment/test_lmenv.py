import unittest
import unittest.mock as mock
from lmctl.environment.common import EnvironmentConfigError, EnvironmentRuntimeError
from lmctl.environment.lmenv import LmEnvironment, LmSessionConfig, LmSession

class TestLmEnvironment(unittest.TestCase):

    def test_init_fails_when_name_is_none(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            config = LmEnvironment(None, '', 80)
        self.assertEqual(str(context.exception), 'LM environment cannot be configured without property: name')

    def test_init_fails_when_host_is_none(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            config = LmEnvironment('lm', None, 80)
        self.assertEqual(str(context.exception), 'LM environment cannot be configured without property: host (ip_address)')

    def test_init_fails_when_protocol_unsupported(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            config = LmEnvironment('lm', 'test', 80, 'ftp')
        self.assertEqual(str(context.exception), 'LM environment cannot be configured with unsupported protocol \'ftp\'. Must be one of: [\'http\', \'https\']')

    def test_init_fails_with_unsupported_kwargs(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            config = LmEnvironment('lm', 'test', 80, not_a_key='test')
        self.assertEqual(str(context.exception), 'Unsupported key argument: not_a_key')

    def test_init_fails_when_secure_and_username_is_none(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            config = LmEnvironment('lm', 'test', 80, secure=True)
        self.assertEqual(str(context.exception), 'Secure LM environment cannot be configured without property: username. If the LM environment is not secure then set \'secure\' to False')

    def test_init_defaults_port_and_protocol(self):
        config = LmEnvironment('lm', 'test')
        self.assertEqual(config.port, None)
        self.assertEqual(config.protocol, 'https')

    def test_init_defaults_path(self):
        config = LmEnvironment('lm', 'test')
        self.assertEqual(config.path, None)

    def test_init_auth_defaults_auth_address(self):
        config = LmEnvironment('lm', 'test', 80, secure=True, username='test')
        self.assertEqual(config.auth_host, config.host)
        self.assertEqual(config.auth_port, config.port)
        self.assertEqual(config.auth_protocol, config.auth_protocol)

    def test_init_with_password(self):
        config = LmEnvironment('lm', 'test', 80, secure=True, username='test', password='secret')
        self.assertEqual(config.username, 'test')
        self.assertEqual(config.password, 'secret')

    def test_init_with_all(self):
        config = LmEnvironment('lm', 'test', 80, 'http', path='gateway', secure=True, username='user', password='secret', auth_host='auth', auth_port=81, auth_protocol='https', brent_name='alt_brent')
        self.assertEqual(config.name, 'lm')
        self.assertEqual(config.host, 'test')
        self.assertEqual(config.port, 80)
        self.assertEqual(config.protocol, 'http')
        self.assertEqual(config.path, 'gateway')
        self.assertEqual(config.secure, True)
        self.assertEqual(config.username, 'user')
        self.assertEqual(config.auth_host, 'auth')
        self.assertEqual(config.auth_port, 81)
        self.assertEqual(config.auth_protocol, 'https')
        self.assertEqual(config.brent_name, 'alt_brent')

    def test_set_defaults_when_none(self):
        config = LmEnvironment('lm', 'test', None, None, path=None, secure=True, username='user', auth_host=None, auth_port=None, auth_protocol=None, brent_name=None)
        self.assertEqual(config.name, 'lm')
        self.assertEqual(config.host, 'test')
        self.assertEqual(config.port, None)
        self.assertEqual(config.protocol, 'https')
        self.assertEqual(config.path, None)
        self.assertEqual(config.secure, True)
        self.assertEqual(config.username, 'user')
        self.assertEqual(config.auth_host, 'test')
        self.assertEqual(config.auth_port, None)
        self.assertEqual(config.auth_protocol, 'https')
        self.assertEqual(config.brent_name, 'brent')

    def test_set_defaults_when_empty(self):
        config = LmEnvironment('lm', 'test', ' ', ' ', path=' ', secure=True, username='user', auth_host=' ', auth_port=' ', auth_protocol=' ', brent_name=' ')
        self.assertEqual(config.name, 'lm')
        self.assertEqual(config.host, 'test')
        self.assertEqual(config.port, None)
        self.assertEqual(config.protocol, 'https')
        self.assertEqual(config.path, None)
        self.assertEqual(config.secure, True)
        self.assertEqual(config.username, 'user')
        self.assertEqual(config.auth_host, 'test')
        self.assertEqual(config.auth_port, None)
        self.assertEqual(config.auth_protocol, 'https')
        self.assertEqual(config.brent_name, 'brent')

    def test_is_secure(self):
        insecure_env = LmEnvironment('lm', 'test', 80)
        self.assertFalse(insecure_env.is_secure)
        secure_env = LmEnvironment('lm', 'test', 80, secure=True, username='user')
        self.assertTrue(secure_env.is_secure)

    def test_address(self):
        env = LmEnvironment('lm', 'test')
        self.assertEqual(env.address, 'https://test')
        env = LmEnvironment('lm', 'test', 32455)
        self.assertEqual(env.address, 'https://test:32455')
        env = LmEnvironment('lm', 'test', 32455, 'http')
        self.assertEqual(env.address, 'http://test:32455')
        env = LmEnvironment('lm', 'test', None, 'http')
        self.assertEqual(env.address, 'http://test')
        env = LmEnvironment('lm', 'test', None, 'http', path='gateway')
        self.assertEqual(env.address, 'http://test/gateway')
        env = LmEnvironment('lm', 'test', 32455, 'http', path='gateway')
        self.assertEqual(env.address, 'http://test:32455/gateway')

    def test_auth_address_fails_when_insecure(self):
        env = LmEnvironment('lm', 'test')
        with self.assertRaises(EnvironmentRuntimeError) as context:
            env.auth_address
        self.assertEqual(str(context.exception), 'auth_address cannot be determined for a non-secure LM environment')

    def test_auth_address(self):
        env = LmEnvironment('lm', 'test', 80, 'http', secure=True, username='user', auth_host='auth', auth_port=82, auth_protocol='https')
        self.assertEqual(env.auth_address, 'https://auth:82')

    def test_create_session_config(self):
        env = LmEnvironment('lm', 'test')
        session_config = env.create_session_config()
        self.assertIsInstance(session_config, LmSessionConfig)
        self.assertEqual(session_config.env, env)
        self.assertEqual(session_config.username, None)
        self.assertEqual(session_config.password, None)

    def test_create_session_config_with_default_username_password(self):
        env = LmEnvironment('lm', 'test', 80, 'https', secure=True, username='user')
        session_config = env.create_session_config()
        self.assertEqual(session_config.username, 'user')
        self.assertEqual(session_config.password, None)
        env = LmEnvironment('lm', 'test', 80, 'https', secure=True, username='user', password='secret')
        session_config = env.create_session_config()
        self.assertEqual(session_config.username, 'user')
        self.assertEqual(session_config.password, 'secret')

class TestLmSessionConfig(unittest.TestCase):

    def test_create(self):
        env = LmEnvironment('lm', 'test', 80, 'https', secure=True, username='user', password='secret')
        session_config = env.create_session_config()
        session = session_config.create()
        self.assertIsInstance(session, LmSession)
        self.assertEqual(session.env, env)
        self.assertEqual(session.username, 'user')
        self.assertEqual(session.password, 'secret')

class TestLmSession(unittest.TestCase):

    def test_init(self):
        env = LmEnvironment('lm', 'test', 80, 'https', secure=True, username='user', password='secret')
        session_config = env.create_session_config()
        session = LmSession(session_config)
        self.assertEqual(session.env, env)
        self.assertEqual(session.username, 'user')
        self.assertEqual(session.password, 'secret')

    def test_init_fails_without_config(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            LmSession(None)
        self.assertEqual(str(context.exception), 'config not provided to session')

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDescriptorDriver')
    def test_descriptor_driver(self, descriptor_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https'), None))
        driver = session.descriptor_driver
        descriptor_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, descriptor_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDescriptorDriver')
    def test_descriptor_driver_with_security(self, descriptor_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret'))
        driver = session.descriptor_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', 'user', 'secret')
        descriptor_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, descriptor_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmOnboardRmDriver')
    def test_onboard_rm_driver(self, onboard_rm_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https'), None))
        driver = session.onboard_rm_driver
        onboard_rm_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, onboard_rm_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmOnboardRmDriver')
    def test_onboard_rm_driver_with_security(self, onboard_rm_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret'))
        driver = session.onboard_rm_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', 'user', 'secret')
        onboard_rm_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, onboard_rm_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmTopologyDriver')
    def test_topology_driver(self, topology_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https'), None))
        driver = session.topology_driver
        topology_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, topology_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmTopologyDriver')
    def test_topology_driver_with_security(self, topology_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret'))
        driver = session.topology_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', 'user', 'secret')
        topology_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, topology_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmBehaviourDriver')
    def test_behaviour_driver(self, behaviour_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https'), None))
        driver = session.behaviour_driver
        behaviour_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, behaviour_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmBehaviourDriver')
    def test_behaviour_driver_with_security(self, behaviour_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret'))
        driver = session.behaviour_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', 'user', 'secret')
        behaviour_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, behaviour_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDeploymentLocationDriver')
    def test_deployment_location_driver(self, deployment_location_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https'), None))
        driver = session.deployment_location_driver
        deployment_location_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, deployment_location_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDeploymentLocationDriver')
    def test_deployment_location_driver_with_security(self, deployment_location_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret'))
        driver = session.deployment_location_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', 'user', 'secret')
        deployment_location_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, deployment_location_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmInfrastructureKeysDriver')
    def test_infrastructure_keys_driver(self, infrastructure_keys_driver_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https'), None))
        driver = session.infrastructure_keys_driver
        infrastructure_keys_driver_init.assert_called_once_with('https://test:80', None)
        self.assertEqual(driver, infrastructure_keys_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmInfrastructureKeysDriver')
    def test_infrastructure_keys_driver_with_security(self, infrastructure_keys_driver_init, mock_security_ctrl_init):
        session = LmSession(LmSessionConfig(LmEnvironment('lm', 'test', 80, 'https', secure=True, username='user', auth_host='auth', auth_port=81, auth_protocol='http'), 'user', 'secret'))
        driver = session.infrastructure_keys_driver
        mock_security_ctrl_init.assert_called_once_with('http://auth:81', 'user', 'secret')
        infrastructure_keys_driver_init.assert_called_once_with('https://test:80', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, infrastructure_keys_driver_init.return_value)
