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

class TestProcessCommands(command_testing.CommandTestCase):

    def setUp(self):
        super().setUp()

        clear_global_controller()

        # Setup Config Path location
        self.tmp_dir = tempfile.mkdtemp(prefix='lmctl-test')
        self.config_path = os.path.join(self.tmp_dir, 'lmctl-config.yaml')
        self.orig_lm_config = os.environ.get('LMCONFIG')
        os.environ['LMCONFIG'] = self.config_path

        self.global_config_patcher = patch('lmctl.cli.controller.get_global_config_with_path')
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


    @mock.patch('lmctl.client.api.permission_type.PermissionTypesAPI.query')
    def test_get_with_permission_type(self, mocked_query):
        mocked_query.return_value = [{
                                        'name': 'OBJECTGROUP_READ',
                                        'description': 'Read Object Groups'
                                    }, {
                                        'name': 'OBJECTGROUP_WRITE',
                                        'description': 'Write Object Groups'
                                    }, {
                                        'name': 'NSDESMGT_READ',
                                        'description': 'Read Assembly Descriptors'
                                    }, {
                                        'name': 'NSDESMGT_WRITE',
                                        'description': 'Write Assembly Descriptors'
                                    }, {
                                        'name': 'NSINSTSMGT_READ',
                                        'description': 'Read Assembly Instances'
                                    }, {
                                        'name': 'NSINSTSMGT_WRITE',
                                        'description': 'Write Assembly Instances'
                                    }, {
                                        'name': 'INTENTREQSLMGT_EXECUTE',
                                        'description': 'Execute (Create) Assembly Instances'
                                    }, {
                                        'name': 'INTENTREQSOPS_EXECUTE',
                                        'description': 'Execute (Heal, Scale) Assembly Instances'
                                    }, {
                                        'name': 'RESOURCEPKG_WRITE',
                                        'description': 'Write Resource Packages'
                                    }, {
                                        'name': 'DEPLOYLOCMGT_READ',
                                        'description': 'Read Deployment Locations'
                                    }, {
                                        'name': 'DEPLOYLOCMGT_WRITE',
                                        'description': 'Write Deployment Locations'
                                    }, {
                                        'name': 'RMDRVRKEYS_READ',
                                        'description': 'Read Infrastracture Keys'
                                    }, {
                                        'name': 'RMDRVRKEYS_WRITE',
                                        'description': 'Write Infrastracture Keys'
                                    }, {
                                        'name': 'SECRET_READ',
                                        'description': 'Read Secrets'
                                    }, {
                                        'name': 'SECRET_WRITE',
                                        'description': 'Write Secrets'
                                    }, {
                                        'name': 'BEHVRSCENEXEC_READ',
                                        'description': 'Read Behaviour Tests'
                                    }, {
                                        'name': 'BEHVRSCENEXEC_WRITE',
                                        'description': 'Write Behaviour Tests'
                                    }, {
                                        'name': 'BEHVRSCENEXEC_EXECUTE',
                                        'description': 'Execute Behaviour Tests'
                                    }, {
                                        'name': 'SPINF_READ',
                                        'description': 'Read SitePlanner Objects'
                                    }, {
                                        'name': 'SPINF_WRITE',
                                        'description': 'Write SitePlanner Objects'
                                    }, {
                                        'name': 'SPINFAUTO_READ',
                                        'description': 'Read SitePlanner Automation Contexts'
                                    }, {
                                        'name': 'SPINFAUTO_WRITE',
                                        'description': 'Write SitePlanner Automation Contexts'
                                    }, {
                                        'name': 'SPINFAUTO_EXECUTE',
                                        'description': 'Execute SitePlanner Automation Contexts'
                                    }, {
                                        'name': 'SPMNGDENT_READ',
                                        'description': 'Read SitePlanner Managed Entities'
                                    }, {
                                        'name': 'SPMNGDENT_WRITE',
                                        'description': 'Write SitePlanner Managed Entities'
                                    }, {
                                        'name': 'SPMNGDENTAUTO_EXECUTE',
                                        'description': 'Execute SitePlanner Managed Entities'
                                    }]
        result = self.runner.invoke(cli, [ 'get', 'permissiontype'])
        self.assert_no_errors(result)
        expected_output = '| Name                   | Description                              |'
        expected_output += '\n|------------------------+------------------------------------------|'
        expected_output += '\n| OBJECTGROUP_READ       | Read Object Groups                       |'
        expected_output += '\n| OBJECTGROUP_WRITE      | Write Object Groups                      |'
        expected_output += '\n| NSDESMGT_READ          | Read Assembly Descriptors                |'
        expected_output += '\n| NSDESMGT_WRITE         | Write Assembly Descriptors               |'
        expected_output += '\n| NSINSTSMGT_READ        | Read Assembly Instances                  |'
        expected_output += '\n| NSINSTSMGT_WRITE       | Write Assembly Instances                 |'
        expected_output += '\n| INTENTREQSLMGT_EXECUTE | Execute (Create) Assembly Instances      |'
        expected_output += '\n| INTENTREQSOPS_EXECUTE  | Execute (Heal, Scale) Assembly Instances |'
        expected_output += '\n| RESOURCEPKG_WRITE      | Write Resource Packages                  |'
        expected_output += '\n| DEPLOYLOCMGT_READ      | Read Deployment Locations                |'
        expected_output += '\n| DEPLOYLOCMGT_WRITE     | Write Deployment Locations               |'
        expected_output += '\n| RMDRVRKEYS_READ        | Read Infrastracture Keys                 |'
        expected_output += '\n| RMDRVRKEYS_WRITE       | Write Infrastracture Keys                |'
        expected_output += '\n| SECRET_READ            | Read Secrets                             |'
        expected_output += '\n| SECRET_WRITE           | Write Secrets                            |'
        expected_output += '\n| BEHVRSCENEXEC_READ     | Read Behaviour Tests                     |'
        expected_output += '\n| BEHVRSCENEXEC_WRITE    | Write Behaviour Tests                    |'
        expected_output += '\n| BEHVRSCENEXEC_EXECUTE  | Execute Behaviour Tests                  |'
        expected_output += '\n| SPINF_READ             | Read SitePlanner Objects                 |'
        expected_output += '\n| SPINF_WRITE            | Write SitePlanner Objects                |'
        expected_output += '\n| SPINFAUTO_READ         | Read SitePlanner Automation Contexts     |'
        expected_output += '\n| SPINFAUTO_WRITE        | Write SitePlanner Automation Contexts    |'
        expected_output += '\n| SPINFAUTO_EXECUTE      | Execute SitePlanner Automation Contexts  |'
        expected_output += '\n| SPMNGDENT_READ         | Read SitePlanner Managed Entities        |'
        expected_output += '\n| SPMNGDENT_WRITE        | Write SitePlanner Managed Entities       |'
        expected_output += '\n| SPMNGDENTAUTO_EXECUTE  | Execute SitePlanner Managed Entities     |'
        self.assert_no_errors(result)
        self.assert_output(result, expected_output)