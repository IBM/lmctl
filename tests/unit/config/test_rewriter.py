import unittest
import tempfile
import shutil
import os
import yaml
from lmctl.config import ConfigRewriter

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
      auth_address: 127.0.0.2
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
    auth_host: 127.0.0.2
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
                        'auth_address': '127.0.0.2',
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
