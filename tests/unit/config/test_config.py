import unittest
import os
import tempfile
import shutil
from lmctl.config import get_config, ConfigError

TEST_CONFIG = '''\
environments:
  test: 
    description: A test env
'''

class TestGetConfig(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def __write_file(self, file_path, content):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)

    def test_get_config_at_path(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, TEST_CONFIG)
        config, config_path = get_config(config_file_path)
        self.assertEqual(config_path, config_file_path)
        self.assertTrue('test' in config.environments)

    def test_get_config_at_path_not_found(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        with self.assertRaises(ConfigError) as context:
            get_config(config_file_path)
        self.assertEqual(str(context.exception), f'Provided config path does not exist: {config_file_path}')

    def test_use_config_finder_when_no_path(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, TEST_CONFIG)
        os.environ['LMCONFIG'] = config_file_path
        try:
            config, config_path = get_config()
        finally:
            del os.environ['LMCONFIG']
        self.assertEqual(config_path, config_file_path)
        self.assertTrue('test' in config.environments)
