import unittest
from pydantic import ValidationError
from lmctl.environment import EnvironmentGroup, TNCOEnvironment, ArmEnvironment

class TestEnvironmentGroup(unittest.TestCase):

    def test_init_without_name_fails(self):
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(None, None)
        self.assertEqual(str(context.exception), '1 validation error for EnvironmentGroup\nname\n  none is not an allowed value (type=type_error.none.not_allowed)')
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup(' ', None)
        self.assertEqual(str(context.exception), '1 validation error for EnvironmentGroup\nname\n  ensure this value has at least 1 characters (type=value_error.any_str.min_length; limit_value=1)')
        
    def test_init_with_invalid_tnco_config_type_fails(self):
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup('test', None, 'tnco')
        self.assertEqual(str(context.exception), '1 validation error for EnvironmentGroup\ntnco\n  instance of TNCOEnvironment, tuple or dict expected (type=type_error.dataclass; class_name=TNCOEnvironment)')

    def test_init_with_invalid_arm_config_type_fails(self):
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup('test', None, None, 'arms')
        self.assertEqual(str(context.exception), '1 validation error for EnvironmentGroup\narms\n  value is not a valid dict (type=type_error.dict)')
        with self.assertRaises(ValidationError) as context:
            EnvironmentGroup('test', None, None, {'arm': 'test'})
        self.assertEqual(str(context.exception), '1 validation error for EnvironmentGroup\narms -> arm\n  instance of ArmEnvironment, tuple or dict expected (type=type_error.dataclass; class_name=ArmEnvironment)')

