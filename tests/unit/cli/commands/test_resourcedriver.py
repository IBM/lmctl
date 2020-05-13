import os
import tests.unit.cli.commands.command_testing as command_testing
import lmctl.drivers.lm.base as lm_drivers
import lmctl.cli.commands.resourcedriver as resourcedriver_cmds
from unittest.mock import patch
from tests.common.simulations.lm_simulator import LmSimulator

class TestResourceDriverCommands(command_testing.CommandTestCase):

    def setUp(self):
        super().setUp()
        # Created simulated LM session when requested
        self.lm_sim = LmSimulator().start()
        create_lm_session_patcher = patch('lmctl.cli.ctlmgmt.create_lm_session')
        self.mock_create_lm_session = create_lm_session_patcher.start()
        self.mock_create_lm_session.return_value = self.lm_sim.as_mocked_session()
        self.addCleanup(create_lm_session_patcher.stop)

    def test_add_with_defaults(self):
        result = self.runner.invoke(resourcedriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com'])
        self.assert_no_errors(result)
        expected_id = None
        for resource_driver_id, resource_driver in self.lm_sim.resource_drivers.items():
            expected_id = resource_driver_id
        expected_output = '| id                                   | type    | baseUri                       |'
        expected_output += '\n|--------------------------------------+---------+-------------------------------|'
        expected_output += '\n| {0} | Ansible | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_resource_mgmt_driver = self.mock_create_lm_session.return_value.resource_driver_mgmt_driver
        mock_resource_mgmt_driver.add_resource_driver.assert_called_once_with({'baseUri': 'http://mockdriver.example.com', 'type': 'Ansible'})

    def test_add_with_type(self):
        result = self.runner.invoke(resourcedriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--type', 'Shell'])
        self.assert_no_errors(result)
        expected_id = None
        for resource_driver_id, resource_driver in self.lm_sim.resource_drivers.items():
            expected_id = resource_driver_id
        expected_output = '| id                                   | type   | baseUri                       |'
        expected_output += '\n|--------------------------------------+--------+-------------------------------|'
        expected_output += '\n| {0} | Shell  | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_resource_mgmt_driver = self.mock_create_lm_session.return_value.resource_driver_mgmt_driver
        mock_resource_mgmt_driver.add_resource_driver.assert_called_once_with({'baseUri': 'http://mockdriver.example.com', 'type': 'Shell'})

    def test_add_with_config(self):
        result = self.runner.invoke(resourcedriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_id = None
        for resource_driver_id, resource_driver in self.lm_sim.resource_drivers.items():
            expected_id = resource_driver_id
        expected_output = '| id                                   | type    | baseUri                       |'
        expected_output += '\n|--------------------------------------+---------+-------------------------------|'
        expected_output += '\n| {0} | Ansible | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_add_with_pwd(self):
        result = self.runner.invoke(resourcedriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_id = None
        for resource_driver_id, resource_driver in self.lm_sim.resource_drivers.items():
            expected_id = resource_driver_id
        expected_output = '| id                                   | type    | baseUri                       |'
        expected_output += '\n|--------------------------------------+---------+-------------------------------|'
        expected_output += '\n| {0} | Ansible | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_add_with_certificate(self):
        certificate_pem_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'resources', 'certificate.pem')

        result = self.runner.invoke(resourcedriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--pwd', 'secret', '--certificate', certificate_pem_file])
        self.assert_no_errors(result)
        expected_id = None
        for resource_driver_id, resource_driver in self.lm_sim.resource_drivers.items():
            expected_id = resource_driver_id
        expected_output = '| id                                   | type    | baseUri                       |'
        expected_output += '\n|--------------------------------------+---------+-------------------------------|'
        expected_output += '\n| {0} | Ansible | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_add_with_missing_certificate(self):
        certificate_pem_file = 'certificate.pem'

        result = self.runner.invoke(resourcedriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--pwd', 'secret', '--certificate', certificate_pem_file])
        self.assert_has_system_exit(result)
        self.assert_output(result, "Error: reading certificate: [Errno 2] No such file or directory: 'certificate.pem'")

    def test_add_with_output_json_format(self):
        result = self.runner.invoke(resourcedriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '-f', 'json'])
        self.assert_no_errors(result)
        expected_id = None
        for resource_driver_id, resource_driver in self.lm_sim.resource_drivers.items():
            expected_id = resource_driver_id
        expected_output = '{'
        expected_output += '\n  \"type\": \"Ansible\",'
        expected_output += '\n  \"baseUri\": \"http://mockdriver.example.com\",'
        expected_output += '\n  \"id\": \"{0}\"'.format(expected_id)
        expected_output += '\n}'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_add_with_output_yaml_format(self):
        result = self.runner.invoke(resourcedriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '-f', 'yaml'])
        self.assert_no_errors(result)
        expected_id = None
        for resource_driver_id, resource_driver in self.lm_sim.resource_drivers.items():
            expected_id = resource_driver_id
        expected_output = 'type: Ansible'
        expected_output += '\nbaseUri: http://mockdriver.example.com'
        expected_output += '\nid: {0}\n'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_add_handles_lm_driver_error(self):
        self.mock_create_lm_session.return_value.resource_driver_mgmt_driver.add_resource_driver.side_effect = lm_drivers.LmDriverException('Mocked error')
        result = self.runner.invoke(resourcedriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occurred: Mocked error'
        self.assert_output(result, expected_output)
        
    def test_delete_with_defaults(self):
        resource_driver_id = '123'
        self.lm_sim.add_resource_driver({'id': resource_driver_id})
        result = self.runner.invoke(resourcedriver_cmds.delete, ['TestEnv', resource_driver_id])
        self.assert_no_errors(result)
        expected_output = 'Deleting resource driver: {0}...'.format(resource_driver_id)
        expected_output += '\nDeleted resource driver: {0}'.format(resource_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_resource_mgmt_driver = self.mock_create_lm_session.return_value.resource_driver_mgmt_driver
        mock_resource_mgmt_driver.delete_resource_driver.assert_called_once_with(resource_driver_id)

    def test_delete_with_config(self):
        resource_driver_id = '123'
        self.lm_sim.add_resource_driver({'id': resource_driver_id})
        result = self.runner.invoke(resourcedriver_cmds.delete, ['TestEnv', resource_driver_id, '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_output = 'Deleting resource driver: {0}...'.format(resource_driver_id)
        expected_output += '\nDeleted resource driver: {0}'.format(resource_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_delete_with_pwd(self):
        resource_driver_id = '123'
        self.lm_sim.add_resource_driver({'id': resource_driver_id})
        result = self.runner.invoke(resourcedriver_cmds.delete, ['TestEnv', resource_driver_id, '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_output = 'Deleting resource driver: {0}...'.format(resource_driver_id)
        expected_output += '\nDeleted resource driver: {0}'.format(resource_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_delete_handles_lm_driver_error(self):
        result = self.runner.invoke(resourcedriver_cmds.delete, ['TestEnv', '987'])
        self.assert_has_system_exit(result)
        expected_output = 'Deleting resource driver: 987...'
        expected_output += '\nLM error occurred: No resource driver with id 987'
        self.assert_output(result, expected_output)

    def test_delete_by_type(self):
        resource_driver_id = '123'
        self.lm_sim.add_resource_driver({'id': resource_driver_id, 'type': 'Ansible'})
        result = self.runner.invoke(resourcedriver_cmds.delete, ['TestEnv', '--type', 'Ansible'])
        self.assert_no_errors(result)
        expected_output = 'Found resource driver matching type \'Ansible\'. Id: 123'
        expected_output += '\nDeleting resource driver: {0}...'.format(resource_driver_id)
        expected_output += '\nDeleted resource driver: {0}'.format(resource_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_resource_mgmt_driver = self.mock_create_lm_session.return_value.resource_driver_mgmt_driver
        mock_resource_mgmt_driver.get_resource_driver_by_type.assert_called_once_with('Ansible')
        mock_resource_mgmt_driver.delete_resource_driver.assert_called_once_with(resource_driver_id)

    def test_delete_by_type_not_found(self):
        result = self.runner.invoke(resourcedriver_cmds.delete, ['TestEnv', '--type', 'Ansible'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occurred: No resource driver with type Ansible'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
    
    def test_delete_without_id_or_type_fails(self):
        result = self.runner.invoke(resourcedriver_cmds.delete, ['TestEnv'])
        self.assert_has_system_exit(result)
        expected_output = 'Error: Must specify driver-id argument or type option'
        self.assert_output(result, expected_output)
        
    def test_get_with_defaults(self):
        resource_driver_id = '123'
        self.lm_sim.add_resource_driver({'id': resource_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(resourcedriver_cmds.get, ['TestEnv', resource_driver_id])
        self.assert_no_errors(result)
        expected_output = '|   id | type    | baseUri     |'
        expected_output += '\n|------+---------+-------------|'
        expected_output += '\n|  123 | Ansible | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_resource_mgmt_driver = self.mock_create_lm_session.return_value.resource_driver_mgmt_driver
        mock_resource_mgmt_driver.get_resource_driver.assert_called_once_with(resource_driver_id)

    def test_get_with_config(self):
        resource_driver_id = '123'
        self.lm_sim.add_resource_driver({'id': resource_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(resourcedriver_cmds.get, ['TestEnv', resource_driver_id, '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_output = '|   id | type    | baseUri     |'
        expected_output += '\n|------+---------+-------------|'
        expected_output += '\n|  123 | Ansible | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_get_with_pwd(self):
        resource_driver_id = '123'
        self.lm_sim.add_resource_driver({'id': resource_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(resourcedriver_cmds.get, ['TestEnv', resource_driver_id, '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_output = '|   id | type    | baseUri     |'
        expected_output += '\n|------+---------+-------------|'
        expected_output += '\n|  123 | Ansible | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_get_handles_lm_driver_error(self):
        result = self.runner.invoke(resourcedriver_cmds.get, ['TestEnv', '987'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occurred: No resource driver with id 987'
        self.assert_output(result, expected_output)

    def test_get_by_type(self):
        resource_driver_id = '123'
        self.lm_sim.add_resource_driver({'id': resource_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(resourcedriver_cmds.get, ['TestEnv', '--type', 'Ansible'])
        self.assert_no_errors(result)
        expected_output = '|   id | type    | baseUri     |'
        expected_output += '\n|------+---------+-------------|'
        expected_output += '\n|  123 | Ansible | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_resource_mgmt_driver = self.mock_create_lm_session.return_value.resource_driver_mgmt_driver
        mock_resource_mgmt_driver.get_resource_driver_by_type.assert_called_once_with('Ansible')

    def test_get_by_type_not_found(self):
        result = self.runner.invoke(resourcedriver_cmds.get, ['TestEnv', '--type', 'Ansible'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occurred: No resource driver with type Ansible'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
    
    def test_get_without_id_or_type_fails(self):
        result = self.runner.invoke(resourcedriver_cmds.get, ['TestEnv'])
        self.assert_has_system_exit(result)
        expected_output = 'Error: Must specify driver-id argument or type option'
        self.assert_output(result, expected_output)
    
    def test_get_with_output_json_format(self):
        resource_driver_id = '123'
        self.lm_sim.add_resource_driver({'id': resource_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(resourcedriver_cmds.get, ['TestEnv', resource_driver_id, '-f', 'json'])
        self.assert_no_errors(result)
        expected_output = '{'
        expected_output += '\n  \"id\": \"123\",'
        expected_output += '\n  \"type\": \"Ansible\",'
        expected_output += '\n  \"baseUri\": \"example.com\"'
        expected_output += '\n}'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_get_with_output_yaml_format(self):
        resource_driver_id = '123'
        self.lm_sim.add_resource_driver({'id': resource_driver_id, 'type': 'Ansible', 'baseUri': 'example.com'})
        result = self.runner.invoke(resourcedriver_cmds.get, ['TestEnv', resource_driver_id, '-f', 'yaml'])
        self.assert_no_errors(result)
        expected_output = 'id: \'123\''
        expected_output += '\ntype: Ansible'
        expected_output += '\nbaseUri: example.com\n'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)