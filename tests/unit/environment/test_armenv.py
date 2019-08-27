import unittest
import unittest.mock as mock
from lmctl.environment.common import EnvironmentConfigError
from lmctl.environment.armenv import ArmEnvironment, ArmSession, ArmSessionConfig


class TestArmEnvironment(unittest.TestCase):

    def test_init_fails_when_name_is_none(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            config = ArmEnvironment(None, '', 80)
        self.assertEqual(str(context.exception), 'AnsibleRM environment cannot be configured without property: name')

    def test_init_fails_when_host_is_none(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            config = ArmEnvironment('arm', None, 80)
        self.assertEqual(str(context.exception), 'AnsibleRM environment cannot be configured without property: host (ip_address)')

    def test_init_fails_when_protocol_unsupported(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            config = ArmEnvironment('arm', 'test', 80, 'ftp')
        self.assertEqual(str(context.exception), 'AnsibleRM environment cannot be configured with unsupported protocol \'ftp\'. Must be one of: [\'http\', \'https\']')

    def test_init_fails_with_unsupported_kwargs(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            config = ArmEnvironment('arm', 'test', 80, not_a_key='test')
        self.assertEqual(str(context.exception), 'Unsupported key argument: not_a_key')

    def test_init_full(self):
        config = ArmEnvironment('arm', 'test', 31080, 'http', onboarding_addr='http://arm:80')
        self.assertEqual(config.name, 'arm')
        self.assertEqual(config.host, 'test')
        self.assertEqual(config.port, 31080)
        self.assertEqual(config.protocol, 'http')
        self.assertEqual(config.onboarding_addr, 'http://arm:80')
    
    def test_set_defaults_to_none(self):
        config = ArmEnvironment('lm', 'test', None, None, onboarding_addr=None)
        self.assertEqual(config.name, 'lm')
        self.assertEqual(config.host, 'test')
        self.assertEqual(config.port, None)
        self.assertEqual(config.protocol, 'https')
        self.assertEqual(config.onboarding_addr, None)

    def test_set_defaults_to_empty(self):
        config = ArmEnvironment('lm', 'test', ' ', ' ', onboarding_addr=' ')
        self.assertEqual(config.name, 'lm')
        self.assertEqual(config.host, 'test')
        self.assertEqual(config.port, None)
        self.assertEqual(config.protocol, 'https')
        self.assertEqual(config.onboarding_addr, None)

    def test_address(self):
        env = ArmEnvironment('arm', 'test')
        self.assertEqual(env.address, 'https://test')
        env = ArmEnvironment('arm', 'test', 32455)
        self.assertEqual(env.address, 'https://test:32455')
        env = ArmEnvironment('arm', 'test', 32455, 'http')
        self.assertEqual(env.address, 'http://test:32455')
        env = ArmEnvironment('arm', 'test', None, 'http')
        self.assertEqual(env.address, 'http://test')

    def test_onboarding_address(self):
        env = ArmEnvironment('arm', 'test')
        self.assertEqual(env.onboarding_address, 'https://test')
        env = ArmEnvironment('arm', 'test', onboarding_addr='http://arm:80')
        self.assertEqual(env.onboarding_address, 'http://arm:80')

    def test_create_session_config(self):
        env = ArmEnvironment('arm', 'test')
        session_config = env.create_session_config()
        self.assertIsInstance(session_config, ArmSessionConfig)
        self.assertEqual(session_config.env, env)

class TestArmSessionConfig(unittest.TestCase):

    def test_create(self):
        env = ArmEnvironment('arm', 'test', 80, 'https')
        session_config = env.create_session_config()
        session = session_config.create()
        self.assertIsInstance(session, ArmSession)
        self.assertEqual(session.env, env)

class TestArmSession(unittest.TestCase):

    def test_init(self):
        env = ArmEnvironment('arm', 'test', 80)
        session_config = env.create_session_config()
        session = ArmSession(session_config)
        self.assertEqual(session.env, env)

    def test_init_fails_without_config(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            ArmSession(None)
        self.assertEqual(str(context.exception), 'config not provided to session')

    @mock.patch('lmctl.environment.armenv.arm_drivers.AnsibleRmDriver')
    def test_arm_driver(self, arm_driver_init):
        session = ArmSession(ArmSessionConfig(ArmEnvironment('lm', 'test', 80, 'https')))
        driver = session.arm_driver
        arm_driver_init.assert_called_once_with('https://test:80')
        self.assertEqual(driver, arm_driver_init.return_value)
    