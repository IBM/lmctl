import tests.unit.cli.commands.command_testing as command_testing
import os
import tempfile
import shutil

from unittest.mock import patch
from lmctl.environment.group import EnvironmentGroup
from lmctl.environment.lmenv import TNCOEnvironment
from lmctl.cli.controller import clear_global_controller
from lmctl.cli.commands.whoami import whoami
from lmctl.config import ConfigIO, Config
from tests.unit.client.token_helper import build_a_token

class TestWhoAmICommands(command_testing.CommandTestCase):

    def setUp(self):
        super().setUp()

        clear_global_controller()

        self.tnco_env_client_patcher = patch('lmctl.environment.lmenv.TNCOClientBuilder')
        self.mock_tnco_client_builder_class = self.tnco_env_client_patcher.start()
        self.addCleanup(self.tnco_env_client_patcher.stop)
        self.mock_tnco_client_builder = self.mock_tnco_client_builder_class.return_value
        self.mock_tnco_client = self.mock_tnco_client_builder.build.return_value
        self.mock_tnco_client.get_access_token.return_value = build_a_token()
        
        # Setup Config Path location        
        self.tmp_dir = tempfile.mkdtemp(prefix='lmctl-test')
        self.config_path = os.path.join(self.tmp_dir, 'lmctl-config.yaml')
        self.orig_lm_config = os.environ.get('LMCONFIG')
        os.environ['LMCONFIG'] = self.config_path

    def tearDown(self):
        super().tearDown()
        
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        if self.orig_lm_config is not None:
            os.environ['LMCONFIG'] = self.orig_lm_config

    def _read_config(self):
        if not os.path.exists(self.config_path):
            self._write_config(Config())
        return ConfigIO().file_to_config(self.config_path)

    def _write_config(self, config: Config):
        ConfigIO().config_to_file(config, self.config_path)

    def _add_tnco_env(self, env_name: str, tnco_env: TNCOEnvironment):
        config = self._read_config()
        config.environments[env_name] = EnvironmentGroup(env_name, tnco=tnco_env)
        self._write_config(config)

    def _set_active_environment(self, env_name: str):
        config = self._read_config()
        config.active_environment = env_name
        self._write_config(config)

    def test_who_am_i_with_no_config_fails(self):
        result = self.runner.invoke(whoami)
        self.assert_has_system_exit(result)
        expected_output = f'Error: Failed to load configuration - Config path on environment variable LMCONFIG does not exist: {self.config_path}'
        self.assert_output(result, expected_output)

    def test_who_am_i_with_no_active_environment_fails(self):
        self._add_tnco_env('dev', TNCOEnvironment(address='https://ishtar.example.com', username='jack', password='test', secure=True))
        result = self.runner.invoke(whoami)
        self.assert_has_system_exit(result)
        expected_output = f'Error: active environment not configured. Run "lmctl use env <env-name>" to activate an environment'
        self.assert_output(result, expected_output)

    def test_who_am_i_with_environment_not_found_fails(self):
        self._set_active_environment('prod')
        result = self.runner.invoke(whoami)
        self.assert_has_system_exit(result)
        expected_output = f'Error: "active_environment" group set to "prod" but there is no environment with that name found in config'
        self.assert_output(result, expected_output)

    def test_who_am_i_with_active_environment_prints_output(self):
        self._add_tnco_env('dev', TNCOEnvironment(address='https://ishtar.example.com', username='jack', password='test', secure=True))
        self._set_active_environment('dev')

        result = self.runner.invoke(whoami)
        self.assert_no_errors(result)
        expected_output = 'User: jack'
        expected_output += '\nEnvironment: dev (https://ishtar.example.com)'
        self.assert_output(result, expected_output)
    
    def test_who_am_i_show_user_only_prints_output(self):
        self._add_tnco_env('dev', TNCOEnvironment(address='https://ishtar.example.com', username='jack', password='test', secure=True))
        self._set_active_environment('dev')

        result = self.runner.invoke(whoami, ['-u'])
        self.assert_no_errors(result)
        expected_output = 'jack'
        self.assert_output(result, expected_output)

    def test_who_am_i_with_show_env_and_show_user_fails(self):
        result = self.runner.invoke(whoami, ['-e', '-u'])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: whoami [OPTIONS]'
        expected_output += '\nTry \'whoami --help\' for help.'
        expected_output += '\n\nError: Cannot use "-e, --show-env" with "-u, --show-user" as they are mutually exclusive'
        self.assert_output(result, expected_output)

    def test_who_am_i_with_show_env_and_show_token_fails(self):
        result = self.runner.invoke(whoami, ['-e', '-t'])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: whoami [OPTIONS]'
        expected_output += '\nTry \'whoami --help\' for help.'
        expected_output += '\n\nError: Cannot use "-e, --show-env" with "-t, --show-token" as they are mutually exclusive'
        self.assert_output(result, expected_output)

    def test_who_am_i_with_show_user_and_show_token_fails(self):
        result = self.runner.invoke(whoami, ['-u', '-t'])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: whoami [OPTIONS]'
        expected_output += '\nTry \'whoami --help\' for help.'
        expected_output += '\n\nError: Cannot use "-u, --show-user" with "-t, --show-token" as they are mutually exclusive'
        self.assert_output(result, expected_output)

    def test_who_am_i_show_env_only_prints_output(self):
        self._add_tnco_env('dev', TNCOEnvironment(address='https://ishtar.example.com', username='jack', password='test', secure=True))
        self._set_active_environment('dev')

        result = self.runner.invoke(whoami, ['-e'])
        self.assert_no_errors(result)
        expected_output = 'dev (https://ishtar.example.com)'
        self.assert_output(result, expected_output)
    
    def test_who_am_i_show_token_only_prints_output(self):
        self._add_tnco_env('dev', TNCOEnvironment(address='https://ishtar.example.com', username='jack', password='test', secure=True))
        self._set_active_environment('dev')

        result = self.runner.invoke(whoami, ['-t'])
        self.assert_no_errors(result)
        mock_token = self.mock_tnco_client.get_access_token.return_value
        self.assert_output(result, mock_token)
    