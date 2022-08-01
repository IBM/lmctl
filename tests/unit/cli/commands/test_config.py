from .command_testing import CommandTestCase
from lmctl.cli.entry import cli
from lmctl.config import get_config, Config
from unittest.mock import patch
import tempfile
import os
import shutil

test_config = '''\
environments:
  default:
    tnco: 
      address: http://example
      secure: True
      client_id: Tester
'''

class TestConfigTarget(CommandTestCase):

    def setUp(self):
        super().setUp()
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_created_config_is_parsable(self):
        target_path = os.path.join(self.tmp_dir, 'config.yaml')
        result = self.runner.invoke(cli, ['create', 'config', '--path', target_path])
        self.assertTrue(os.path.exists(target_path), msg='Config file not created')
        config = get_config(target_path)
        self.assertIsInstance(config, Config)
        self.assertIn('default', config.environments)

    def test_create_at_path(self):
        target_path = os.path.join(self.tmp_dir, 'config.yaml')
        result = self.runner.invoke(cli, ['create', 'config', '--path', target_path])
        self.assertTrue(os.path.exists(target_path), msg='Config file not created')

    def test_create_at_path_overwrite(self):
        target_path = os.path.join(self.tmp_dir, 'config.yaml')
        with open(target_path, 'w') as f:
            f.write('Existing content')
        result = self.runner.invoke(cli, ['create', 'config', '--path', target_path, '--overwrite'])
        config = get_config(target_path)
        self.assertIsInstance(config, Config)
    
    def test_create_at_path_that_exists_fails(self):
        target_path = os.path.join(self.tmp_dir, 'config.yaml')
        with open(target_path, 'w') as f:
            f.write('Existing content')
        result = self.runner.invoke(cli, ['create', 'config', '--path', target_path])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli create config [OPTIONS]'
        expected_output += '\nTry \'cli create config --help\' for help.'
        expected_output += f'\n\nError: Cannot create configuration file at path "{target_path}" because there is already a file there and "--overwrite" was not set'
        self.assert_output(result, expected_output)

    def test_create_also_creates_directory(self):
        target_dir = os.path.join(self.tmp_dir, 'somedir')
        target_path = os.path.join(target_dir, 'config.yaml')
        result = self.runner.invoke(cli, ['create', 'config', '--path', target_path])
        self.assertTrue(os.path.exists(target_dir), msg='Config directory not created')
        self.assertTrue(os.path.isdir(target_dir), msg='Expected a directory to be created')
        self.assertTrue(os.path.exists(target_path), msg='Config file not created')
        config = get_config(target_path)
        self.assertIsInstance(config, Config)

    def test_create_ok_with_existing_directory(self):
        target_dir = os.path.join(self.tmp_dir, 'somedir')
        os.makedirs(target_dir)
        target_path = os.path.join(target_dir, 'config.yaml')
        some_other_file = os.path.join(target_dir, 'someotherfile.yaml')
        with open(some_other_file, 'w') as f:
            f.write('Original content')
        result = self.runner.invoke(cli, ['create', 'config', '--path', target_path])
        self.assertTrue(os.path.exists(target_path), msg='Config file not created')
        config = get_config(target_path)
        self.assertIsInstance(config, Config)
        self.assertTrue(os.path.exists(some_other_file), msg='Existing file should not have been removed')
        with open(some_other_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, 'Original content')

    @patch('lmctl.cli.commands.config.find_config_location')
    def test_create_at_default_directory(self, mock_find_config_location):
        default_dir = os.path.join(self.tmp_dir, 'defaultdir')
        os.makedirs(default_dir)
        default_path = os.path.join(default_dir, 'config.yaml')
        mock_find_config_location.return_value = default_path
        result = self.runner.invoke(cli, ['create', 'config'])
        self.assertTrue(os.path.exists(default_path), msg='Config file not created')
        config = get_config(default_path)
        self.assertIsInstance(config, Config)

    @patch('lmctl.cli.commands.config.get_config_with_path')
    def test_get(self, mock_get_config):
        config_path = os.path.join(self.tmp_dir, 'config.yaml')
        with open(config_path, 'w') as f:
            f.write(test_config)
        mock_get_config.return_value = (Config(), config_path)
        result = self.runner.invoke(cli, ['get', 'config'])
        self.assert_no_errors(result)
        self.assert_output(result, test_config)

    @patch('lmctl.cli.commands.config.get_config_with_path')
    def test_get_print_path(self, mock_get_config):
        config_path = os.path.join(self.tmp_dir, 'config.yaml')
        with open(config_path, 'w') as f:
            f.write(test_config)
        mock_get_config.return_value = (Config(), config_path)
        result = self.runner.invoke(cli, ['get', 'config', '--print-path'])
        self.assert_no_errors(result)
        expected_output = f'Path: {config_path}'
        expected_output += '\n---\n'
        expected_output += test_config
        self.assert_output(result, expected_output)

    @patch('lmctl.cli.commands.config.get_config_with_path')
    def test_get_print_path_only(self, mock_get_config):
        config_path = os.path.join(self.tmp_dir, 'config.yaml')
        with open(config_path, 'w') as f:
            f.write(test_config)
        mock_get_config.return_value = (Config(), config_path)
        result = self.runner.invoke(cli, ['get', 'config', '--path-only'])
        self.assert_no_errors(result)
        expected_output = config_path
        self.assert_output(result, expected_output)


