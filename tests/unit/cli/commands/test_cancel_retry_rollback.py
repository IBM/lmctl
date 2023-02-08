import tests.unit.cli.commands.command_testing as command_testing
import tempfile
import os
import shutil
from unittest.mock import patch
from lmctl.cli.controller import clear_global_controller
from lmctl.cli.commands.login import login
from lmctl.config import ConfigFinder, Config
from lmctl.environment import EnvironmentGroup, TNCOEnvironment
import lmctl.cli.commands.processes as process_cmds


class TestIntentCommands(command_testing.CommandTestCase):

    def setUp(self):
        super().setUp()

        clear_global_controller()

        self.tnco_env_client_patcher = patch('lmctl.environment.lmenv.TNCOClientBuilder')
        self.mock_tnco_client_builder_class = self.tnco_env_client_patcher.start()
        self.addCleanup(self.tnco_env_client_patcher.stop)
        self.mock_tnco_client_builder = self.mock_tnco_client_builder_class.return_value
        self.mock_tnco_client = self.mock_tnco_client_builder.build.return_value
        self.mock_tnco_client.get_access_token.return_value = '123'


    def test_cancel_intent(self):
        result = self.runner.invoke(process_cmds.cancel, ['process', '8475f402-cb6f-4ef1-a379-77c7e20cdf72'])
        self.assert_no_errors(result)
        expected_output = 'Accepted - Cancel request for process: 8475f402-cb6f-4ef1-a379-77c7e20cdf72'
        self.assert_output(result, expected_output)
        self.mock_tnco_client.assemblies.intent_cancel.assert_called_once_with({'processId': '8475f402-cb6f-4ef1-a379-77c7e20cdf72'})

    def test_retry_intent(self):
        result = self.runner.invoke(process_cmds.retry, ['process', '8475f402-cb6f-4ef1-a379-77c7e20cdf72'])
        self.assert_no_errors(result)
        expected_output = 'Accepted - Retry request for process: 8475f402-cb6f-4ef1-a379-77c7e20cdf72'
        self.assert_output(result, expected_output)
        self.mock_tnco_client.assemblies.intent_retry.assert_called_once_with({'processId': '8475f402-cb6f-4ef1-a379-77c7e20cdf72'})

    def test_rollback_intent(self):
        result = self.runner.invoke(process_cmds.rollback, ['process', '8475f402-cb6f-4ef1-a379-77c7e20cdf72'])
        self.assert_no_errors(result)
        expected_output = 'Accepted - Rollback request for process: 8475f402-cb6f-4ef1-a379-77c7e20cdf72'
        self.assert_output(result, expected_output)
        self.mock_tnco_client.assemblies.intent_rollback.assert_called_once_with({'processId': '8475f402-cb6f-4ef1-a379-77c7e20cdf72'})