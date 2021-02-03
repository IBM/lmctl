from .cli_test_base import CLIIntegrationTest
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat
from lmctl.cli.commands.targets.env import EnvironmentTable, PingTable
from lmctl.cli.controller import get_global_controller
from lmctl.client import TestResults, TestResult, TNCOClientError
from unittest.mock import patch
import yaml
import json
import unittest

class TestEnvironments(CLIIntegrationTest):

    def test_get_all_as_yaml(self):
        result = self.cli_runner.invoke(cli, 
            ['get', 'env', '-o', 'yaml']
        )
        loaded_output = yaml.safe_load(result.output)
        self.assertIn('default', loaded_output)
        self.assertIn('tnco', loaded_output['default'])
        
    def test_get_all_as_json(self):
        result = self.cli_runner.invoke(cli, 
            ['get', 'env', '-o', 'json']
        )
        loaded_output = json.loads(result.output)
        self.assertIn('default', loaded_output)
        self.assertIn('lm', loaded_output['default'])
    
    def test_get_all_as_table(self):
        result = self.cli_runner.invoke(cli, 
            ['get', 'env']
        )
        table_format = TableFormat(table=EnvironmentTable())
        ctl = get_global_controller()
        expected_output = table_format.convert_list(ctl.config.environments.values())
        self.assert_output(result, expected_output)

    def test_get_by_name_as_yaml(self):
        result = self.cli_runner.invoke(cli, 
            ['get', 'env', 'default', '-o', 'yaml']
        )
        loaded_output = yaml.safe_load(result.output)
        self.assertIn('tnco', loaded_output)
        
    def test_get_all_as_json(self):
        result = self.cli_runner.invoke(cli, 
            ['get', 'env', 'default', '-o', 'json']
        )
        loaded_output = json.loads(result.output)
        self.assertIn('tnco', loaded_output)
        
    def test_get_all_as_table(self):
        result = self.cli_runner.invoke(cli, 
            ['get', 'env', 'default']
        )
        table_format = TableFormat(table=EnvironmentTable())
        ctl = get_global_controller()
        expected_output = table_format.convert_element(ctl.config.environments.get('default', None))
        self.assert_output(result, expected_output)

    def test_ping(self):
        result = self.cli_runner.invoke(cli, 
            ['ping', 'env', 'default']
        )
        self.assert_no_errors(result)
        ctl = get_global_controller()
        expected_results = TestResults(tests=[
            TestResult('Descriptors', error=None),
            TestResult('Topology', error=None),
            TestResult('Behaviour', error=None),
            TestResult('Resource Manager', error=None)
        ])
        table_format = TableFormat(table=PingTable())
        address = ctl.config.environments.get('default').tnco.address
        expected_output = f'Pinging TNCO (ALM): {address}'
        expected_output += '\n'
        expected_output += table_format.convert_list(expected_results.tests)
        expected_output += '\nTNCO (ALM) tests passed! ✅'
        self.assert_output(result, expected_output)
    
    @patch('lmctl.client.client.DescriptorsAPI')
    def test_ping_with_failure(self, mock_descriptors_api):
        mock_error = TNCOClientError('Mock error')
        mock_descriptors_api.return_value.all.side_effect = mock_error
        result = self.cli_runner.invoke(cli, 
            ['ping', 'env', 'default']
        )
        self.assert_has_system_exit(result)
        ctl = get_global_controller()
        expected_results = TestResults(tests=[
            TestResult('Descriptors', error='Mock error'),
            TestResult('Topology', error=None),
            TestResult('Behaviour', error=None),
            TestResult('Resource Manager', error=None)
        ])
        table_format = TableFormat(table=PingTable())
        address = ctl.config.environments.get('default').tnco.address
        expected_output = f'Pinging TNCO (ALM): {address}'
        expected_output += '\n'
        expected_output += table_format.convert_list(expected_results.tests)
        expected_output += '\nTNCO (ALM) tests failed! ❌'
        self.assert_output(result, expected_output)

    @unittest.skip('Templates not GA')
    def test_ping_include_template_engine(self):
        result = self.cli_runner.invoke(cli, 
            ['ping', 'env', 'default', '--include-template-engine']
        )
        self.assert_no_errors(result)
        ctl = get_global_controller()
        expected_results = TestResults(tests=[
            TestResult('Descriptors', error=None),
            TestResult('Topology', error=None),
            TestResult('Behaviour', error=None),
            TestResult('Resource Manager', error=None),
            TestResult('Template Engine', error=None)
        ])
        table_format = TableFormat(table=PingTable())
        address = ctl.config.environments.get('default').tnco.address
        expected_output = f'Pinging TNCO (ALM): {address}'
        expected_output += '\n'
        expected_output += table_format.convert_list(expected_results.tests)
        expected_output += '\nTNCO (ALM) tests passed! ✅'
        self.assert_output(result, expected_output)