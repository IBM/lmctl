import unittest
import tempfile
import os
import shutil
from unittest.mock import patch
from lmctl.config import Config, ConfigIO, ConfigError
from lmctl.environment import EnvironmentGroup, TNCOEnvironment, ArmEnvironment
from .config_files import ConfigFileTestHelper

class TestConfigIO(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.test_helper = ConfigFileTestHelper(self.tmp_dir)

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    @patch('lmctl.config.io.ConfigFinder')
    def test_read_discovered_file(self, mock_config_finder_class):
        config_path = self.test_helper.prepare_file('simple-config')
        mock_config_finder_inst = mock_config_finder_class.return_value
        mock_config_finder_inst.find.return_value = config_path
        
        config_io = ConfigIO()
        config, found_path = config_io.read_discovered_file()
        mock_config_finder_inst.find.assert_called_once()
        
        # Check config
        self.assertEqual(found_path, config_path)
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
        self.assertEqual(default_arm_config.address, 'http://default:8765')
        self.assertIn('test2', config.environments)
        test2_env = config.environments['test2']
        arms_config = test2_env.arms
        self.assertEqual(len(arms_config), 2)
        self.assertIn('first', arms_config)
        self.assertIn('second', arms_config)

    @patch('lmctl.config.io.ConfigFinder')
    def test_read_discovered_file_override_path(self, mock_config_finder_class):
        config_path = self.test_helper.prepare_file('simple-config')
        mock_config_finder_inst = mock_config_finder_class.return_value
        
        config_io = ConfigIO()
        config, found_path = config_io.read_discovered_file(override_path=config_path)
        mock_config_finder_inst.find.assert_not_called()

        # Brief check that config loaded
        self.assertEqual(found_path, config_path)
        self.assertIn('test', config.environments)

    def test_file_to_config(self):
        config_io = ConfigIO()
        config_path = self.test_helper.prepare_file('simple-config')

        config = config_io.file_to_config(config_path)
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
        self.assertEqual(default_arm_config.address, 'http://default:8765')
        self.assertIn('test2', config.environments)
        test2_env = config.environments['test2']
        arms_config = test2_env.arms
        self.assertEqual(len(arms_config), 2)
        self.assertIn('first', arms_config)
        self.assertIn('second', arms_config)

    def test_dict_to_config(self):
        config_io = ConfigIO()
        config_dict = self.test_helper.read_yaml_file('simple-config')
        config = config_io.dict_to_config(config_dict)
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
        self.assertEqual(default_arm_config.address, 'http://default:8765')
        self.assertIn('test2', config.environments)
        test2_env = config.environments['test2']
        arms_config = test2_env.arms
        self.assertEqual(len(arms_config), 2)
        self.assertIn('first', arms_config)
        self.assertIn('second', arms_config)
    
    def test_parse_tnco_using_lm_key(self):
        config_io = ConfigIO()
        config_dict = self.test_helper.read_yaml_file('lm-key')
        config = config_io.dict_to_config(config_dict)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        self.assertEqual(lm_config.address, 'https://127.0.0.1:1111')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'jack')
        self.assertEqual(lm_config.password, 'secret')
        self.assertEqual(lm_config.auth_address, 'https://auth:32456')

    def test_parse_tnco_using_tnco_key(self):
        config_io = ConfigIO()
        config_dict = self.test_helper.read_yaml_file('tnco-key')
        config = config_io.dict_to_config(config_dict)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        self.assertEqual(lm_config.address, 'https://127.0.0.1:1113')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'jack')
        self.assertEqual(lm_config.password, 'secret')
        self.assertEqual(lm_config.auth_address, 'https://auth:32456')
    
    def test_parse_tnco_using_alm_key(self):
        config_io = ConfigIO()
        config_dict = self.test_helper.read_yaml_file('alm-key')
        config = config_io.dict_to_config(config_dict)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        self.assertIsNotNone(test_group_config.tnco)
        lm_config = test_group_config.tnco
        self.assertIsInstance(lm_config, TNCOEnvironment)
        self.assertEqual(lm_config.address, 'https://127.0.0.1:1112')
        self.assertEqual(lm_config.secure, True)
        self.assertEqual(lm_config.username, 'jack')
        self.assertEqual(lm_config.password, 'secret')
        self.assertEqual(lm_config.auth_address, 'https://auth:32456')
    
    def test_parse_fail_when_lm_and_alm_used(self):
        config_dict = self.test_helper.read_yaml_file('lm-and-alm-key')
        with self.assertRaises(ConfigError) as context:
            ConfigIO().dict_to_config(config_dict)
        self.assertEqual(str(context.exception), 'Environment should not feature both "lm" and "alm"')

    def test_parse_fail_when_lm_and_tnco_used(self):
        config_dict = self.test_helper.read_yaml_file('lm-and-tnco-key')
        with self.assertRaises(ConfigError) as context:
            ConfigIO().dict_to_config(config_dict)
        self.assertEqual(str(context.exception), 'Environment should not feature both "lm" and "tnco"')

    def test_parse_fail_when_alm_and_tnco_used(self):
        config_dict = self.test_helper.read_yaml_file('alm-and-tnco-key')
        with self.assertRaises(ConfigError) as context:
            ConfigIO().dict_to_config(config_dict)
        self.assertEqual(str(context.exception), 'Environment should not feature both "alm" and "tnco"')

    def test_parse_tnco_in_parts(self):
        config_io = ConfigIO()
        config_dict = self.test_helper.read_yaml_file('tnco-in-parts')
        config = config_io.dict_to_config(config_dict)
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

    def test_parse_arm_in_parts(self):
        config_io = ConfigIO()
        config_dict = self.test_helper.read_yaml_file('arm-in-parts')
        config = config_io.dict_to_config(config_dict)
        self.assertIn('test', config.environments)
        test_group_config = config.environments.get('test')
        arms_config = test_group_config.arms
        self.assertEqual(len(arms_config), 2)
        self.assertIn('first', arms_config)
        first_arm_config = arms_config['first']
        self.assertIsInstance(first_arm_config, ArmEnvironment)
        self.assertEqual(first_arm_config.address, 'http://test:1')
        self.assertEqual(first_arm_config.onboarding_addr, 'http://onboard')
        self.assertIn('second', arms_config)
        second_arm_config = arms_config['second']
        self.assertIsInstance(second_arm_config, ArmEnvironment)
        self.assertEqual(second_arm_config.address, 'https://test2:2')
        self.assertEqual(second_arm_config.onboarding_addr, 'http://onboard2')

    def test_parse_invalid_tnco(self):
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
            ConfigIO().dict_to_config(invalid_config)
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
            ConfigIO().dict_to_config(invalid_config)
        self.assertEqual(str(context.exception).split('[type=value_error')[0].strip(), 'Config error: 1 validation error for Config\nenvironments.test.arms.invalid\n  Value error, AnsibleRM environment cannot be configured without "address" property or "host" property')

    def test_config_to_file(self):
        config = Config(environments={
            'test': EnvironmentGroup(
                name='test',
                description='Just testing',
                tnco=TNCOEnvironment(address='https://localhost:80', secure=True, username='jack', client_id='client'),
                arms={
                    'defaultrm': ArmEnvironment(address='https://localhost:81')
                }
            )
        })

        target_path = os.path.join(self.tmp_dir, 'write-config.yaml')
        config_io = ConfigIO()
        config_io.config_to_file(config, target_path)

        self.assertTrue(os.path.exists(target_path))
        config_dict = self.test_helper.read_workspace_yaml_file('write-config.yaml')
        self.assertEqual(config_dict, {
            'environments': {
                'test': {
                    'description': 'Just testing',
                    'tnco': {
                        'address': 'https://localhost:80',
                        'secure': True,
                        'username': 'jack', 
                        'client_id': 'client'
                    },
                    'arms': {
                        'defaultrm': {
                            'address': 'https://localhost:81'
                        }
                    }
                }
            }
        })

    def test_config_to_file_backup_existing(self):
        config = Config(environments={
            'test': EnvironmentGroup(
                name='test',
                description='Just testing',
                tnco=TNCOEnvironment(address='https://localhost:80', secure=True, username='jack', client_id='client'),
                arms={
                    'defaultrm': ArmEnvironment(address='https://localhost:81')
                }
            )
        })

        target_path = os.path.join(self.tmp_dir, 'write-config.yaml')
        ConfigIO().config_to_file(config, target_path)

        config.environments['test'].description = 'Updated description'
        ConfigIO().config_to_file(config, target_path, backup_existing=True)

        self.assertTrue(os.path.exists(target_path))
        config_dict = self.test_helper.read_workspace_yaml_file('write-config.yaml')
        self.assertEqual(config_dict, {
            'environments': {
                'test': {
                    'description': 'Updated description',
                    'tnco': {
                        'address': 'https://localhost:80',
                        'secure': True,
                        'username': 'jack', 
                        'client_id': 'client'
                    },
                    'arms': {
                        'defaultrm': {
                            'address': 'https://localhost:81'
                        }
                    }
                }
            }
        })

        bkup_config_dict = self.test_helper.read_workspace_yaml_file('write-config.yaml.bak')
        self.assertEqual(bkup_config_dict, {
            'environments': {
                'test': {
                    'description': 'Just testing',
                    'tnco': {
                        'address': 'https://localhost:80',
                        'secure': True,
                        'username': 'jack', 
                        'client_id': 'client'
                    },
                    'arms': {
                        'defaultrm': {
                            'address': 'https://localhost:81'
                        }
                    }
                }
            }
        })

    def test_config_to_dict(self):
        config = Config(environments={
            'test': EnvironmentGroup(
                name='test',
                description='Just testing',
                tnco=TNCOEnvironment(address='https://localhost:80', secure=True, username='jack', client_id='client'),
                arms={
                    'defaultrm': ArmEnvironment(address='https://localhost:81')
                }
            )
        })

        config_dict = ConfigIO().config_to_dict(config)
        self.assertEqual(config_dict, {
            'environments': {
                'test': {
                    'description': 'Just testing',
                    'tnco': {
                        'address': 'https://localhost:80',
                        'secure': True,
                        'username': 'jack', 
                        'client_id': 'client'
                    },
                    'arms': {
                        'defaultrm': {
                            'address': 'https://localhost:81'
                        }
                    }
                }
            }
        })