import os
import tests.unit.cli.commands.command_testing as command_testing
import lmctl.drivers.lm.base as lm_drivers
import lmctl.cli.commands.vimdriver as vimdriver_cmds
from unittest.mock import patch
from tests.common.simulations.lm_simulator import LmSimulator

class TestVimDriverCommands(command_testing.CommandTestCase):

    def setUp(self):
        super().setUp()
        # Created simulated LM session when requested
        self.lm_sim = LmSimulator().start()
        create_lm_session_patcher = patch('lmctl.cli.ctlmgmt.create_lm_session')
        self.mock_create_lm_session = create_lm_session_patcher.start()
        self.mock_create_lm_session.return_value = self.lm_sim.as_mocked_session()
        self.addCleanup(create_lm_session_patcher.stop)

    def test_add_with_defaults(self):
        result = self.runner.invoke(vimdriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com'])
        self.assert_no_errors(result)
        expected_id = None
        for vim_id, vim_driver in self.lm_sim.vim_drivers.items():
            expected_id = vim_id
        expected_output = '| id                                   | infrastructureType   | baseUri                       |'
        expected_output += '\n|--------------------------------------+----------------------+-------------------------------|'
        expected_output += '\n| {0} | Openstack            | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_vim_mgmt_driver = self.mock_create_lm_session.return_value.vim_driver_mgmt_driver
        mock_vim_mgmt_driver.add_vim_driver.assert_called_once_with({'baseUri': 'http://mockdriver.example.com', 'infrastructureType': 'Openstack'})

    def test_add_with_type(self):
        result = self.runner.invoke(vimdriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--type', 'Kubernetes'])
        self.assert_no_errors(result)
        expected_id = None
        for vim_id, vim_driver in self.lm_sim.vim_drivers.items():
            expected_id = vim_id
        expected_output = '| id                                   | infrastructureType   | baseUri                       |'
        expected_output += '\n|--------------------------------------+----------------------+-------------------------------|'
        expected_output += '\n| {0} | Kubernetes           | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_vim_mgmt_driver = self.mock_create_lm_session.return_value.vim_driver_mgmt_driver
        mock_vim_mgmt_driver.add_vim_driver.assert_called_once_with({'baseUri': 'http://mockdriver.example.com', 'infrastructureType': 'Kubernetes'})

    def test_add_with_certificate(self):
        certificate_pem_file = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, os.pardir, 'resources', 'certificate.pem')

        result = self.runner.invoke(vimdriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--type', 'Kubernetes', '--certificate', certificate_pem_file])
        self.assert_no_errors(result)
        expected_id = None
        for vim_id, vim_driver in self.lm_sim.vim_drivers.items():
            expected_id = vim_id
        expected_output = '| id                                   | infrastructureType   | baseUri                       |'
        expected_output += '\n|--------------------------------------+----------------------+-------------------------------|'
        expected_output += '\n| {0} | Kubernetes           | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_vim_mgmt_driver = self.mock_create_lm_session.return_value.vim_driver_mgmt_driver
        mock_vim_mgmt_driver.add_vim_driver.assert_called_once_with({'baseUri': 'http://mockdriver.example.com', 'infrastructureType': 'Kubernetes', 'certificate': '-----BEGIN CERTIFICATE-----\\nMIIDDzCCAfegAwIBAgIQXgj9XfKMhQRCDLhG4/BGSDANBgkqhkiG9w0BAQsFADAj\\nMSEwHwYDVQQDExhhbnNpYmxlLWxpZmVjeWNsZS1kcml2ZXIwHhcNMjAwMTE1MDcz\\nMzQzWhcNMzAwMTEyMDczMzQzWjAjMSEwHwYDVQQDExhhbnNpYmxlLWxpZmVjeWNs\\nZS1kcml2ZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDAk6+0/uLm\\n2H8KQmApSgWGtehVUIyq2iIDxfQrRkF3HiS/9UzMKVdLaafX+vPvkJniLDs162Ch\\ngkO8JKejmwopO2pzYUFS/yhnCS8Ys+BMjYfX+5Wpuq/mBVQODuBVJV3n/evheuj1\\nr8t97kPbgNTQxygSAI/C/QdzbuC6GG4cw9seiM/1kVEqb1D9z53DvVftq6yJELDj\\nbItJiY57reDfUj3raUh7GfNt68d1DSRBMYGmyu0o7uHVEL5PCeqRJpOmiL7DyoH6\\nTYg7QEjEFdao4X3ohWdw9rxxO4PKw5g5zL5yjFqygBH0XkZ/9TVefpcAn5d/uaTY\\n4bv36qT3BF6LAgMBAAGjPzA9MA4GA1UdDwEB/wQEAwIFoDAdBgNVHSUEFjAUBggr\\nBgEFBQcDAQYIKwYBBQUHAwIwDAYDVR0TAQH/BAIwADANBgkqhkiG9w0BAQsFAAOC\\nAQEAhzczPnzCCWCXg8O5K6CmIqXPyOrNEobegTifjdGdGBayFYFfp2ybLJX+XK8O\\nJiuoOqY/ti0ZkBFiV7JbfmUl4uRTEqBdax5sU0UlR6YxyRbiSM152uPUjYQwZkMM\\nfSqPjcvIoLCcznHe0z7ECgfJPjgti9YZlnhBTGW3WDelhXgQyU94A+c7NLBn2cK5\\nVfcvyunmSiAUVzSjmjpGBZ/xX2I4JjmteLrr8WsxSllg8DAo0AI+7jeecty3BG4q\\ne4p06LPHR/j8yBaHyMHweAolrn01cZXP7h5aRiE3xPRBK/Rccr6xYDTgqBLdwhfX\\nkF8OyMZPlY0Jf7/zbjbHi/D93A==\\n-----END CERTIFICATE-----'})

    def test_add_with_missing_certificate(self):
        certificate_pem_file = 'certificate.pem'

        result = self.runner.invoke(vimdriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--type', 'Kubernetes', '--certificate', certificate_pem_file])
        self.assert_has_system_exit(result)
        self.assert_output(result, "Error: reading certificate: [Errno 2] No such file or directory: 'certificate.pem'")

    def test_add_with_config(self):
        result = self.runner.invoke(vimdriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_id = None
        for vim_id, vim_driver in self.lm_sim.vim_drivers.items():
            expected_id = vim_id
        expected_output = '| id                                   | infrastructureType   | baseUri                       |'
        expected_output += '\n|--------------------------------------+----------------------+-------------------------------|'
        expected_output += '\n| {0} | Openstack            | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_add_with_pwd(self):
        result = self.runner.invoke(vimdriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_id = None
        for vim_id, vim_driver in self.lm_sim.vim_drivers.items():
            expected_id = vim_id
        expected_output = '| id                                   | infrastructureType   | baseUri                       |'
        expected_output += '\n|--------------------------------------+----------------------+-------------------------------|'
        expected_output += '\n| {0} | Openstack            | http://mockdriver.example.com |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_add_with_output_json_format(self):
        result = self.runner.invoke(vimdriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '-f', 'json'])
        self.assert_no_errors(result)
        expected_id = None
        for vim_id, vim_driver in self.lm_sim.vim_drivers.items():
            expected_id = vim_id
        expected_output = '{'
        expected_output += '\n  \"infrastructureType\": \"Openstack\",'
        expected_output += '\n  \"baseUri\": \"http://mockdriver.example.com\",'
        expected_output += '\n  \"id\": \"{0}\"'.format(expected_id)
        expected_output += '\n}'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_add_with_output_yaml_format(self):
        result = self.runner.invoke(vimdriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com', '-f', 'yaml'])
        self.assert_no_errors(result)
        expected_id = None
        for vim_id, vim_driver in self.lm_sim.vim_drivers.items():
            expected_id = vim_id
        expected_output = 'infrastructureType: Openstack'
        expected_output += '\nbaseUri: http://mockdriver.example.com'
        expected_output += '\nid: {0}\n'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_add_handles_lm_driver_error(self):
        self.mock_create_lm_session.return_value.vim_driver_mgmt_driver.add_vim_driver.side_effect = lm_drivers.LmDriverException('Mocked error')
        result = self.runner.invoke(vimdriver_cmds.add, ['TestEnv', '--url', 'http://mockdriver.example.com'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occurred: Mocked error'
        self.assert_output(result, expected_output)
        
    def test_delete_with_defaults(self):
        vim_driver_id = '123'
        self.lm_sim.add_vim_driver({'id': vim_driver_id})
        result = self.runner.invoke(vimdriver_cmds.delete, ['TestEnv', vim_driver_id])
        self.assert_no_errors(result)
        expected_output = 'Deleting VIM driver: {0}...'.format(vim_driver_id)
        expected_output += '\nDeleted VIM driver: {0}'.format(vim_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_vim_mgmt_driver = self.mock_create_lm_session.return_value.vim_driver_mgmt_driver
        mock_vim_mgmt_driver.delete_vim_driver.assert_called_once_with(vim_driver_id)
        
    def test_delete_with_config(self):
        vim_driver_id = '123'
        self.lm_sim.add_vim_driver({'id': vim_driver_id})
        result = self.runner.invoke(vimdriver_cmds.delete, ['TestEnv', vim_driver_id, '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_output = 'Deleting VIM driver: {0}...'.format(vim_driver_id)
        expected_output += '\nDeleted VIM driver: {0}'.format(vim_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_delete_with_pwd(self):
        vim_driver_id = '123'
        self.lm_sim.add_vim_driver({'id': vim_driver_id})
        result = self.runner.invoke(vimdriver_cmds.delete, ['TestEnv', vim_driver_id, '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_output = 'Deleting VIM driver: {0}...'.format(vim_driver_id)
        expected_output += '\nDeleted VIM driver: {0}'.format(vim_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_delete_handles_lm_driver_error(self):
        result = self.runner.invoke(vimdriver_cmds.delete, ['TestEnv', '987'])
        self.assert_has_system_exit(result)
        expected_output = 'Deleting VIM driver: 987...'
        expected_output += '\nLM error occurred: No VIM driver with id 987'
        self.assert_output(result, expected_output)

    def test_delete_by_type(self):
        vim_driver_id = '123'
        self.lm_sim.add_vim_driver({'id': vim_driver_id, 'infrastructureType': 'Openstack'})
        result = self.runner.invoke(vimdriver_cmds.delete, ['TestEnv', '--type', 'Openstack'])
        self.assert_no_errors(result)
        expected_output = 'Found VIM driver matching type \'Openstack\'. Id: 123'
        expected_output += '\nDeleting VIM driver: {0}...'.format(vim_driver_id)
        expected_output += '\nDeleted VIM driver: {0}'.format(vim_driver_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_vim_mgmt_driver = self.mock_create_lm_session.return_value.vim_driver_mgmt_driver
        mock_vim_mgmt_driver.get_vim_driver_by_type.assert_called_once_with('Openstack')
        mock_vim_mgmt_driver.delete_vim_driver.assert_called_once_with(vim_driver_id)
        
    def test_delete_by_type_not_found(self):
        result = self.runner.invoke(vimdriver_cmds.delete, ['TestEnv', '--type', 'Openstack'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occurred: No VIM driver with infrastructure type Openstack'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
    
    def test_delete_without_id_or_type_fails(self):
        result = self.runner.invoke(vimdriver_cmds.delete, ['TestEnv'])
        self.assert_has_system_exit(result)
        expected_output = 'Error: Must specify driver-id argument or type option'
        self.assert_output(result, expected_output)
        
    def test_get_with_defaults(self):
        vim_driver_id = '123'
        self.lm_sim.add_vim_driver({'id': vim_driver_id, 'infrastructureType': 'Openstack', 'baseUri': 'example.com'})
        result = self.runner.invoke(vimdriver_cmds.get, ['TestEnv', vim_driver_id])
        self.assert_no_errors(result)
        expected_output = '|   id | infrastructureType   | baseUri     |'
        expected_output += '\n|------+----------------------+-------------|'
        expected_output += '\n|  123 | Openstack            | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_vim_mgmt_driver = self.mock_create_lm_session.return_value.vim_driver_mgmt_driver
        mock_vim_mgmt_driver.get_vim_driver.assert_called_once_with(vim_driver_id)
        
    def test_get_with_config(self):
        vim_driver_id = '123'
        self.lm_sim.add_vim_driver({'id': vim_driver_id, 'infrastructureType': 'Openstack', 'baseUri': 'example.com'})
        result = self.runner.invoke(vimdriver_cmds.get, ['TestEnv', vim_driver_id, '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_output = '|   id | infrastructureType   | baseUri     |'
        expected_output += '\n|------+----------------------+-------------|'
        expected_output += '\n|  123 | Openstack            | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_get_with_pwd(self):
        vim_driver_id = '123'
        self.lm_sim.add_vim_driver({'id': vim_driver_id, 'infrastructureType': 'Openstack', 'baseUri': 'example.com'})
        result = self.runner.invoke(vimdriver_cmds.get, ['TestEnv', vim_driver_id, '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_output = '|   id | infrastructureType   | baseUri     |'
        expected_output += '\n|------+----------------------+-------------|'
        expected_output += '\n|  123 | Openstack            | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_get_handles_lm_driver_error(self):
        result = self.runner.invoke(vimdriver_cmds.get, ['TestEnv', '987'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occurred: No VIM driver with id 987'
        self.assert_output(result, expected_output)

    def test_get_by_type(self):
        vim_driver_id = '123'
        self.lm_sim.add_vim_driver({'id': vim_driver_id, 'infrastructureType': 'Openstack', 'baseUri': 'example.com'})
        result = self.runner.invoke(vimdriver_cmds.get, ['TestEnv', '--type', 'Openstack'])
        self.assert_no_errors(result)
        expected_output = '|   id | infrastructureType   | baseUri     |'
        expected_output += '\n|------+----------------------+-------------|'
        expected_output += '\n|  123 | Openstack            | example.com |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_vim_mgmt_driver = self.mock_create_lm_session.return_value.vim_driver_mgmt_driver
        mock_vim_mgmt_driver.get_vim_driver_by_type.assert_called_once_with('Openstack')
        
    def test_get_by_type_not_found(self):
        result = self.runner.invoke(vimdriver_cmds.get, ['TestEnv', '--type', 'Openstack'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occurred: No VIM driver with infrastructure type Openstack'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
    
    def test_get_without_id_or_type_fails(self):
        result = self.runner.invoke(vimdriver_cmds.get, ['TestEnv'])
        self.assert_has_system_exit(result)
        expected_output = 'Error: Must specify driver-id argument or type option'
        self.assert_output(result, expected_output)
    
    def test_get_with_output_json_format(self):
        vim_driver_id = '123'
        self.lm_sim.add_vim_driver({'id': vim_driver_id, 'infrastructureType': 'Openstack', 'baseUri': 'example.com'})
        result = self.runner.invoke(vimdriver_cmds.get, ['TestEnv', vim_driver_id, '-f', 'json'])
        self.assert_no_errors(result)
        expected_output = '{'
        expected_output += '\n  \"id\": \"123\",'
        expected_output += '\n  \"infrastructureType\": \"Openstack\",'
        expected_output += '\n  \"baseUri\": \"example.com\"'
        expected_output += '\n}'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_get_with_output_yaml_format(self):
        vim_driver_id = '123'
        self.lm_sim.add_vim_driver({'id': vim_driver_id, 'infrastructureType': 'Openstack', 'baseUri': 'example.com'})
        result = self.runner.invoke(vimdriver_cmds.get, ['TestEnv', vim_driver_id, '-f', 'yaml'])
        self.assert_no_errors(result)
        expected_output = 'id: \'123\''
        expected_output += '\ninfrastructureType: Openstack'
        expected_output += '\nbaseUri: example.com\n'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)