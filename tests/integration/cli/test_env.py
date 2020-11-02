from .cli_test_base import CLIIntegrationTest
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat
from lmctl.cli.commands.targets.env import EnvironmentTable
from lmctl.cli.controller import get_global_controller
import yaml
import json

class TestEnvironments(CLIIntegrationTest):

    def test_get_all_as_yaml(self):
        result = self.cli_runner.invoke(cli, 
            ['get', 'env', '-o', 'yaml']
        )
        loaded_output = yaml.safe_load(result.output)
        self.assertIn('default', loaded_output)
        self.assertIn('lm', loaded_output['default'])
        
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
        self.assertIn('lm', loaded_output)
        
    def test_get_all_as_json(self):
        result = self.cli_runner.invoke(cli, 
            ['get', 'env', 'default', '-o', 'json']
        )
        loaded_output = json.loads(result.output)
        self.assertIn('lm', loaded_output)
        
    def test_get_all_as_table(self):
        result = self.cli_runner.invoke(cli, 
            ['get', 'env', 'default']
        )
        table_format = TableFormat(table=EnvironmentTable())
        ctl = get_global_controller()
        expected_output = table_format.convert_element(ctl.config.environments.get('default', None))
        self.assert_output(result, expected_output)