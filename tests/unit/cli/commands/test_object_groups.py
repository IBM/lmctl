from unittest import mock

import tests.unit.cli.commands.command_testing as command_testing
import tempfile
import os
import shutil
from unittest.mock import patch
from lmctl.cli.controller import clear_global_controller
from lmctl.cli.entry import cli
from lmctl.config import Config
from lmctl.environment import EnvironmentGroup, TNCOEnvironment

class TestObjectGroupsCommands(command_testing.CommandTestCase):

    def setUp(self):
        super().setUp()

        clear_global_controller()

        # Setup Config Path location
        self.tmp_dir = tempfile.mkdtemp(prefix='lmctl-test')
        self.config_path = os.path.join(self.tmp_dir, 'lmctl-config.yaml')
        self.orig_lm_config = os.environ.get('LMCONFIG')
        os.environ['LMCONFIG'] = self.config_path

        self.global_config_patcher = patch('lmctl.cli.controller.get_config_with_path')
        self.mock_get_global_config = self.global_config_patcher.start()
        self.addCleanup(self.global_config_patcher.stop)
        self.mock_get_global_config.return_value = (Config(
            active_environment='default',
            environments={
                'default': EnvironmentGroup(
                    name='default',
                    tnco=TNCOEnvironment(
                        address='https://mock.example.com',
                        secure=True,
                        token='123',
                        auth_mode='token'
                    )
                )
            }
        ), self.config_path)

    def tearDown(self):
        super().tearDown()

        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
        if self.orig_lm_config is not None:
            os.environ['LMCONFIG'] = self.orig_lm_config


    @mock.patch('lmctl.client.api.object_groups.ObjectGroupsAPI.query')
    def test_get_with_defaults(self, mocked_query):
        mocked_query.return_value = [{'id': '59799459-0067-4901-8265-a173196d3928', 'name': 'Domain1', 'description': 'Orchestration for Domain 1', 'isDefault': False}]
        result = self.runner.invoke(cli, [ 'get', 'objectgroups'])
        self.assert_no_errors(result)
        expected_output = '| ID                                   | Name    | Description                | Default   |'
        expected_output += '\n|--------------------------------------+---------+----------------------------+-----------|'
        expected_output += '\n| 59799459-0067-4901-8265-a173196d3928 | Domain1 | Orchestration for Domain 1 | False     |'
        self.assert_no_errors(result)
        self.assert_output(result, expected_output)

    @mock.patch('lmctl.client.api.object_groups.ObjectGroupsAPI.get')
    def test_get_with_id(self, mocked_query):
        mocked_query.return_value = {'id': '59799459-0067-4901-8265-a173196d3928', 'name': 'Domain1', 'description': 'Orchestration for Domain 1', 'isDefault': False}
        result = self.runner.invoke(cli, [ 'get', 'objectgroups', '59799459-0067-4901-8265-a173196d3928'])
        self.assert_no_errors(result)
        expected_output = '| ID                                   | Name    | Description                | Default   |'
        expected_output += '\n|--------------------------------------+---------+----------------------------+-----------|'
        expected_output += '\n| 59799459-0067-4901-8265-a173196d3928 | Domain1 | Orchestration for Domain 1 | False     |'
        self.assert_no_errors(result)
        self.assert_output(result, expected_output)

    @mock.patch('lmctl.client.api.object_groups.ObjectGroupsAPI.query')
    def test_get_with_permission(self, mocked_query):
        mocked_query.return_value = [{'id': '59799459-0067-4901-8265-a173196d3928', 'name': 'Domain1', 'description': 'Orchestration for Domain 1', 'isDefault': False}]
        result = self.runner.invoke(cli, [ 'get', 'objectgroups','--permission', 'SPINFAUTO_WRITE'])
        self.assert_no_errors(result)
        expected_output = '| ID                                   | Name    | Description                | Default   |'
        expected_output += '\n|--------------------------------------+---------+----------------------------+-----------|'
        expected_output += '\n| 59799459-0067-4901-8265-a173196d3928 | Domain1 | Orchestration for Domain 1 | False     |'
        self.assert_no_errors(result)
        self.assert_output(result, expected_output)

    @mock.patch('lmctl.client.api.object_groups.ObjectGroupsAPI.get_default')
    def test_get_default(self, mocked_query):
        mocked_query.return_value = {'id': '59799459-0067-4901-8265-a173196d3928', 'name': 'Domain1', 'description': 'Orchestration for Domain 1', 'isDefault': True}
        result = self.runner.invoke(cli, [ 'get', 'objectgroups', '--default'])
        self.assert_no_errors(result)
        expected_output = '| ID                                   | Name    | Description                | Default   |'
        expected_output += '\n|--------------------------------------+---------+----------------------------+-----------|'
        expected_output += '\n| 59799459-0067-4901-8265-a173196d3928 | Domain1 | Orchestration for Domain 1 | True      |'
        self.assert_no_errors(result)
        self.assert_output(result, expected_output)


    @mock.patch('lmctl.client.api.object_groups.ObjectGroupsAPI.query')
    def test_get_with_yaml(self, mocked_query):
        mocked_query.return_value = [{'id': '59799459-0067-4901-8265-a173196d3928', 'name': 'Domain1', 'description': 'Orchestration for Domain 1', 'isDefault': False}]
        result = self.runner.invoke(cli, [ 'get', 'objectgroups', '-o', 'yaml'])
        self.assert_no_errors(result)
        expected_output = 'items:'
        expected_output += '\n- id: 59799459-0067-4901-8265-a173196d3928'
        expected_output += '\n  name: Domain1'
        expected_output += '\n  description: Orchestration for Domain 1'
        expected_output += '\n  isDefault: false'
        expected_output += '\n'
        self.assert_no_errors(result)
        self.assert_output(result, expected_output)

    @mock.patch('lmctl.client.api.object_groups.ObjectGroupsAPI.query')
    def test_get_with_json(self, mocked_query):
        mocked_query.return_value = [{'id': '59799459-0067-4901-8265-a173196d3928', 'name': 'Domain1', 'description': 'Orchestration for Domain 1', 'isDefault': False}]
        result = self.runner.invoke(cli, [ 'get', 'objectgroups', '-o', 'json'])
        self.assert_no_errors(result)
        expected_output = '{'
        expected_output += '\n  "items": ['
        expected_output += '\n    {'
        expected_output += '\n      "id": "59799459-0067-4901-8265-a173196d3928",'
        expected_output += '\n      "name": "Domain1",'
        expected_output += '\n      "description": "Orchestration for Domain 1",'
        expected_output += '\n      "isDefault": false'
        expected_output += '\n    }'
        expected_output += '\n  ]'
        expected_output += '\n}'
        self.assert_no_errors(result)
