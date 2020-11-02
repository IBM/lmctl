from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat
from lmctl.client import LmClientHttpError
from lmctl.cli.commands.targets.infrastructure_keys import InfrastructureKeyTable
import yaml
import json
import time

class TestInfrastructureKeys(CLIIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        with open(tester.test_file('dummy_key_rsa.pub'), 'r') as f:
            cls.test_case_props['public_key'] = f.read()
        with open(tester.test_file('dummy_key_rsa'), 'r') as f:
            cls.test_case_props['private_key'] = f.read()
        cls.test_case_props['key_A'] = tester.default_client.shared_inf_keys.create({
            'name': tester.exec_prepended_name('inf-key-cmd-A'),
            'publicKey': cls.test_case_props['public_key'],
            'privateKey': cls.test_case_props['private_key']
        })
        cls.test_case_props['key_B'] = tester.default_client.shared_inf_keys.create({
            'name': tester.exec_prepended_name('inf-key-cmd-B'),
            'publicKey': cls.test_case_props['public_key']
        })
        # Get their IDs
        get_A = tester.default_client.shared_inf_keys.get(cls.test_case_props['key_A']['name'])
        cls.test_case_props['key_A']['id'] = get_A['id']
        get_B = tester.default_client.shared_inf_keys.get(cls.test_case_props['key_B']['name'])
        cls.test_case_props['key_B']['id'] = get_B['id']
        
    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.shared_inf_keys.delete(cls.test_case_props['key_A']['name'])
        tester.default_client.shared_inf_keys.delete(cls.test_case_props['key_B']['name'])
    
    def _match_key(self, x: Dict, y: Dict):
        if x.get('name') != y.get('name'):
            return False
        x_pub_key = x.get('publicKey').strip()
        if x_pub_key is not None:
            x_pub_key = x_pub_key.strip()
        y_pub_key = x.get('publicKey').strip()
        if y_pub_key is not None:
            y_pub_key = y_pub_key.strip()
        if x_pub_key != y_pub_key:
            return False
        return True

    def _match_key_with_private(self, x: Dict, y: Dict):
        if x.get('name') != y.get('name'):
            return False
        x_pub_key = x.get('publicKey')
        if x_pub_key is not None:
            x_pub_key = x_pub_key.strip()
        y_pub_key = x.get('publicKey')
        if y_pub_key is not None:
            y_pub_key = y_pub_key.strip()
        if x_pub_key != y_pub_key:
            return False
        x_private_key = x.get('privateKey')
        if x_private_key is not None:
            x_private_key = x_private_key.strip()
        y_private_key = x.get('privateKey')
        if y_private_key is not None:
            y_private_key = y_private_key.strip()
        if x_private_key != y_private_key:
            return False
        return True

    def test_get_all_as_yaml(self):
        result = self.cli_runner.invoke(cli, ['get', 'infrastructurekey', '-e', 'default', '-o', 'yaml'])
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self.test_case_props['key_A'],
                self.test_case_props['key_B']
            ],
            matcher=self._match_key
        )
    
    def test_get_all_as_json(self):
        result = self.cli_runner.invoke(cli, ['get', 'infrastructurekey', '-e', 'default', '-o', 'json'])
        loaded_output = json.loads(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self.test_case_props['key_A'],
                self.test_case_props['key_B']
            ],
            matcher=self._match_key
        )

    def test_get_include_private_key(self):
        result = self.cli_runner.invoke(cli, ['get', 'infrastructurekey', '-e', 'default', '-o', 'yaml', '--include-private'])
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self.test_case_props['key_A'],
                self.test_case_props['key_B']
            ],
            matcher=self._match_key_with_private
        )

    def test_get_by_name_as_yaml(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'infrastructurekey', self.test_case_props['key_A']['name'], '-e', 'default', '-o', 'yaml'
            ])
        loaded_output = yaml.safe_load(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['key_A']['name'])
        self.assertEqual(loaded_output['publicKey'], self.test_case_props['key_A']['publicKey'])
    
    def test_get_by_name_as_json(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'infrastructurekey', self.test_case_props['key_A']['name'], '-e', 'default', '-o', 'json'
            ])
        loaded_output = json.loads(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['key_A']['name'])
        self.assertEqual(loaded_output['publicKey'], self.test_case_props['key_A']['publicKey'])
    
    def test_get_by_name_as_table(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'infrastructurekey', self.test_case_props['key_A']['name'], '-e', 'default', '--include-private'
            ])
        table_format = TableFormat(table=InfrastructureKeyTable())
        expected_output = table_format.convert_element(self.test_case_props['key_A'])
        self.assert_output(result, expected_output)

    def test_create_with_yaml_file(self):
        key_name = self.tester.exec_prepended_name('inf-key-cmd-create-with-yaml')
        inf_key = {
            'name': key_name,
            'publicKey': self.test_case_props['public_key'] 
        }
        yml_file = self.tester.create_yaml_file('inf-key-cmd-create-with.yaml', inf_key)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'infrastructurekey', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(create_result, f'Created: {key_name}')
        api_get_result = self.tester.default_client.shared_inf_keys.get(key_name)
        self.assertEqual(api_get_result['name'], inf_key['name'])
        self.assertEqual(api_get_result['publicKey'], inf_key['publicKey'])

    def test_create_with_json_file(self):
        key_name = self.tester.exec_prepended_name('inf-key-cmd-create-with-json')
        inf_key = {
            'name': key_name,
            'publicKey': self.test_case_props['public_key'] 
        }
        json_file = self.tester.create_json_file('inf-key-cmd-create-with.json', inf_key)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'infrastructurekey', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {key_name}')
        api_get_result = self.tester.default_client.shared_inf_keys.get(key_name)
        self.assertEqual(api_get_result['name'], inf_key['name'])
        self.assertEqual(api_get_result['publicKey'], inf_key['publicKey'])

    def test_create_with_set(self):
        key_name = self.tester.exec_prepended_name('inf-key-cmd-create-with-set')
        pub_key = self.test_case_props['public_key'] 
        create_result = self.cli_runner.invoke(cli, [
            'create', 'infrastructurekey', '-e', 'default', 
                        '--set', f'name={key_name}', 
                        '--set', f'publicKey={pub_key}'
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {key_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.shared_inf_keys.get(key_name)
        self.assertEqual(api_get_result['name'], key_name)
        self.assertEqual(api_get_result['publicKey'], pub_key)

    def test_update_with_yaml_file(self):
        self.test_case_props['key_A']['description'] = 'Updated description for cmd testing with yaml'
        yml_file = self.tester.create_yaml_file('inf-key-cmd-update-with.yaml', self.test_case_props['key_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'infrastructurekey', '-e', 'default', '-f', yml_file
            ])
        key_name = self.test_case_props['key_A']['name']
        self.assert_output(update_result, f'Updated: {key_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.shared_inf_keys.get(key_name)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with yaml')

    def test_update_with_json_file(self):
        self.test_case_props['key_A']['description'] = 'Updated description for cmd testing with json'
        json_file = self.tester.create_json_file('inf-key-cmd-update-with.json', self.test_case_props['key_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'infrastructurekey', '-e', 'default', '-f', json_file
            ])
        key_name = self.test_case_props['key_A']['name']
        self.assert_output(update_result, f'Updated: {key_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.shared_inf_keys.get(key_name)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with json')

    def test_update_with_set(self):
        key_name = self.test_case_props['key_A']['name']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'infrastructurekey', '-e', 'default', key_name, '--set', 'description=Updated descriptor for cmd testing with --set'
            ])
        self.assert_output(update_result, f'Updated: {key_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.shared_inf_keys.get(key_name)
        self.assertEqual(api_get_result['description'], 'Updated descriptor for cmd testing with --set')

    def test_update_with_name_and_file_fails(self):
        yml_file = self.tester.create_yaml_file('inf-key-cmd-update-with-name-and-file-fails.yaml', self.test_case_props['key_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'infrastructurekey', '-e', 'default', 'SomeName', '-f', yml_file
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update infrastructurekey [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli update infrastructurekey --help\' for help.'
        expected_output += '\n\nError: Do not use "NAME" argument when using "-f, --file" option'
        self.assert_output(update_result, expected_output)

    def test_update_with_set_and_no_name_fails(self):
        update_result = self.cli_runner.invoke(cli, [
            'update', 'infrastructurekey', '-e', 'default',  '--set', 'description=testing'
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update infrastructurekey [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli update infrastructurekey --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument when no "-f, --file" option specified'
        self.assert_output(update_result, expected_output)

    def test_delete_with_yaml_file(self):
        key_name = self.tester.exec_prepended_name('inf-key-cmd-delete-with-yaml')
        inf_key = {
            'name': key_name,
            'publicKey': self.test_case_props['public_key']
        }
        yml_file = self.tester.create_yaml_file('inf-key-cmd-delete-with.yaml', inf_key)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'infrastructurekey', '-e', 'default', '-f', yml_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {key_name}')
        inf_key['name'] = key_name
        yml_file = self.tester.create_yaml_file('inf-key-cmd-delete-with.yaml', inf_key)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'infrastructurekey', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(delete_result, f'Removed: {key_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.shared_inf_keys.get(key_name)
            self.fail('Infrastructure Key should have been deleted but it can still be found')
        except LmClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Infrastructure Key failed with an unexpected error: {str(e)}')
    
    def test_delete_with_json_file(self):
        key_name = self.tester.exec_prepended_name('inf-key-cmd-delete-with-json')
        inf_key = {
            'name': key_name,
            'publicKey': self.test_case_props['public_key']
        }
        json_file = self.tester.create_json_file('inf-key-cmd-delete-with.json', inf_key)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'infrastructurekey', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {key_name}')
        inf_key['name'] = key_name
        json_file = self.tester.create_json_file('inf-key-cmd-delete-with.json', inf_key)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'infrastructurekey', '-e', 'default', '-f', json_file
            ])
        self.assert_output(delete_result, f'Removed: {key_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.shared_inf_keys.get(key_name)
            self.fail('Infrastructure Key should have been deleted but it can still be found')
        except LmClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Infrastructure Key failed with an unexpected error: {str(e)}')
    
    def test_delete_with_name(self):
        key_name = self.tester.exec_prepended_name('inf-key-cmd-delete-with-json')
        inf_key = {
            'name': key_name,
            'publicKey': self.test_case_props['public_key']
        }
        json_file = self.tester.create_json_file('inf-key-cmd-delete-with.json', inf_key)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'infrastructurekey', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {key_name}')
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'infrastructurekey', '-e', 'default', key_name
            ])
        self.assert_output(delete_result, f'Removed: {key_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.shared_inf_keys.get(key_name)
            self.fail('Infrastructure Key should have been deleted but it can still be found')
        except LmClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Infrastructure Key failed with an unexpected error: {str(e)}')
    
    def test_delete_with_no_name_or_file_fails(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'infrastructurekey', '-e', 'default'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete infrastructurekey [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli delete infrastructurekey --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument when no "-f, --file" option specified'
        self.assert_output(delete_result, expected_output)
    
    def test_delete_with_ignore_missing(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'infrastructurekey', '-e', 'default', 'NonExistentObj', '--ignore-missing'
            ])
        self.assert_no_errors(delete_result)
        self.assert_output(delete_result, f'No Infrastructure Key found with name NonExistentObj (ignoring)')