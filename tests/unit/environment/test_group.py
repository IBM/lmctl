import unittest
from lmctl.environment import EnvironmentGroup, LmEnvironment, ArmEnvironment,EnvironmentConfigError, EnvironmentRuntimeError

class TestEnvironmentGroup(unittest.TestCase):

    def test_init_without_name_fails(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            EnvironmentGroup(None, None)
        self.assertEqual(str(context.exception), 'name must be defined')
        with self.assertRaises(EnvironmentConfigError) as context:
            EnvironmentGroup(' ', None)
        self.assertEqual(str(context.exception), 'name must be defined')
        
    def test_init_with_invalid_lm_config_type_fails(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            EnvironmentGroup('test', None, 'lm')
        self.assertEqual(str(context.exception), 'lm_env provided must be of type LmEnvironment')

    def test_init_with_invalid_arm_config_type_fails(self):
        with self.assertRaises(EnvironmentConfigError) as context:
            EnvironmentGroup('test', None, None, [])
        self.assertEqual(str(context.exception), 'arm_envs must be name/value pairs')
        with self.assertRaises(EnvironmentConfigError) as context:
            EnvironmentGroup('test', None, None, {'arm': 'test'})
        self.assertEqual(str(context.exception), 'Items in arm_envs dict must be of type ArmEnvironment')

    def test_attributes(self):
        name = 'test'
        description = 'test description'
        lm = LmEnvironment('test', 'host')
        arms =   {'test': ArmEnvironment('test', 'host')}
        config = EnvironmentGroup(name, description, lm, arms)
        self.assertEqual(config.name, name)
        self.assertEqual(config.description, description)
        self.assertEqual(config.lm, lm)
        self.assertEqual(config.arms, arms)

    def test_fails_when_lm_not_found(self):
        group = EnvironmentGroup('test', 'test')
        with self.assertRaises(EnvironmentRuntimeError) as context:
            group.lm
        self.assertEqual(str(context.exception), 'No TNCO environment has been configured on this group: test')

    def tests_fails_when_arm_not_found(self):
        group = EnvironmentGroup('test', 'test')
        with self.assertRaises(EnvironmentRuntimeError) as context:
            group.arm_named('test')
        self.assertEqual(str(context.exception), 'No ARM named \'test\' on this group: test')
