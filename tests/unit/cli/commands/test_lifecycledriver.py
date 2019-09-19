import tests.unit.cli.commands.command_testing as command_testing
import lmctl.drivers.lm.base as lm_drivers
import lmctl.cli.commands.lifecycledriver as lifecycledriver_cmds
from unittest.mock import patch
from tests.common.simulations.lm_simulator import LmSimulator

class TestLifecycleDriverCommands(command_testing.CommandTestCase):

    def setUp(self):
        super().setUp()
        # Created simulated LM session when requested
        self.lm_sim = LmSimulator().start()
        create_lm_session_patcher = patch('lmctl.cli.ctlmgmt.create_lm_session')
        self.mock_create_lm_session = create_lm_session_patcher.start()
        self.mock_create_lm_session.return_value = self.lm_sim.as_mocked_session()
        self.addCleanup(create_lm_session_patcher.stop)

    def test_add_with_defaults(self):
        result = self.runner.invoke(lifecycledriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com'])
        self.assert_no_errors(result)
        expected_id = None
        for lifecycle_driver_id, lifecycle_driver in self.lm_sim.lifecycle_drivers.items():
            expected_id = lifecycle_driver_id
        expected_output = '| id                                   | type    | baseUri                       |'
        expected_output += '\n|--------------------------------------+---------+-------------------------------|'
        expected_output += '\n| {0} | Ansible | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_add_with_type(self):
        result = self.runner.invoke(lifecycledriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--type', 'Shell'])
        self.assert_no_errors(result)
        expected_id = None
        for lifecycle_driver_id, lifecycle_driver in self.lm_sim.lifecycle_drivers.items():
            expected_id = lifecycle_driver_id
        expected_output = '| id                                   | type   | baseUri                       |'
        expected_output += '\n|--------------------------------------+--------+-------------------------------|'
        expected_output += '\n| {0} | Shell  | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_add_with_config(self):
        result = self.runner.invoke(lifecycledriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_id = None
        for lifecycle_driver_id, lifecycle_driver in self.lm_sim.lifecycle_drivers.items():
            expected_id = lifecycle_driver_id
        expected_output = '| id                                   | type    | baseUri                       |'
        expected_output += '\n|--------------------------------------+---------+-------------------------------|'
        expected_output += '\n| {0} | Ansible | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_add_with_pwd(self):
        result = self.runner.invoke(lifecycledriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_id = None
        for lifecycle_driver_id, lifecycle_driver in self.lm_sim.lifecycle_drivers.items():
            expected_id = lifecycle_driver_id
        expected_output = '| id                                   | type    | baseUri                       |'
        expected_output += '\n|--------------------------------------+---------+-------------------------------|'
        expected_output += '\n| {0} | Ansible | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_add_with_output_json_format(self):
        result = self.runner.invoke(lifecycledriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '-f', 'json'])
        self.assert_no_errors(result)
        expected_id = None
        for lifecycle_driver_id, lifecycle_driver in self.lm_sim.lifecycle_drivers.items():
            expected_id = lifecycle_driver_id
        expected_output = '{'
        expected_output += '\n  \"type\": \"Ansible\",'
        expected_output += '\n  \"baseUri\": \"http://mockdriver.example.com\",'
        expected_output += '\n  \"id\": \"{0}\"'.format(expected_id)
        expected_output += '\n}'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_add_with_output_yaml_format(self):
        result = self.runner.invoke(lifecycledriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '-f', 'yaml'])
        self.assert_no_errors(result)
        expected_id = None
        for lifecycle_driver_id, lifecycle_driver in self.lm_sim.lifecycle_drivers.items():
            expected_id = lifecycle_driver_id
        expected_output = 'baseUri: http://mockdriver.example.com'
        expected_output += '\nid: {0}'.format(expected_id)
        expected_output += '\ntype: Ansible\n'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_add_handles_lm_driver_error(self):
        self.mock_create_lm_session.return_value.lifecycle_driver_mgmt_driver.add_lifecycle_driver.side_effect = lm_drivers.LmDriverException('Mocked error')
        result = self.runner.invoke(lifecycledriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occured: Mocked error'
        self.assert_output(result, expected_output)
        
    def test_delete_with_defaults(self):
        lifecycle_driver_id = '123'
        self.lm_sim.add_lifecycle_driver({'id': lifecycle_driver_id})
        result = self.runner.invoke(lifecycledriver_cmds.delete, ['TestEnv', lifecycle_driver_id])
        self.assert_no_errors(result)
        expected_output = 'Deleting lifecycle driver: {0}...'.format(lifecycle_driver_id)
        expected_output += '\nDeleted lifecycle driver: {0}'.format(lifecycle_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_delete_with_config(self):
        lifecycle_driver_id = '123'
        self.lm_sim.add_lifecycle_driver({'id': lifecycle_driver_id})
        result = self.runner.invoke(lifecycledriver_cmds.delete, ['TestEnv', lifecycle_driver_id, '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_output = 'Deleting lifecycle driver: {0}...'.format(lifecycle_driver_id)
        expected_output += '\nDeleted lifecycle driver: {0}'.format(lifecycle_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_delete_with_pwd(self):
        lifecycle_driver_id = '123'
        self.lm_sim.add_lifecycle_driver({'id': lifecycle_driver_id})
        result = self.runner.invoke(lifecycledriver_cmds.delete, ['TestEnv', lifecycle_driver_id, '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_output = 'Deleting lifecycle driver: {0}...'.format(lifecycle_driver_id)
        expected_output += '\nDeleted lifecycle driver: {0}'.format(lifecycle_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_delete_handles_lm_driver_error(self):
        result = self.runner.invoke(lifecycledriver_cmds.delete, ['TestEnv', '987'])
        self.assert_has_system_exit(result)
        expected_output = 'Deleting lifecycle driver: 987...'
        expected_output += '\nLM error occured: No lifecycle driver with id 987'
        self.assert_output(result, expected_output)

    def test_delete_by_type(self):
        lifecycle_driver_id = '123'
        self.lm_sim.add_lifecycle_driver({'id': lifecycle_driver_id, 'type': 'Ansible'})
        result = self.runner.invoke(lifecycledriver_cmds.delete, ['TestEnv', '--type', 'Ansible'])
        self.assert_no_errors(result)
        expected_output = 'Found lifecycle driver matching type \'Ansible\'. Id: 123'
        expected_output += '\nDeleting lifecycle driver: {0}...'.format(lifecycle_driver_id)
        expected_output += '\nDeleted lifecycle driver: {0}'.format(lifecycle_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
    
    def test_delete_by_type_not_found(self):
        result = self.runner.invoke(lifecycledriver_cmds.delete, ['TestEnv', '--type', 'Ansible'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occured: No lifecycle driver with type Ansible'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
    
    def test_delete_without_id_or_type_fails(self):
        result = self.runner.invoke(lifecycledriver_cmds.delete, ['TestEnv'])
        self.assert_has_system_exit(result)
        expected_output = 'Error: Must specify driver-id argument or type option'
        self.assert_output(result, expected_output)
        
    def test_get_with_defaults(self):
        lifecycle_driver_id = '123'
        self.lm_sim.add_lifecycle_driver({'id': lifecycle_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(lifecycledriver_cmds.get, ['TestEnv', lifecycle_driver_id])
        self.assert_no_errors(result)
        expected_output = '|   id | type    | baseUri     |'
        expected_output += '\n|------+---------+-------------|'
        expected_output += '\n|  123 | Ansible | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_get_with_config(self):
        lifecycle_driver_id = '123'
        self.lm_sim.add_lifecycle_driver({'id': lifecycle_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(lifecycledriver_cmds.get, ['TestEnv', lifecycle_driver_id, '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_output = '|   id | type    | baseUri     |'
        expected_output += '\n|------+---------+-------------|'
        expected_output += '\n|  123 | Ansible | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_get_with_pwd(self):
        lifecycle_driver_id = '123'
        self.lm_sim.add_lifecycle_driver({'id': lifecycle_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(lifecycledriver_cmds.get, ['TestEnv', lifecycle_driver_id, '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_output = '|   id | type    | baseUri     |'
        expected_output += '\n|------+---------+-------------|'
        expected_output += '\n|  123 | Ansible | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_get_handles_lm_driver_error(self):
        result = self.runner.invoke(lifecycledriver_cmds.get, ['TestEnv', '987'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occured: No lifecycle driver with id 987'
        self.assert_output(result, expected_output)

    def test_delete_by_type(self):
        lifecycle_driver_id = '123'
        self.lm_sim.add_lifecycle_driver({'id': lifecycle_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(lifecycledriver_cmds.get, ['TestEnv', '--type', 'Ansible'])
        self.assert_no_errors(result)
        expected_output = '|   id | type    | baseUri     |'
        expected_output += '\n|------+---------+-------------|'
        expected_output += '\n|  123 | Ansible | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
    
    def test_get_by_type_not_found(self):
        result = self.runner.invoke(lifecycledriver_cmds.get, ['TestEnv', '--type', 'Ansible'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occured: No lifecycle driver with type Ansible'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
    
    def test_get_without_id_or_type_fails(self):
        result = self.runner.invoke(lifecycledriver_cmds.get, ['TestEnv'])
        self.assert_has_system_exit(result)
        expected_output = 'Error: Must specify driver-id argument or type option'
        self.assert_output(result, expected_output)
    
    def test_get_with_output_json_format(self):
        lifecycle_driver_id = '123'
        self.lm_sim.add_lifecycle_driver({'id': lifecycle_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(lifecycledriver_cmds.get, ['TestEnv', lifecycle_driver_id, '-f', 'json'])
        self.assert_no_errors(result)
        expected_output = '{'
        expected_output += '\n  \"id\": \"123\",'
        expected_output += '\n  \"type\": \"Ansible\",'
        expected_output += '\n  \"baseUri\": \"example.com\"'
        expected_output += '\n}'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_get_with_output_yaml_format(self):
        lifecycle_driver_id = '123'
        self.lm_sim.add_lifecycle_driver({'id': lifecycle_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(lifecycledriver_cmds.get, ['TestEnv', lifecycle_driver_id, '-f', 'yaml'])
        self.assert_no_errors(result)
        expected_output = 'baseUri: example.com'
        expected_output += '\nid: \'123\''
        expected_output += '\ntype: Ansible\n'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)