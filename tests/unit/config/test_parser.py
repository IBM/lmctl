import unittest
import unittest.mock as mock
import tempfile
import shutil
import os
import yaml
from lmctl.config import Config, ConfigParser, ConfigParserError
from lmctl.environment.group import EnvironmentGroup, EnvironmentGroup
from lmctl.environment.lmenv import LmEnvironment
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
      auth_protocol: http
      username: jack
      password: secret
      kami_port: 34567
      kami_protocol: https
    arm:
      default:
        host: default
        port: 8765
        protocol: http
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
      address: http://some.lm.example.com
    arm:
      default:
        address: http://some.arm.example.com
"""
class TestConfigParser(unittest.TestCase):

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
        self.assertIsInstance(test_env.lm, LmEnvironment)
        self.assertEqual(test_env.lm.address, 'https://127.0.0.1:1111')
        self.assertEqual(test_env.lm.auth_address, 'http://auth:4643')
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
        with self.assertRaises(ConfigParserError) as context:
            ConfigParser().from_file(config_file_path)
        self.assertEqual(str(context.exception), 'The configuration file provided ({0}) appears to be a 2.0.X file. \
            Lmctl attempted to rewrite the file with updated syntax for 2.1.X but failed with the following error: Mocked error'.format(config_file_path))
