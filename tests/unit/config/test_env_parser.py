import unittest
from lmctl.config import ConfigError, EnvironmentGroupsParser
from lmctl.environment.lmenv import LmEnvironment
from lmctl.environment.armenv import ArmEnvironment

class TestEnvironmentGroupsParser(unittest.TestCase):

    def test_parse_lm_using_lm_key(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'lm': {
                    'host': 'test',
                    'port': 32455,
                    'protocol': 'http',
                    'secure': True,
                    'username': 'user',
                    'password': 'secret', 
                    'auth_host': 'auth',
                    'auth_port': 32456,
                    'auth_protocol': 'http'
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        lm_config = test_group_config.lm
        self.assertIsInstance(lm_config, LmEnvironment)
        self.assertEqual(lm_config.name, 'alm')
        self.assertEqual(lm_config.address, 'http://test:32455')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, 'secret')
        self.assertEqual(lm_config.auth_address, 'http://auth:32456')

    def test_parse_lm_using_tnco_key(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'tnco': {
                    'host': 'test',
                    'port': 32455,
                    'protocol': 'http',
                    'secure': True,
                    'username': 'user',
                    'password': 'secret', 
                    'auth_host': 'auth',
                    'auth_port': 32456,
                    'auth_protocol': 'http'
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        lm_config = test_group_config.lm
        self.assertIsInstance(lm_config, LmEnvironment)
        self.assertEqual(lm_config.name, 'alm')
        self.assertEqual(lm_config.address, 'http://test:32455')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, 'secret')
        self.assertEqual(lm_config.auth_address, 'http://auth:32456')

    def test_parse_fail_when_lm_and_alm_used(self):
        invalid_config = {
            'test': {
                'description': 'a test group',
                'lm': {},
                'alm': {}
            }
        }
        with self.assertRaises(ConfigError) as context:
            EnvironmentGroupsParser.from_dict(invalid_config)
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
            EnvironmentGroupsParser.from_dict(invalid_config)
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
            EnvironmentGroupsParser.from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'Environment should not feature both "alm" and "tnco"')
    
    def test_parse_lm_address(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'alm': {
                    'address': 'http://test:32455',
                    'secure': True,
                    'username': 'user',
                    'password': 'secret', 
                    'auth_address': 'http://auth:32456'
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        lm_config = test_group_config.lm
        self.assertIsInstance(lm_config, LmEnvironment)
        self.assertEqual(lm_config.name, 'alm')
        self.assertEqual(lm_config.address, 'http://test:32455')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, 'secret')
        self.assertEqual(lm_config.auth_address, 'http://auth:32456')
        
    def test_parse_lm_parts(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'alm': {
                    'host': 'test',
                    'port': 32455,
                    'protocol': 'http',
                    'secure': True,
                    'username': 'user',
                    'password': 'secret', 
                    'auth_host': 'auth',
                    'auth_port': 32456,
                    'auth_protocol': 'http'
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        lm_config = test_group_config.lm
        self.assertIsInstance(lm_config, LmEnvironment)
        self.assertEqual(lm_config.name, 'alm')
        self.assertEqual(lm_config.address, 'http://test:32455')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, 'secret')
        self.assertEqual(lm_config.auth_address, 'http://auth:32456')

    def test_parse_lm_kami_address_as_parts(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'alm': {
                    'address': 'http://test:32455',
                    'kami_protocol': 'https',
                    'kami_port': '12345'
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        lm_config = test_group_config.lm
        self.assertIsInstance(lm_config, LmEnvironment)
        self.assertEqual(lm_config.name, 'alm')
        self.assertEqual(lm_config.address, 'http://test:32455')
        self.assertEqual(lm_config.kami_address, 'https://test:12345')
        
    def test_parse_lm_kami_address(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'alm': {
                    'address': 'http://test:32455',
                    'kami_address': 'http://kami:12345'
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        lm_config = test_group_config.lm
        self.assertIsInstance(lm_config, LmEnvironment)
        self.assertEqual(lm_config.name, 'alm')
        self.assertEqual(lm_config.address, 'http://test:32455')
        self.assertEqual(lm_config.kami_address, 'http://kami:12345')
        
    def test_parse_lm_defaults(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'alm': {
                    'host': 'test'
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        lm_config = test_group_config.lm
        self.assertIsInstance(lm_config, LmEnvironment)
        self.assertEqual(lm_config.name, 'alm')
        self.assertEqual(lm_config.address, 'https://test')
        self.assertEqual(lm_config.secure, False)
        self.assertEqual(lm_config.username, None)
        self.assertEqual(lm_config.password, None)
        self.assertEqual(lm_config.auth_address, 'https://test')
        
    def test_parse_lm_auth_defaults(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'alm': {
                    'host': 'test',
                    'secure': True,
                    'username': 'user'
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        lm_config = test_group_config.lm
        self.assertIsInstance(lm_config, LmEnvironment)
        self.assertEqual(lm_config.name, 'alm')
        self.assertEqual(lm_config.address, 'https://test')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, None)
        self.assertEqual(lm_config.auth_address, 'https://test')

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
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        lm_config = test_group_config.lm
        self.assertIsInstance(lm_config, LmEnvironment)
        self.assertEqual(lm_config.name, 'alm')
        self.assertEqual(lm_config.address, 'http://test')
        self.assertEqual(lm_config.secure, False)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, None)
        self.assertEqual(lm_config.auth_address, 'auth')

    def test_parse_arm_address(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'arm': {
                    'first': {
                        'address': 'http://test:1111'
                    },
                    'second': {
                        'address': 'https://test:2222'
                    }
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        arms_config = test_group_config.arms
        self.assertEqual(len(arms_config), 2)
        self.assertIn('first', arms_config)
        first_arm_config = arms_config['first']
        self.assertIsInstance(first_arm_config, ArmEnvironment)
        self.assertEqual(first_arm_config.name, 'first')
        self.assertEqual(first_arm_config.address, 'http://test:1111')
        self.assertIn('second', arms_config)
        second_arm_config = arms_config['second']
        self.assertIsInstance(second_arm_config, ArmEnvironment)
        self.assertEqual(second_arm_config.name, 'second')
        self.assertEqual(second_arm_config.address, 'https://test:2222')
       
    def test_parse_arm_as_parts(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'arm': {
                    'first': {
                        'host': 'test',
                        'port': 1,
                        'protocol': 'http',
                        'onboarding_addr': 'http://onboard'
                    },
                    'second': {
                        'host': 'test2',
                        'port': 2,
                        'protocol': 'https',
                        'onboarding_addr': 'http://onboard2'
                    }
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        arms_config = test_group_config.arms
        self.assertEqual(len(arms_config), 2)
        self.assertIn('first', arms_config)
        first_arm_config = arms_config['first']
        self.assertIsInstance(first_arm_config, ArmEnvironment)
        self.assertEqual(first_arm_config.name, 'first')
        self.assertEqual(first_arm_config.address, 'http://test:1')
        self.assertEqual(first_arm_config.onboarding_addr, 'http://onboard')
        self.assertIn('second', arms_config)
        second_arm_config = arms_config['second']
        self.assertIsInstance(second_arm_config, ArmEnvironment)
        self.assertEqual(second_arm_config.name, 'second')
        self.assertEqual(second_arm_config.address, 'https://test2:2')
        self.assertEqual(second_arm_config.onboarding_addr, 'http://onboard2')
       
    def test_parse_arm_defaults(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'arm': {
                    'default': {
                        'host': 'test'
                    }
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        arms_config = test_group_config.arms
        self.assertEqual(len(arms_config), 1)
        self.assertIn('default', arms_config)
        default_arm_config = arms_config['default']
        self.assertIsInstance(default_arm_config, ArmEnvironment)
        self.assertEqual(default_arm_config.name, 'default')
        self.assertEqual(default_arm_config.address, 'https://test')
        self.assertEqual(default_arm_config.onboarding_addr, None)
    
    def test_parse_arm_deprecated_properties(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'arm': {
                    'default': {
                        'ip_address': 'test',
                        'secure_port': False
                    }
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        arms_config = test_group_config.arms
        self.assertEqual(len(arms_config), 1)
        self.assertIn('default', arms_config)
        default_arm_config = arms_config['default']
        self.assertIsInstance(default_arm_config, ArmEnvironment)
        self.assertEqual(default_arm_config.name, 'default')
        self.assertEqual(default_arm_config.address, 'http://test')
        self.assertEqual(default_arm_config.onboarding_addr, None)
     
    def test_parse_group(self):
        valid_config = {
            'test': {
                'description': 'a test group'
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        test_group_config = groups_config['test']
        self.assertEqual(test_group_config.description, 'a test group')

    def test_parse_multi_envs(self):
        valid_config = {
            'test': {
                'description': 'a test group',
                'alm': {
                    'host': 'test'
                },
                'arm': {
                    'first': {
                        'host': 'test'
                    },
                    'second': {
                        'host': 'test2'
                    }
                }
            },
            'test2': {
                'description': 'another test group',
                'alm': {
                    'host': 'test'
                },
                'arm': {
                    'first': {
                        'host': 'test'
                    },
                    'second': {
                        'host': 'test2'
                    }
                }
            }
        }
        groups_config = EnvironmentGroupsParser.from_dict(valid_config)
        self.assertIn('test', groups_config)
        self.assertIn('test2', groups_config)

    def test_parse_invalid_lm(self):
        invalid_config = {
            'test': {
                'description': 'a test group',
                'alm': {
                    'host': 'test',
                    'secure': True
                }
            }
        }
        with self.assertRaises(ConfigError) as context:
            EnvironmentGroupsParser.from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'Secure LM environment cannot be configured without "client_id" or "username" property. If the LM environment is not secure then set "secure" to False')

    def test_parse_invalid_arm(self):
        invalid_config = {
            'test': {
                'description': 'a test group',
                'arm': {
                    'invalid': {}
                }
            }
        }
        with self.assertRaises(ConfigError) as context:
            EnvironmentGroupsParser.from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'AnsibleRM environment cannot be configured without "address" property or "host" property')