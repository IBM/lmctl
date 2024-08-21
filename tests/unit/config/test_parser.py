import unittest
import unittest.mock as mock
import tempfile
import shutil
import os
import yaml
from lmctl.config import Config, ConfigParser, ConfigError
from lmctl.environment.group import EnvironmentGroup
from lmctl.environment.lmenv import TNCOEnvironment
from lmctl.environment.armenv import ArmEnvironment


PARSER_TEST_CONFIG_PARTS = """\
environments:
  test:
    alm:
      host: 127.0.0.1
      port: 1111
      protocol: https
      auth_host: auth
      auth_port: 4643
      auth_protocol: https
      username: jack
      password: secret
      kami_port: 34567
      kami_protocol: https
    arm:
      default:
        host: default
        port: 8765
        protocol: https
  test2:
    arm:
      first:
        host: first
      second: 
        host: second
"""

OLD_PARSER_TEST_CONFIG = """\
testlm:
  alm: 
    ip_address: 127.0.0.1
    secure_port: True
    username: jack
    auth_address: 127.0.0.2
testarm:
  arm:
    default:
      ip_address: 127.0.0.3
      secure_port: False
"""

ADDRESS_BASED_CONFIG = """\
environments:
  test:
    lm:
      address: https://some.lm.example.com
    arm:
      default:
        address: https://some.arm.example.com
"""
class TestConfigParser(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def __write_file(self, file_path, content):
        with open(file_path, 'w') as f:
            f.write(content)

    def test_from_file(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, PARSER_TEST_CONFIG_PARTS)
        config = ConfigParser().from_file(config_file_path)
        self.assertIsNotNone(config)
        self.assertIsInstance(config, Config)
        self.assertEqual(len(config.environments), 2)
        self.assertIn('test', config.environments)
        test_env = config.environments['test']
        self.assertIsInstance(test_env, EnvironmentGroup)
        self.assertIsInstance(test_env.lm, TNCOEnvironment)
        self.assertEqual(test_env.lm.address, 'https://127.0.0.1:1111')
        self.assertEqual(test_env.lm.auth_address, 'https://auth:4643')
        self.assertEqual(test_env.lm.username, 'jack')
        self.assertEqual(test_env.lm.password, 'secret')
        self.assertEqual(test_env.lm.kami_address, 'https://127.0.0.1:34567')
        arms_config = test_env.arms
        self.assertEqual(len(arms_config), 1)
        default_arm_config = arms_config['default']
        self.assertIsInstance(default_arm_config, ArmEnvironment)
        self.assertEqual(default_arm_config.address, 'https://default:8765')
        self.assertIn('test2', config.environments)
        test2_env = config.environments['test2']
        arms_config = test2_env.arms
        self.assertEqual(len(arms_config), 2)
        self.assertIn('first', arms_config)
        self.assertIn('second', arms_config)
        
    def test_from_file_rewrites_old_config(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, OLD_PARSER_TEST_CONFIG)
        config = ConfigParser().from_file(config_file_path)
        self.assertEqual(len(config.environments), 2)
        testlm_env = config.environments['testlm']
        self.assertEqual(testlm_env.lm.address, 'https://127.0.0.1')
        self.assertEqual(testlm_env.lm.secure, True)
        self.assertEqual(testlm_env.lm.username, 'jack')
        testarm_env = config.environments['testarm']
        self.assertEqual(testarm_env.arms['default'].address, 'http://127.0.0.3')

    @mock.patch('lmctl.ctl.config.ConfigRewriter.rewrite')
    def test_rewrite_fails(self, mock_rewrite):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, OLD_PARSER_TEST_CONFIG)
        mock_rewrite.side_effect = ValueError('Mocked error')
        with self.assertRaises(ConfigError) as context:
            ConfigParser().from_file(config_file_path)
        self.assertEqual(str(context.exception), 'The configuration file provided ({0}) appears to be a 2.0.X file. \
            Lmctl attempted to rewrite the file with updated syntax for 2.1.X but failed with the following error: Mocked error'.format(config_file_path))

    def test_parse_tnco_using_lm_key(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'lm': {
                    'host': 'test',
                    'port': 32455,
                    'protocol': 'https',
                    'secure': True,
                    'username': 'user',
                    'password': 'secret', 
                    'auth_host': 'auth',
                    'auth_port': 32456,
                    'auth_protocol': 'https'
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        self.assertEqual(lm_config.address, 'https://test:32455')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, 'secret')
        self.assertEqual(lm_config.auth_address, 'https://auth:32456')

    def test_parse_tnco_key(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'tnco': {
                    'host': 'test',
                    'port': 32455,
                    'protocol': 'https',
                    'secure': True,
                    'username': 'user',
                    'password': 'secret', 
                    'auth_host': 'auth',
                    'auth_port': 32456,
                    'auth_protocol': 'https'
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        self.assertEqual(lm_config.address, 'https://test:32455')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, 'secret')
        self.assertEqual(lm_config.auth_address, 'https://auth:32456')

    def test_parse_fail_when_lm_and_alm_used(self):
        invalid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'lm': {},
                'alm': {}
            }
          }
        }
        with self.assertRaises(ConfigError) as context:
            ConfigParser().from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'Environment should not feature both "lm" and "alm"')

    def test_parse_fail_when_lm_and_tnco_used(self):
        invalid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'lm': {},
                'tnco': {}
            }
          }
        }
        with self.assertRaises(ConfigError) as context:
            ConfigParser().from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'Environment should not feature both "lm" and "tnco"')
    
    def test_parse_fail_when_alm_and_tnco_used(self):
        invalid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'alm': {},
                'tnco': {}
            }
          }
        }
        with self.assertRaises(ConfigError) as context:
            ConfigParser().from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'Environment should not feature both "alm" and "tnco"')
    
    def test_parse_lm_address(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'alm': {
                    'address': 'https://test:32455',
                    'secure': True,
                    'username': 'user',
                    'password': 'secret', 
                    'auth_address': 'https://auth:32456'
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        
        self.assertEqual(lm_config.address, 'https://test:32455')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, 'secret')
        self.assertEqual(lm_config.auth_address, 'https://auth:32456')
        
    def test_parse_lm_parts(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'alm': {
                    'host': 'test',
                    'port': 32455,
                    'protocol': 'https',
                    'secure': True,
                    'username': 'user',
                    'password': 'secret', 
                    'auth_host': 'auth',
                    'auth_port': 32456,
                    'auth_protocol': 'https'
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        
        self.assertEqual(lm_config.address, 'https://test:32455')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, 'secret')
        self.assertEqual(lm_config.auth_address, 'https://auth:32456')

    def test_parse_lm_kami_address_as_parts(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'alm': {
                    'address': 'https://test:32455',
                    'kami_protocol': 'https',
                    'kami_port': '12345'
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        
        self.assertEqual(lm_config.address, 'https://test:32455')
        self.assertEqual(lm_config.kami_address, 'https://test:12345')
        
    def test_parse_lm_kami_address(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'alm': {
                    'address': 'https://test:32455',
                    'kami_address': 'https://kami:12345'
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        
        self.assertEqual(lm_config.address, 'https://test:32455')
        self.assertEqual(lm_config.kami_address, 'https://kami:12345')
        
    def test_parse_lm_defaults(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'alm': {
                    'host': 'test'
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        
        self.assertEqual(lm_config.address, 'https://test')
        self.assertEqual(lm_config.secure, False)
        self.assertEqual(lm_config.username, None)
        self.assertEqual(lm_config.password, None)
        self.assertEqual(lm_config.auth_address, 'https://test')
        
    def test_parse_lm_auth_defaults(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'alm': {
                    'host': 'test',
                    'secure': True,
                    'username': 'user'
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        
        self.assertEqual(lm_config.address, 'https://test')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, None)
        self.assertEqual(lm_config.auth_address, 'https://test')

    def test_parse_lm_deprecated_properties(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'alm': {
                    'ip_address': 'test',
                    'username': 'user',
                    'auth_address': 'auth',
                    'secure_port': False,
                    'protocol': 'https'
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        
        self.assertEqual(lm_config.address, 'https://test')
        self.assertEqual(lm_config.secure, False)
        self.assertEqual(lm_config.username, 'user')
        self.assertEqual(lm_config.password, None)
        self.assertEqual(lm_config.auth_address, 'https://auth')

    def test_parse_arm_address(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'arm': {
                    'first': {
                        'address': 'https://test:1111'
                    },
                    'second': {
                        'address': 'https://test:2222'
                    }
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        arms_config = test_group_config.arms
        self.assertEqual(len(arms_config), 2)
        self.assertIn('first', arms_config)
        first_arm_config = arms_config['first']
        self.assertIsInstance(first_arm_config, ArmEnvironment)
        self.assertEqual(first_arm_config.address, 'https://test:1111')
        self.assertIn('second', arms_config)
        second_arm_config = arms_config['second']
        self.assertIsInstance(second_arm_config, ArmEnvironment)
        self.assertEqual(second_arm_config.address, 'https://test:2222')
       
    def test_parse_arm_as_parts(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'arm': {
                    'first': {
                        'host': 'test',
                        'port': 1,
                        'protocol': 'https',
                        'onboarding_addr': 'https://onboard'
                    },
                    'second': {
                        'host': 'test2',
                        'port': 2,
                        'protocol': 'https',
                        'onboarding_addr': 'https://onboard2'
                    }
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        arms_config = test_group_config.arms
        self.assertEqual(len(arms_config), 2)
        self.assertIn('first', arms_config)
        first_arm_config = arms_config['first']
        self.assertIsInstance(first_arm_config, ArmEnvironment)
        self.assertEqual(first_arm_config.address, 'https://test:1')
        self.assertEqual(first_arm_config.onboarding_addr, 'https://onboard')
        self.assertIn('second', arms_config)
        second_arm_config = arms_config['second']
        self.assertIsInstance(second_arm_config, ArmEnvironment)
        self.assertEqual(second_arm_config.address, 'https://test2:2')
        self.assertEqual(second_arm_config.onboarding_addr, 'https://onboard2')
       
    def test_parse_arm_defaults(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'arm': {
                    'default': {
                        'host': 'test'
                    }
                }
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        arms_config = test_group_config.arms
        self.assertEqual(len(arms_config), 1)
        self.assertIn('default', arms_config)
        default_arm_config = arms_config['default']
        self.assertIsInstance(default_arm_config, ArmEnvironment)
        self.assertEqual(default_arm_config.address, 'https://test')
        self.assertEqual(default_arm_config.onboarding_addr, None)
    
    def test_parse_arm_deprecated_properties(self):
        valid_config = {
          'environments': {
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
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        arms_config = test_group_config.arms
        self.assertEqual(len(arms_config), 1)
        self.assertIn('default', arms_config)
        default_arm_config = arms_config['default']
        self.assertIsInstance(default_arm_config, ArmEnvironment)
        self.assertEqual(default_arm_config.address, 'http://test')
        self.assertEqual(default_arm_config.onboarding_addr, None)
     
    def test_parse_group(self):
        valid_config = {
          'environments': {
            'test': {
                'description': 'a test group'
            }
          }
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertEqual(test_group_config.description, 'a test group')

    def test_parse_multi_envs(self):
        valid_config = {
          'environments': {
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
        }
        config = ConfigParser().from_dict(valid_config)
        self.assertIn('test', config.environments)
        self.assertIn('test2', config.environments)

    def test_parse_invalid_lm(self):
        invalid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'alm': {
                    'host': 'test',
                    'secure': True
                }
            }
          }
        }
        with self.assertRaises(ConfigError) as context:
            ConfigParser().from_dict(invalid_config)
        self.assertEqual(str(context.exception).split('[type=value_error')[0].strip(), 'Config error: 1 validation error for Config\nenvironments.test.tnco\n  Value error, Secure TNCO environment must be configured with either "client_id" or "username" property when using "auth_mode=oauth". If the TNCO environment is not secure then set "secure" to False')

    def test_parse_invalid_arm(self):
        invalid_config = {
          'environments': {
            'test': {
                'description': 'a test group',
                'arm': {
                    'invalid': {}
                }
            }
          }
        }
        with self.assertRaises(ConfigError) as context:
            ConfigParser().from_dict(invalid_config)
       
        self.assertEqual(str(context.exception).split('[type=value_error')[0].strip(), 'Config error: 1 validation error for Config\nenvironments.test.arms.invalid\n  Value error, AnsibleRM environment cannot be configured without "address" property or "host" property')