import unittest
import unittest.mock as mock
import tempfile
import shutil
import os
import yaml
from lmctl.ctl.config import Ctl, ConfigRewriter, Config, ConfigParser, ConfigParserError, ConfigError, CtlConfigFinder
from lmctl.environment.group import EnvironmentGroup, EnvironmentGroup
from lmctl.environment.lmenv import LmEnvironment
from lmctl.environment.armenv import ArmEnvironment


OLD_CONFIG = """\
test:
  alm:
    ip_address: '127.0.0.1'
    secure_port: True
    auth_address: 127.0.0.2
"""
NEW_CONFIG = """\
## Lmctl has updated this file with the latest schema changes. A backup of your existing config file has been placed in the same directory with a .bak extension
environments:
  test:
    alm:
      host: 127.0.0.1
      protocol: https
      auth_host: 127.0.0.2
      secure: false
"""
OLD_CONFIG_NON_SECURE_PORT = """\
test:
  alm:
    secure_port: false
"""
NEW_CONFIG_NON_SECURE_PORT = """\
## Lmctl has updated this file with the latest schema changes. A backup of your existing config file has been placed in the same directory with a .bak extension
environments:
  test:
    alm:
      protocol: http
      secure: false
"""
OLD_CONFIG_KEEP_OTHER_PROPS = """\
test:
  alm:
    ip_address: '127.0.0.1'
    port: 7654
    username: jack
    secure_port: True
    auth_port: 4643
    auth_address: 127.0.0.2
    password: secret
"""
NEW_CONFIG_KEEP_OTHER_PROPS = """\
## Lmctl has updated this file with the latest schema changes. A backup of your existing config file has been placed in the same directory with a .bak extension
environments:
  test:
    alm:
      host: 127.0.0.1
      port: 7654
      username: jack
      protocol: https
      auth_port: 4643
      auth_host: 127.0.0.2
      password: secret
      secure: true
"""

