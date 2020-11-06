from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat
from lmctl.client import TNCOClientHttpError
from lmctl.cli.commands.targets.descriptors import DescriptorTable
import yaml
import json
import time

class TestDescriptors(CLIIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add an Assembly descriptor
        cls.test_case_props['descriptor_A'] = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='descriptor-cmds-A')
        tester.default_client.descriptors.create(cls.test_case_props['descriptor_A'])
        cls.test_case_props['descriptor_B'] = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='descriptor-cmds-B')
        tester.default_client.descriptors.create(cls.test_case_props['descriptor_B'])

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.descriptors.delete(cls.test_case_props['descriptor_A']['name'])
        tester.default_client.descriptors.delete(cls.test_case_props['descriptor_B']['name'])

    def _build_descriptor_summary(self, descriptor: Dict) -> Dict:
        summary = {
            'name': descriptor['name']
        }
        if 'description' in descriptor:
            summary['description'] = descriptor['description']
        return summary

    def _match_descriptor_summary(self, x: Dict, y: Dict):
        if x.get('name') != y.get('name'):
            return False
        if x.get('description', None) != y.get('description', None):
            return False
        return True

    def test_get_all_as_yaml(self):
        result = self.cli_runner.invoke(cli, ['get', 'descriptor', '-e', 'default', '-o', 'yaml'])
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self._build_descriptor_summary(self.test_case_props['descriptor_A']),
                self._build_descriptor_summary(self.test_case_props['descriptor_B']),
            ],
            matcher=self._match_descriptor_summary
        )
    
    def test_get_all_as_json(self):
        result = self.cli_runner.invoke(cli, ['get', 'descriptor', '-e', 'default', '-o', 'json'])
        loaded_output = json.loads(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self._build_descriptor_summary(self.test_case_props['descriptor_A']),
                self._build_descriptor_summary(self.test_case_props['descriptor_B']),
            ],
            matcher=self._match_descriptor_summary
        )

    def test_get_by_name_as_yaml(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'descriptor', self.test_case_props['descriptor_A']['name'], '-e', 'default', '-o', 'yaml'
            ])
        loaded_output = yaml.safe_load(result.output)
        self.assertEqual(loaded_output, self.test_case_props['descriptor_A'])
    
    def test_get_by_name_as_json(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'descriptor', self.test_case_props['descriptor_A']['name'], '-e', 'default', '-o', 'json'
            ])
        loaded_output = json.loads(result.output)
        self.assertEqual(loaded_output, self.test_case_props['descriptor_A'])
    
    def test_get_by_name_as_table(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'descriptor', self.test_case_props['descriptor_A']['name'], '-e', 'default'
            ])
        table_format = TableFormat(table=DescriptorTable())
        expected_output = table_format.convert_element(self.test_case_props['descriptor_A'])
        self.assert_output(result, expected_output)

    def test_create_with_yaml_file(self):
        descriptor_name = 'assembly::' + self.tester.exec_prepended_name('descriptor-cmd-create-with-yaml') + '::1.0'
        descriptor = {
            'name': descriptor_name,
            'description': 'A test descriptor'
        }
        yml_file = self.tester.create_yaml_file('descriptor-cmd-create-with.yaml', descriptor)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptor', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(create_result, f'Created: {descriptor_name}')
        api_get_result = self.tester.default_client.descriptors.get(descriptor_name)
        self.assertEqual(api_get_result['name'], descriptor['name'])
        self.assertEqual(api_get_result['description'], descriptor['description'])

    def test_create_with_json_file(self):
        descriptor_name = 'assembly::' + self.tester.exec_prepended_name('descriptor-cmd-create-with-json') + '::1.0'
        descriptor = {
            'name': descriptor_name,
            'description': 'A test descriptor'
        }
        json_file = self.tester.create_json_file('descriptor-cmd-create-with.json', descriptor)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptor', '-e', 'default', '-f', json_file
            ])
        self.assert_output(create_result, f'Created: {descriptor_name}')
        api_get_result = self.tester.default_client.descriptors.get(descriptor_name)
        self.assertEqual(api_get_result['name'], descriptor['name'])
        self.assertEqual(api_get_result['description'], descriptor['description'])

    def test_create_with_set(self):
        descriptor_name = 'assembly::' + self.tester.exec_prepended_name('descriptor-cmd-create-with-set') + '::1.0'
        description = 'Just testing cmds'
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptor', '-e', 'default', 
                        '--set', f'name={descriptor_name}', 
                        '--set', f'description={description}'
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {descriptor_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.descriptors.get(descriptor_name)
        self.assertEqual(api_get_result['name'], descriptor_name)
        self.assertEqual(api_get_result['description'], description)

    def test_update_with_yaml_file(self):
        self.test_case_props['descriptor_A']['description'] = 'Updated description for cmd testing with yaml'
        yml_file = self.tester.create_yaml_file('descriptor-cmd-update-with.yaml', self.test_case_props['descriptor_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'descriptor', '-e', 'default', '-f', yml_file
            ])
        descriptor_name = self.test_case_props['descriptor_A']['name']
        self.assert_output(update_result, f'Updated: {descriptor_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.descriptors.get(descriptor_name)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with yaml')

    def test_update_with_json_file(self):
        self.test_case_props['descriptor_A']['description'] = 'Updated description for cmd testing with json'
        json_file = self.tester.create_json_file('descriptor-cmd-update-with.json', self.test_case_props['descriptor_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'descriptor', '-e', 'default', '-f', json_file
            ])
        descriptor_name = self.test_case_props['descriptor_A']['name']
        self.assert_output(update_result, f'Updated: {descriptor_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.descriptors.get(descriptor_name)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with json')

    def test_update_with_set(self):
        descriptor_name = self.test_case_props['descriptor_A']['name']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'descriptor', '-e', 'default', descriptor_name, '--set', 'description=Updated descriptor for cmd testing with --set'
            ])
        self.assert_output(update_result, f'Updated: {descriptor_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.descriptors.get(descriptor_name)
        self.assertEqual(api_get_result['description'], 'Updated descriptor for cmd testing with --set')

    def test_update_with_name_and_file_fails(self):
        yml_file = self.tester.create_yaml_file('descriptor-cmd-update-with-name-and-file-fails.yaml', self.test_case_props['descriptor_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'descriptor', '-e', 'default', 'SomeName', '-f', yml_file
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update descriptor [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli update descriptor --help\' for help.'
        expected_output += '\n\nError: Do not use "NAME" argument when using "-f, --file" option'
        self.assert_output(update_result, expected_output)

    def test_update_with_set_and_no_name_fails(self):
        update_result = self.cli_runner.invoke(cli, [
            'update', 'descriptor', '-e', 'default',  '--set', 'description=testing'
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update descriptor [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli update descriptor --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument when no "-f, --file" option specified'
        self.assert_output(update_result, expected_output)

    def test_delete_with_yaml_file(self):
        descriptor_name = 'assembly::' + self.tester.exec_prepended_name('descriptor-cmd-delete-with-yaml') + '::1.0'
        descriptor = {
            'name': descriptor_name,
            'description': 'Just testing'
        }
        yml_file = self.tester.create_yaml_file('descriptor-cmd-delete-with.yaml', descriptor)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptor', '-e', 'default', '-f', yml_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {descriptor_name}')
        descriptor['name'] = descriptor_name
        yml_file = self.tester.create_yaml_file('descriptor-cmd-delete-with.yaml', descriptor)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'descriptor', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(delete_result, f'Removed: {descriptor_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.descriptors.get(descriptor_name)
            self.fail('Descriptor should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Descriptor failed with an unexpected error: {str(e)}')
    
    def test_delete_with_json_file(self):
        descriptor_name = 'assembly::' +  self.tester.exec_prepended_name('descriptor-cmd-delete-with-json') + '::1.0'
        descriptor = {
            'name': descriptor_name,
            'description': 'Just testing'
        }
        json_file = self.tester.create_json_file('descriptor-cmd-delete-with.json', descriptor)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptor', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {descriptor_name}')
        descriptor['name'] = descriptor_name
        json_file = self.tester.create_json_file('descriptor-cmd-delete-with.json', descriptor)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'descriptor', '-e', 'default', '-f', json_file
            ])
        self.assert_output(delete_result, f'Removed: {descriptor_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.descriptors.get(descriptor_name)
            self.fail('Descriptor should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Descriptor failed with an unexpected error: {str(e)}')
    
    def test_delete_with_name(self):
        descriptor_name = 'assembly::' + self.tester.exec_prepended_name('descriptor-cmd-delete-with-json') + '::1.0'
        descriptor = {
            'name': descriptor_name,
            'description': 'Just testing'
        }
        json_file = self.tester.create_json_file('descriptor-cmd-delete-with.json', descriptor)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptor', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {descriptor_name}')
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'descriptor', '-e', 'default', descriptor_name
            ])
        self.assert_output(delete_result, f'Removed: {descriptor_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.descriptors.get(descriptor_name)
            self.fail('Descriptor should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Descriptor failed with an unexpected error: {str(e)}')
    
    def test_delete_with_no_name_or_file_fails(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'descriptor', '-e', 'default'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete descriptor [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli delete descriptor --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument when no "-f, --file" option specified'
        self.assert_output(delete_result, expected_output)
    
    def test_delete_with_ignore_missing(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'descriptor', '-e', 'default', 'assembly::nonexistent::1.0', '--ignore-missing'
            ])
        self.assert_no_errors(delete_result)
        self.assert_output(delete_result, f'No Descriptor found with name assembly::nonexistent::1.0 (ignoring)')