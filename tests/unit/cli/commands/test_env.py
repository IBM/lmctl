from lmctl.environment.group import EnvironmentGroup
import tests.unit.cli.commands.command_testing as command_testing
import os
import tempfile
import shutil
import yaml

from unittest.mock import patch

from lmctl.config import Config, ConfigIO
from lmctl.cli.entry import cli
from lmctl.cli.controller import clear_global_controller

class TestEnvCommands(command_testing.CommandTestCase):

    def setUp(self):
        super().setUp()

        clear_global_controller()
        
        self.write_config_patcher = patch('lmctl.cli.commands.login.write_config')
        self.mock_write_config = self.write_config_patcher.start()
        self.addCleanup(self.mock_write_config.stop)

        # Setup Config Path location        
        self.tmp_dir = tempfile.mkdtemp(prefix='lmctl-test')
        self.config_path = os.path.join(self.tmp_dir, 'lmctl-config.yaml')
        with open(self.config_path, 'w') as f:
            f.write(yaml.safe_dump({}))
        self.orig_lm_config = os.environ.get('LMCONFIG')
        os.environ['LMCONFIG'] = self.config_path

        self.global_config_patcher = patch('lmctl.cli.controller.get_global_config_with_path')
        self.mock_get_global_config = self.global_config_patcher.start()
        self.addCleanup(self.global_config_patcher.stop)
        def get_config(*args, **kwargs):
            config = ConfigIO().file_to_config(self.config_path)
            return (config, self.config_path)
        self.get_config = get_config
        self.mock_get_global_config.side_effect = get_config

    def tearDown(self):
        super().tearDown()

        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        if self.orig_lm_config is not None:
            os.environ['LMCONFIG'] = self.orig_lm_config

    def add_environment(self, name, make_active=False):
        config, config_path = self.get_config()
        config.environments[name] = EnvironmentGroup(name)
        if make_active:
            config.active_environment = name
        ConfigIO().config_to_file(config, config_path)

    def test_delete_env_with_name_and_active_raises_error(self):
        result = self.runner.invoke(cli, ['delete', 'env', 'TestA', '--active'])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli delete env [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli delete env --help\' for help.'
        expected_output += '\n\nError: Cannot not use "name" argument when using the "--active" option'
        self.assert_output(result, expected_output)

    def test_delete_env_by_name(self):
        self.add_environment('TestA')
        config = self.get_config()[0]
        self.assertIn('TestA', config.environments)

        result = self.runner.invoke(cli, ['delete', 'env', 'TestA'])
        self.assert_no_errors(result)
        config = self.get_config()[0]
        self.assertNotIn('TestA', config.environments)

    def test_delete_env_by_active(self):
        self.add_environment('TestA', make_active=True)
        config = self.get_config()[0]
        self.assertIn('TestA', config.environments)
        self.assertEqual(config.active_environment, 'TestA')

        result = self.runner.invoke(cli, ['delete', 'env', '--active'])
        self.assert_no_errors(result)
        config = self.get_config()[0]
        self.assertNotIn('TestA', config.environments)
        self.assertIsNone(config.active_environment)

    def test_delete_env_by_active_when_no_active_env_raises_error(self):
        self.add_environment('TestA')
        result = self.runner.invoke(cli, ['delete', 'env', '--active'])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli delete env [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli delete env --help\' for help.'
        expected_output += '\n\nError: Cannot use "--active" option when no active environment is set in config'
        self.assert_output(result, expected_output)

    def test_delete_env_does_not_exist_raises_error(self):
        result = self.runner.invoke(cli, ['delete', 'env', 'Dummy'])
        self.assert_has_system_exit(result)
        expected_output = 'No environment named "Dummy" could be found in current config file'
        self.assert_output(result, expected_output)

    def test_delete_env_does_not_exist_does_not_raise_error_when_ignore_missing(self):
        result = self.runner.invoke(cli, ['delete', 'env', 'Dummy', '--ignore-missing'])
        self.assert_no_errors(result)
        expected_output = '(Ignored) No environment named "Dummy" could be found in current config file'
        self.assert_output(result, expected_output)