OLD_ARM_CONFIG = """\
test:
  arm:
    first:
      ip_address: '127.0.0.1'
      port: 1111
      secure_port: True
      onboarding_addr: http://127.0.0.1
    second:
      ip_address: '127.0.0.2'
      port: 2222
      secure_port: False
      onboarding_addr: http://127.0.0.2
"""
NEW_ARM_CONFIG = """\
## Lmctl has updated this file with the latest schema changes. A backup of your existing config file has been placed in the same directory with a .bak extension
environments:
  test:
    arm:
      first:
        host: 127.0.0.1
        port: 1111
        protocol: https
      second:
        host: 127.0.0.2
        port: 2222
        protocol: http
"""
class TestConfigRewriter(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_rewrite_lm(self):
        file_path = os.path.join(self.tmp_dir, 'rewrite.yml')
        with open(file_path, 'w') as f:
            f.write(OLD_CONFIG)
        old_config_dict = yaml.safe_load(OLD_CONFIG)
        new_config_dict = ConfigRewriter(file_path, old_config_dict).rewrite()
        expected_new_config_dict = {
            'environments': {
                'test': {
                    'alm': {
                        'host': '127.0.0.1',
                        'protocol': 'https',
                        'auth_host': '127.0.0.2',
                        'secure': False
                    }
                }
            }
        }
        self.assertDictEqual(new_config_dict, expected_new_config_dict)
        backup_path = os.path.join(self.tmp_dir, 'rewrite.yml.bak')
        self.assertTrue(os.path.exists(backup_path))
        with open(backup_path, 'r') as f:
            backup_config = f.read()
        self.assertEqual(backup_config, OLD_CONFIG)
        with open(file_path, 'r') as f:
            new_config = f.read()
        self.assertEqual(new_config, NEW_CONFIG)

    def test_rewrite_non_secure_port_lm(self):
        file_path = os.path.join(self.tmp_dir, 'rewrite.yml')
        with open(file_path, 'w') as f:
            f.write(OLD_CONFIG_NON_SECURE_PORT)
        old_config_dict = yaml.safe_load(OLD_CONFIG_NON_SECURE_PORT)
        new_config_dict = ConfigRewriter(file_path, old_config_dict).rewrite()
        expected_new_config_dict = {
            'environments': {
                'test': {
                    'alm': {
                        'protocol': 'http',
                        'secure': False
                    }
                }
            }
        }
        self.assertDictEqual(new_config_dict, expected_new_config_dict)
        backup_path = os.path.join(self.tmp_dir, 'rewrite.yml.bak')
        self.assertTrue(os.path.exists(backup_path))
        with open(backup_path, 'r') as f:
            backup_config = f.read()
        self.assertEqual(backup_config, OLD_CONFIG_NON_SECURE_PORT)
        with open(file_path, 'r') as f:
            new_config = f.read()
        self.assertEqual(new_config, NEW_CONFIG_NON_SECURE_PORT)

    def test_rewrite_lm_keep_other_properties(self):
        file_path = os.path.join(self.tmp_dir, 'rewrite.yml')
        with open(file_path, 'w') as f:
            f.write(OLD_CONFIG_KEEP_OTHER_PROPS)
        old_config_dict = yaml.safe_load(OLD_CONFIG_KEEP_OTHER_PROPS)
        new_config_dict = ConfigRewriter(file_path, old_config_dict).rewrite()
        expected_new_config_dict = {
            'environments': {
                'test': {
                    'alm': {
                        'host': '127.0.0.1',
                        'protocol': 'https',
                        'auth_host': '127.0.0.2',
                        'port': 7654,
                        'username': 'jack',
                        'auth_port': 4643,
                        'password': 'secret',
                        'secure': True
                    }
                }
            }
        }
        self.assertDictEqual(new_config_dict, expected_new_config_dict)
        backup_path = os.path.join(self.tmp_dir, 'rewrite.yml.bak')
        self.assertTrue(os.path.exists(backup_path))
        with open(backup_path, 'r') as f:
            backup_config = f.read()
        self.assertEqual(backup_config, OLD_CONFIG_KEEP_OTHER_PROPS)
        with open(file_path, 'r') as f:
            new_config = f.read()
        self.assertEqual(new_config, NEW_CONFIG_KEEP_OTHER_PROPS)

    def test_rewrite_arm(self):
        file_path = os.path.join(self.tmp_dir, 'rewrite.yml')
        with open(file_path, 'w') as f:
            f.write(OLD_ARM_CONFIG)
        old_config_dict = yaml.safe_load(OLD_ARM_CONFIG)
        new_config_dict = ConfigRewriter(file_path, old_config_dict).rewrite()
        expected_new_config_dict = {
            'environments': {
                'test': {
                    'arm': {
                        'first': {
                            'host': '127.0.0.1',
                            'protocol': 'https',
                            'port': 1111
                        },
                        'second': {
                            'host': '127.0.0.2',
                            'protocol': 'http',
                            'port': 2222
                        }
                    }
                }
            }
        }
        self.assertDictEqual(new_config_dict, expected_new_config_dict)
        backup_path = os.path.join(self.tmp_dir, 'rewrite.yml.bak')
        self.assertTrue(os.path.exists(backup_path))
        with open(backup_path, 'r') as f:
            backup_config = f.read()
        self.assertEqual(backup_config, OLD_ARM_CONFIG)
        with open(file_path, 'r') as f:
            new_config = f.read()
        self.assertEqual(new_config, NEW_ARM_CONFIG)


PARSER_TEST_CONFIG = """\
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
    arm:
      default:
        host: default
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
        self.__write_file(config_file_path, PARSER_TEST_CONFIG)
        config = ConfigParser().from_file(config_file_path)
        self.assertIsNotNone(config)
        self.assertIsInstance(config, Config)
        self.assertEqual(len(config.environments), 2)
        self.assertIn('test', config.environments)
        test_env = config.environments['test']
        self.assertIsInstance(test_env, EnvironmentGroup)
        self.assertIsInstance(test_env.lm, LmEnvironment)
        self.assertEqual(test_env.lm.host, '127.0.0.1')
        self.assertEqual(test_env.lm.port, 1111)
        self.assertEqual(test_env.lm.protocol, 'https')
        self.assertEqual(test_env.lm.auth_host, 'auth')
        self.assertEqual(test_env.lm.auth_port, 4643)
        self.assertEqual(test_env.lm.username, 'jack')
        self.assertEqual(test_env.lm.password, 'secret')
        self.assertEqual(test_env.lm.auth_protocol, 'http')
        arms_config = test_env.arms
        self.assertEqual(len(arms_config), 1)
        default_arm_config = arms_config['default']
        self.assertIsInstance(default_arm_config, ArmEnvironment)
        self.assertEqual(default_arm_config.host, 'default')
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
        self.assertEqual(testlm_env.lm.host, '127.0.0.1')
        self.assertEqual(testlm_env.lm.protocol, 'https')
        self.assertEqual(testlm_env.lm.auth_host, '127.0.0.2')
        self.assertEqual(testlm_env.lm.secure, True)
        self.assertEqual(testlm_env.lm.username, 'jack')
        testarm_env = config.environments['testarm']
        self.assertEqual(testarm_env.arms['default'].host, '127.0.0.3')
        self.assertEqual(testarm_env.arms['default'].protocol, 'http')

    @mock.patch('lmctl.ctl.config.ConfigRewriter.rewrite')
    def test_rewrite_fails(self, mock_rewrite):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, OLD_PARSER_TEST_CONFIG)
        mock_rewrite.side_effect = ValueError('Mocked error')
        with self.assertRaises(ConfigParserError) as context:
            ConfigParser().from_file(config_file_path)
        self.assertEqual(str(context.exception), 'The configuration file provided ({0}) appears to be a 2.0.X file. \
            Lmctl attempted to rewrite the file with updated syntax for 2.1.X but failed with the following error: Mocked error'.format(config_file_path))

class TestCtlConfigFinder(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def __write_file(self, file_path, content):
        with open(file_path, 'w') as f:
            f.write(content)

    def test_find_by_path(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, 'test')
        finder = CtlConfigFinder(config_file_path)
        self.assertEqual(config_file_path, finder.find())
    
    def test_fail_path_not_found(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        with self.assertRaises(ConfigError) as context:
            CtlConfigFinder(config_file_path).find()
        self.assertEqual(str(context.exception), 'Path provided to load control config does not exist: {0}'.format(config_file_path))
    
    def test_find_by_env_var(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, 'test')
        os.environ['LMCONFIG'] = config_file_path
        try:
            finder = CtlConfigFinder(None, 'LMCONFIG')
            self.assertEqual(config_file_path, finder.find())
        finally:
            del os.environ['LMCONFIG']
    
    def test_fail_env_var_path_not_found(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        os.environ['LMCONFIG'] = config_file_path
        try:
            with self.assertRaises(ConfigError) as context:
                CtlConfigFinder(None, 'LMCONFIG').find()
            self.assertEqual(str(context.exception), 'Config environment variable LMCONFIG path does not exist: {0}'.format(config_file_path))
        finally:
            del os.environ['LMCONFIG']

    def test_fail_env_var_not_set(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, 'test')
        if os.environ.get('LMCONFIG') != None:
            del os.environ['LMCONFIG']
        with self.assertRaises(ConfigError) as context:
            CtlConfigFinder(None, 'LMCONFIG').find()
        self.assertEqual(str(context.exception), 'Config environment variable LMCONFIG is not set'.format(config_file_path))

    def test_find_by_path_not_env_var(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        config_env_file_path = os.path.join(self.tmp_dir, 'env_config.yaml')
        self.__write_file(config_file_path, 'test')
        self.__write_file(config_env_file_path, 'test')
        os.environ['LMCONFIG'] = config_env_file_path
        try:
            finder = CtlConfigFinder(config_file_path, 'LMCONFIG')
            self.assertEqual(config_file_path, finder.find())
        finally:
            del os.environ['LMCONFIG']
    

class TestCtl(unittest.TestCase):

    def test_init(self):
        environments = {
            'groupA': EnvironmentGroup('groupA', '', LmEnvironment('alm', 'host'), {'defaultrm': ArmEnvironment('defaultrm', 'host')}),
            'groupB': EnvironmentGroup('groupB', '', LmEnvironment('alm', 'hostB'), {'defaultrm': ArmEnvironment('defaultrm', 'hostB')})
        }
        config = Config(environments)
        ctl = Ctl(config)
        self.assertEqual(len(ctl.environments), 2)
        groupA_env = ctl.environment_group_named('groupA')
        self.assertIsNotNone(groupA_env)
        self.assertIsInstance(groupA_env, EnvironmentGroup)
        groupB_env = ctl.environment_group_named('groupB')
        self.assertIsNotNone(groupB_env)
        self.assertIsInstance(groupB_env, EnvironmentGroup)

    def test_environment_group_named_fails_when_not_found(self):
        config = Config({})
        ctl = Ctl(config)
        with self.assertRaises(ConfigError) as context:
            ctl.environment_group_named('groupA')
        self.assertEqual(str(context.exception), 'No environment group with name: groupA')