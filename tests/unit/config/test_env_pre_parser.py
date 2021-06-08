import unittest
from lmctl.config import ConfigError
from lmctl.config.env_pre_parser import EnvironmentGroupPreParser
from lmctl.environment.lmenv import TNCOEnvironment
from lmctl.environment.armenv import ArmEnvironment

class TestEnvironmentGroupPreParser(unittest.TestCase):

    def test_group_include_name(self):
        valid_config = {
            'test': {}
        }
        parsed_config = EnvironmentGroupPreParser().parse(valid_config)
        self.assertIn('test', parsed_config)
        self.assertEqual(parsed_config.get('test').get('name', None), 'test')
    
    def test_normalize_lm_key_to_tnco(self):
        valid_config = {
            'test': {
                'lm': {
                    'address': 'localhost'
                }
            }
        }
        parsed_config = EnvironmentGroupPreParser().parse(valid_config)
        test_env = parsed_config.get('test')
        self.assertNotIn('lm', test_env)
        self.assertEqual(test_env['tnco'], {
            'name': 'tnco',
            'address': 'localhost'
        })

    def test_normalize_alm_key_to_tnco(self):
        valid_config = {
            'test': {
                'alm': {
                    'address': 'localhost'
                }
            }
        }
        parsed_config = EnvironmentGroupPreParser().parse(valid_config)
        test_env = parsed_config.get('test')
        self.assertNotIn('lm', test_env)
        self.assertEqual(test_env['tnco'], {
            'name': 'tnco',
            'address': 'localhost'
        })

    def test_parse_fail_when_lm_and_alm_used(self):
        invalid_config = {
            'test': {
                'description': 'a test group',
                'lm': {},
                'alm': {}
            }
        }
        with self.assertRaises(ConfigError) as context:
            EnvironmentGroupPreParser().parse(invalid_config)
        self.assertEqual(str(context.exception), 'Environment should not feature both "lm" and "alm"')

    def test_parse_fail_when_lm_and_tnco_used(self):
        invalid_config = {
            'test': {
                'description': 'a test group',
                'lm': {},
                'tnco': {}
            }
        }
        with self.assertRaises(ConfigError) as context:
            EnvironmentGroupPreParser().parse(invalid_config)
        self.assertEqual(str(context.exception), 'Environment should not feature both "lm" and "tnco"')
    
    def test_parse_fail_when_alm_and_tnco_used(self):
        invalid_config = {
            'test': {
                'description': 'a test group',
                'alm': {},
                'tnco': {}
            }
        }
        with self.assertRaises(ConfigError) as context:
            EnvironmentGroupPreParser().parse(invalid_config)
        self.assertEqual(str(context.exception), 'Environment should not feature both "alm" and "tnco"')

    def test_parse_lm_deprecated_properties(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'alm': {
                    'ip_address': 'test',
                    'username': 'user',
                    'auth_address': 'auth',
                    'secure_port': False
                }
            }
        }
        groups_config = EnvironmentGroupPreParser().parse(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        lm_config = test_group_config['tnco']
        self.assertEqual(lm_config, {
            'name': 'tnco',
            'host': 'test',
            'protocol': 'http',
            'username': 'user',
            'auth_address': 'auth'
        })
    
    def test_normalize_arm_key(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'arm': {
                    'default': {
                        'address': 'localhost'
                    }
                }
            }
        }
        groups_config = EnvironmentGroupPreParser().parse(valid_config)
        test_env = groups_config.get('test')
        self.assertNotIn('arm', test_env)
        self.assertEqual(test_env['arms'], {
            'default': {
                'name': 'default',
                'address': 'localhost'
            }
        })

    def test_parse_arms_deprecated_properties(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'arms': {
                    'default': {
                        'ip_address': 'test',
                        'secure_port': False
                    }
                }
            }
        }
        groups_config = EnvironmentGroupPreParser().parse(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        arms_config = test_group_config['arms']
        self.assertEqual(len(arms_config), 1)
        self.assertIn('default', arms_config)
        default_arm_config = arms_config['default']
        self.assertEqual(default_arm_config, {
            'name': 'default',
            'host': 'test',
            'protocol': 'http'
        })
     