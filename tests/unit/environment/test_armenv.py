import unittest
import unittest.mock as mock
from lmctl.environment.common import EnvironmentConfigError
from lmctl.environment.armenv import ArmEnvironment, ArmSession, ArmSessionConfig


class TestArmEnvironment(unittest.TestCase):

    def test_init_fails_when_name_is_none(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            config = ArmEnvironment(None, '', 80)
        self.assertEqual(str(context.exception), 'AnsibleRM environment cannot be configured without property: name')

    def test_init_fails_when_address_and_host_are_none(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            config = ArmEnvironment('arm', port=80)
        self.assertEqual(str(context.exception), 'AnsibleRM environment cannot be configured without "address" property or "host" property')

    def test_init_with_all_as_parts(self):
        config = ArmEnvironment('arm', host='test', port=31080, protocol='http', onboarding_addr='http://arm:80')
        self.assertEqual(config.name, 'arm')
        self.assertEqual(config.address, 'http://test:31080')
        self.assertEqual(config.onboarding_addr, 'http://arm:80')
    
    def test_set_defaults_to_none(self):
        config = ArmEnvironment('lm', host='test', port=None, protocol=None, onboarding_addr=None)
        self.assertEqual(config.name, 'lm')
        self.assertEqual(config.address, 'https://test')
        self.assertEqual(config.onboarding_addr, None)

    def test_set_defaults_to_empty(self):
        config = ArmEnvironment('lm', host='test', port=' ', protocol=' ', onboarding_addr=' ')
        self.assertEqual(config.name, 'lm')
        self.assertEqual(config.address, 'https://test')
        self.assertEqual(config.onboarding_addr, None)

    def test_init_with_address(self):
        config = ArmEnvironment('arm', address='https://test:8080/api')
        self.assertEqual(config.address, 'https://test:8080/api')

    def test_address_from_parts(self):
        env = ArmEnvironment('arm', host='test')
        self.assertEqual(env.address, 'https://test')
        env = ArmEnvironment('arm', host='test', port=32455)
        self.assertEqual(env.address, 'https://test:32455')
        env = ArmEnvironment('arm', host='test', port=32455, protocol='http')
        self.assertEqual(env.address, 'http://test:32455')
        env = ArmEnvironment('arm', host='test', port=None, protocol='http')
        self.assertEqual(env.address, 'http://test')

    def test_create_session_config(self):
        env = ArmEnvironment('arm', host='test')
        session_config = env.create_session_config()
        self.assertIsInstance(session_config, ArmSessionConfig)
        self.assertEqual(session_config.env, env)

class TestArmSessionConfig(unittest.TestCase):

    def test_create(self):
        env = ArmEnvironment('arm', host='test', port=80, protocol='https')
        session_config = env.create_session_config()
        session = session_config.create()
        self.assertIsInstance(session, ArmSession)
        self.assertEqual(session.env, env)

class TestArmSession(unittest.TestCase):

    def test_init(self):
        env = ArmEnvironment('arm', host='test', port=80)
        session_config = env.create_session_config()
        session = ArmSession(session_config)
        self.assertEqual(session.env, env)

    def test_init_fails_without_config(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            ArmSession(None)
        self.assertEqual(str(context.exception), 'config not provided to session')

    @mock.patch('lmctl.environment.armenv.arm_drivers.AnsibleRmDriver')
    def test_arm_driver(self, arm_driver_init):
        session = ArmSession(ArmSessionConfig(ArmEnvironment('lm', host='test', port=80, protocol='https')))
        driver = session.arm_driver
        arm_driver_init.assert_called_once_with('https://test:80')
        self.assertEqual(driver, arm_driver_init.return_value)
    