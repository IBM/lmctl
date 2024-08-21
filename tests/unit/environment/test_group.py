import unittest
from pydantic import ValidationError
from lmctl.environment import EnvironmentGroup, TNCOEnvironment, ArmEnvironment

class TestEnvironmentGroup(unittest.TestCase):

    def test_init_without_name_fails(self):
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(name=None, description=None)
        self.assertEqual(str(context.exception).split('[type=string_type')[0].strip(), '1 validation error for EnvironmentGroup\nname\n  Input should be a valid string')
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(name=' ', description=None)
        self.assertEqual(str(context.exception).split('[type=string_too_short')[0].strip(), '1 validation error for EnvironmentGroup\nname\n  String should have at least 1 character')
        
    def test_init_with_invalid_tnco_config_type_fails(self):
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(name='test', description=None, tnco='tnco')
        self.assertEqual(str(context.exception).split('[type=value_error')[0].strip(), '1 validation error for EnvironmentGroup\ntnco\n  Value error,')

    def test_init_with_invalid_arm_config_type_fails(self):
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(name='test', description=None, tnco=None, arms='arms')
        self.assertEqual(str(context.exception).split('[type=dict_type')[0].strip(), '1 validation error for EnvironmentGroup\narms\n  Input should be a valid dictionary')
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(name='test', description=None, tnco=None, arms=['test'])
        self.assertEqual(str(context.exception).split('[type=dict_type')[0].strip(), '1 validation error for EnvironmentGroup\narms\n  Input should be a valid dictionary')

