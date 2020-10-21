import unittest
import tempfile
import shutil
import os
import yaml
from pathlib import Path
from unittest.mock import patch
from lmctl.config import ConfigError, ConfigFinder

class TestConfigFinder(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def __write_file(self, file_path, content):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            f.write(content)

    @patch('lmctl.config.finder.Path')
    def test_find_default_location(self, mock_path):
        # Mock home directory
        mock_path.home.return_value = Path(self.tmp_dir)
        default_config_file_path = os.path.join(self.tmp_dir, '.lmctl', 'config.yaml')
        self.__write_file(default_config_file_path, 'test')
        finder = ConfigFinder()
        self.assertEqual(default_config_file_path, finder.find())
    
    def test_find_by_path(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, 'test')
        finder = ConfigFinder(config_file_path)
        self.assertEqual(config_file_path, finder.find())
    
    def test_fail_path_not_found(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        with self.assertRaises(ConfigError) as context:
            ConfigFinder(config_file_path).find()
        self.assertEqual(str(context.exception), 'Provided config path does not exist: {0}'.format(config_file_path))
    
    def test_find_by_env_var(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, 'test')
        os.environ['LMCONFIG'] = config_file_path
        try:
            finder = ConfigFinder(None, 'LMCONFIG')
            self.assertEqual(config_file_path, finder.find())
        finally:
            del os.environ['LMCONFIG']
    
    def test_fail_env_var_path_not_found(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        os.environ['LMCONFIG'] = config_file_path
        try:
            with self.assertRaises(ConfigError) as context:
                ConfigFinder(None, 'LMCONFIG').find()
            self.assertEqual(str(context.exception), 'Config path on environment variable LMCONFIG does not exist: {0}'.format(config_file_path))
        finally:
            del os.environ['LMCONFIG']

    def test_fail_env_var_not_set(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        self.__write_file(config_file_path, 'test')
        if os.environ.get('LMCONFIG') != None:
            del os.environ['LMCONFIG']
        with self.assertRaises(ConfigError) as context:
            ConfigFinder(None, 'LMCONFIG').find()
        expected_default_path = str(Path.home().joinpath('.lmctl').joinpath('config.yaml'))
        self.assertEqual(str(context.exception), f'Config file could not be found at default location "{expected_default_path}" or from environment variable LMCONFIG')

    def test_find_by_path_not_env_var(self):
        config_file_path = os.path.join(self.tmp_dir, 'config.yaml')
        config_env_file_path = os.path.join(self.tmp_dir, 'env_config.yaml')
        self.__write_file(config_file_path, 'test')
        self.__write_file(config_env_file_path, 'test')
        os.environ['LMCONFIG'] = config_env_file_path
        try:
            finder = ConfigFinder(config_file_path, 'LMCONFIG')
            self.assertEqual(config_file_path, finder.find())
        finally:
            del os.environ['LMCONFIG']
    
