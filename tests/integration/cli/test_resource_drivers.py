from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat, Table
from lmctl.client import TNCOClientHttpError
from lmctl.cli.commands.resourcedriver import default_columns
import yaml
import json
import time

class TestResourceDrivers(CLIIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        cls.test_case_props['driver_A'] = tester.default_client.resource_drivers.create({
            'type': 'vCloud',
            'baseUri': 'http://ansible-lifecycle-driver:8292'
        })
        cls.test_case_props['driver_B'] = tester.default_client.resource_drivers.create({
            'type': 'Other',
            'baseUri': 'http://ansible-lifecycle-driver:8292'
        })
        
    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.resource_drivers.delete(cls.test_case_props['driver_A']['id'])
        tester.default_client.resource_drivers.delete(cls.test_case_props['driver_B']['id'])

    def test_get_by_id_as_yaml(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'resourcedriver', self.test_case_props['driver_A']['id'], '-e', 'default', '-o', 'yaml'
            ])
        loaded_output = yaml.safe_load(result.output)
        self.assertEqual(loaded_output['id'], self.test_case_props['driver_A']['id'])
        self.assertEqual(loaded_output['type'], self.test_case_props['driver_A']['type'])
        self.assertEqual(loaded_output['baseUri'], self.test_case_props['driver_A']['baseUri'])
    
    def test_get_by_id_as_json(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'resourcedriver', self.test_case_props['driver_A']['id'], '-e', 'default', '-o', 'json'
            ])
        loaded_output = json.loads(result.output)
        self.assertEqual(loaded_output['id'], self.test_case_props['driver_A']['id'])
        self.assertEqual(loaded_output['type'], self.test_case_props['driver_A']['type'])
        self.assertEqual(loaded_output['baseUri'], self.test_case_props['driver_A']['baseUri'])
    
    def test_get_by_id_as_table(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'resourcedriver', self.test_case_props['driver_A']['id'], '-e', 'default'
            ])
        table_format = TableFormat(table=Table(columns=default_columns))
        expected_output = table_format.convert_element(self.test_case_props['driver_A'])
        self.assert_output(result, expected_output)

    def test_get_by_type(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'resourcedriver', '-e', 'default', '--type', self.test_case_props['driver_B']['type']
            ])
        table_format = TableFormat(table=Table(columns=default_columns))
        expected_output = table_format.convert_element(self.test_case_props['driver_B'])
        self.assert_output(result, expected_output)

    def test_get_without_id_or_type_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'resourcedriver', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get resourcedriver [OPTIONS] [ID]'
        expected_output += '\nTry \'cli get resourcedriver --help\' for help.'
        expected_output += '\n\nError: Must identify the target by specifying one parameter from ["id", "--type"] or by including one of the following attributes ["id", "infrastructureType"] in the given object/file'
        self.assert_output(result, expected_output)
    
    def test_create_with_yaml_file(self):
        yml_file = self.tester.create_yaml_file('resource-driver-cmd-create-with.yaml', {
            'type': 'GCE',
            'baseUri': 'http://ansible-lifecycle-driver:8292'
        })
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcedriver', '-e', 'default', '-f', yml_file
            ])
        self.assertTrue(create_result.output.startswith('Created: '))
        driver_id = create_result.output[len('Created: ')-1:].strip()
        api_get_result = self.tester.default_client.resource_drivers.get(driver_id)
        self.assertEqual(api_get_result['id'], driver_id)
        self.assertEqual(api_get_result['type'], 'GCE')
        self.assertEqual(api_get_result['baseUri'], 'http://ansible-lifecycle-driver:8292')
        self.tester.default_client.resource_drivers.delete(driver_id)
    
    def test_create_with_json_file(self):
        json_file = self.tester.create_json_file('resource-driver-cmd-create-with.json', {
            'type': 'GCE',
            'baseUri': 'http://ansible-lifecycle-driver:8292'
        })
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcedriver', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        driver_id = create_result.output[len('Created: ')-1:].strip()
        api_get_result = self.tester.default_client.resource_drivers.get(driver_id)
        self.assertEqual(api_get_result['id'], driver_id)
        self.assertEqual(api_get_result['type'], 'GCE')
        self.assertEqual(api_get_result['baseUri'], 'http://ansible-lifecycle-driver:8292')
        self.tester.default_client.resource_drivers.delete(driver_id)
    
    def test_create_with_set(self):
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcedriver', '-e', 'default', 
                        '--set', f'baseUri=http://ansible-lifecycle-driver:8292', 
                        '--set', f'type=GCE'
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        driver_id = create_result.output[len('Created: ')-1:].strip()
        time.sleep(0.2)
        api_get_result = self.tester.default_client.resource_drivers.get(driver_id)
        self.assertEqual(api_get_result['id'], driver_id)
        self.assertEqual(api_get_result['type'], 'GCE')
        self.assertEqual(api_get_result['baseUri'], 'http://ansible-lifecycle-driver:8292')
        self.tester.default_client.resource_drivers.delete(driver_id)
    
    def test_delete_with_yaml_file(self):
        driver_id = self.tester.exec_prepended_name('resource-driver-cmd-delete-with-yaml')
        driver = {
            'id': driver_id,
            'type': 'GCE',
            'baseUri': 'http://ansible-lifecycle-driver:8292'
        }
        yml_file = self.tester.create_yaml_file('resource-driver-cmd-delete-with.yaml', driver)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcedriver', '-e', 'default', '-f', yml_file
            ])
        self.assert_no_errors(create_result)
        yml_file = self.tester.create_yaml_file('resource-driver-cmd-delete-with.yaml', driver)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcedriver', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(delete_result, f'Removed: {driver_id}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.resource_drivers.get(driver_id)
            self.fail('Resource Driver should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Resource Driver failed with an unexpected error: {str(e)}')
    
    def test_delete_with_json_file(self):
        driver_id = self.tester.exec_prepended_name('resource-driver-cmd-delete-with-json')
        driver = {
            'id': driver_id,
            'type': 'GCE',
            'baseUri': 'http://ansible-lifecycle-driver:8292'
        }
        json_file = self.tester.create_json_file('resource-driver-cmd-delete-with.json', driver)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcedriver', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        json_file = self.tester.create_json_file('resource-driver-cmd-delete-with.json', driver)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcedriver', '-e', 'default', '-f', json_file
            ])
        self.assert_output(delete_result, f'Removed: {driver_id}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.resource_drivers.get(driver_id)
            self.fail('Resource Driver should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Resource Driver failed with an unexpected error: {str(e)}')
    
    def test_delete_with_id(self):
        driver_id = self.tester.exec_prepended_name('resource-driver-cmd-delete-with-json')
        driver = {
            'id': driver_id,
            'type': 'GCE',
            'baseUri': 'http://ansible-lifecycle-driver:8292'
        }
        json_file = self.tester.create_json_file('resource-driver-cmd-delete-with.json', driver)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcedriver', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcedriver', '-e', 'default', driver_id
            ])
        self.assert_output(delete_result, f'Removed: {driver_id}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.resource_drivers.get(driver_id)
            self.fail('Resource Driver should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Resource Driver failed with an unexpected error: {str(e)}')
      
    def test_delete_with_type(self):
        driver_id = self.tester.exec_prepended_name('resource-driver-cmd-delete-with-json')
        driver = {
            'id': driver_id,
            'type': 'GCE',
            'baseUri': 'http://ansible-lifecycle-driver:8292'
        }
        json_file = self.tester.create_json_file('resource-driver-cmd-delete-with.json', driver)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcedriver', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcedriver', '-e', 'default', '--type', 'GCE'
            ])
        self.assert_output(delete_result, f'Removed: {driver_id}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.resource_drivers.get(driver_id)
            self.fail('Resource Driver should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Resource Driver failed with an unexpected error: {str(e)}')
    
    def test_delete_with_no_id_or_file_fails(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcedriver', '-e', 'default'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete resourcedriver [OPTIONS] [ID]'
        expected_output += '\nTry \'cli delete resourcedriver --help\' for help.'
        expected_output += '\n\nError: Must identify the target by specifying one parameter from ["id", "--type"] or by including one of the following attributes ["id", "infrastructureType"] in the given object/file'
        self.assert_output(delete_result, expected_output)
    
    def test_delete_with_ignore_missing(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcedriver', '-e', 'default', 'NonExistentObj', '--ignore-missing'
            ])
        self.assert_no_errors(delete_result)
        self.assert_output(delete_result, f'(Ignored) 404 Client Error:  for url: https://9.20.192.159/api/resource-manager/resource-drivers/NonExistentObj')