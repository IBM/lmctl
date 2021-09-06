from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat, Table
from lmctl.client import TNCOClientHttpError
from lmctl.cli.commands.behaviour_assembly_configurations import default_columns
import yaml
import json
import time

class TestBehaviourAssemblyConfigurations(CLIIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add an Assembly descriptor so a project is available
        assembly_descriptor = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='assembly-config-cmds')
        tester.default_client.descriptors.create(assembly_descriptor)
        cls.test_case_props['assembly_descriptor_name'] = assembly_descriptor['name']
        cls.test_case_props['project_name'] = assembly_descriptor['name']
        ## Add some Assembly configurations
        cls.test_case_props['assembly_config_A'] = tester.default_client.behaviour_assembly_confs.create({
            'name': tester.exec_prepended_name('assembly-config-cmds-A'),
            'projectId': cls.test_case_props['project_name'],
            'descriptorName': cls.test_case_props['assembly_descriptor_name'],
            'properties': {
                'resourceManager': 'brent',
                'dummyProp': 'testing'
            }
        })
        cls.test_case_props['assembly_config_B'] = tester.default_client.behaviour_assembly_confs.create({
            'name': tester.exec_prepended_name('assembly-config-cmds-B'),
            'projectId': cls.test_case_props['project_name'],
            'descriptorName': cls.test_case_props['assembly_descriptor_name'],
            'properties': {
                'resourceManager': 'brent',
                'dummyProp': 'testing'
            }
        })

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.descriptors.delete(cls.test_case_props['assembly_descriptor_name'])

    def _match_assembly_configuration(self, x: Dict, y: Dict):
        if x.get('id') != y.get('id'):
            return False
        if x.get('name') != y.get('name'):
            return False
        return True

    def test_get_all_as_yaml(self):
        result = self.cli_runner.invoke(cli, ['get', 'assemblyconfig', '-e', 'default', '--project', self.test_case_props['project_name'], '-o', 'yaml'])
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self.test_case_props['assembly_config_A'],
                self.test_case_props['assembly_config_B']
            ],
            matcher=self._match_assembly_configuration
        )
    
    def test_get_all_as_json(self):
        result = self.cli_runner.invoke(cli, ['get', 'assemblyconfig', '-e', 'default', '--project', self.test_case_props['project_name'], '-o', 'json'])
        loaded_output = json.loads(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self.test_case_props['assembly_config_A'],
                self.test_case_props['assembly_config_B']
            ],
            matcher=self._match_assembly_configuration
        )

    def test_get_by_id_as_yaml(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assemblyconfig', self.test_case_props['assembly_config_A']['id'], '-e', 'default', '-o', 'yaml'
            ])
        loaded_output = yaml.safe_load(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['assembly_config_A']['name'])
        self.assertEqual(loaded_output['id'], self.test_case_props['assembly_config_A']['id'])
    
    def test_get_by_id_as_json(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assemblyconfig', self.test_case_props['assembly_config_A']['id'], '-e', 'default', '-o', 'json'
            ])
        loaded_output = json.loads(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['assembly_config_A']['name'])
        self.assertEqual(loaded_output['id'], self.test_case_props['assembly_config_A']['id'])
    
    def test_get_by_id_as_table(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assemblyconfig', self.test_case_props['assembly_config_A']['id'], '-e', 'default'
            ])
        table_format = TableFormat(table=Table(columns=default_columns))
        expected_output = table_format.convert_element(self.test_case_props['assembly_config_A'])
        self.assert_output(result, expected_output)

    def test_get_with_id_and_project_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assemblyconfig', 'SomeId', '--project', 'SomeProject', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get assemblyconfig [OPTIONS] [ID]'
        expected_output += '\nTry \'cli get assemblyconfig --help\' for help.'
        expected_output += '\n\nError: Cannot use "--project" with "id" as they are mutually exclusive'
        self.assert_output(result, expected_output)
    
    def test_get_without_id_or_project_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assemblyconfig', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get assemblyconfig [OPTIONS] [ID]'
        expected_output += '\nTry \'cli get assemblyconfig --help\' for help.'
        expected_output += '\n\nError: Must identify the target by specifying one parameter from ["id", "--project"] or by including one of the following attributes ["id", "projectId"] in the given object/file'
        self.assert_output(result, expected_output)

    def test_create_with_yaml_file(self):
        assembly_config_name = self.tester.exec_prepended_name('assembly-config-cmd-create-with-yaml')
        assembly_config = {
            'name': assembly_config_name,
            'projectId': self.test_case_props['project_name'],
            'descriptorName': self.test_case_props['assembly_descriptor_name'],
            'properties': {
                'resourceManager': 'brent',
                'dummyProp': 'testing'
            }
        }
        yml_file = self.tester.create_yaml_file('assembly-config-cmd-create-with.yaml', assembly_config)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'assemblyconfig', '-e', 'default', '-f', yml_file
            ])
        self.assertTrue(create_result.output.startswith('Created: '))
        assembly_config_id = create_result.output[len('Created: ')-1:create_result.output.index('(')].strip()
        api_get_result = self.tester.default_client.behaviour_assembly_confs.get(assembly_config_id)
        self.assertEqual(api_get_result['name'], assembly_config['name'])
        self.assertEqual(api_get_result['projectId'], assembly_config['projectId'])
        self.assertEqual(api_get_result['descriptorName'], assembly_config['descriptorName'])
        self.assertEqual(api_get_result['properties'], assembly_config['properties'])

    def test_create_with_json_file(self):
        assembly_config_name = self.tester.exec_prepended_name('assembly-config-cmd-create-with-json')
        assembly_config = {
            'name': assembly_config_name,
            'projectId': self.test_case_props['project_name'],
            'descriptorName': self.test_case_props['assembly_descriptor_name'],
            'properties': {
                'resourceManager': 'brent',
                'dummyProp': 'testing'
            }
        }
        json_file = self.tester.create_json_file('assembly-config-cmd-create-with.json', assembly_config)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'assemblyconfig', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        assembly_config_id = create_result.output[len('Created: ')-1:create_result.output.index('(')].strip()
        api_get_result = self.tester.default_client.behaviour_assembly_confs.get(assembly_config_id)
        self.assertEqual(api_get_result['name'], assembly_config['name'])
        self.assertEqual(api_get_result['projectId'], assembly_config['projectId'])
        self.assertEqual(api_get_result['descriptorName'], assembly_config['descriptorName'])
        self.assertEqual(api_get_result['properties'], assembly_config['properties'])

    def test_create_with_set(self):
        assembly_config_name = self.tester.exec_prepended_name('assembly-config-cmd-create-with-set')
        project_id = self.test_case_props['project_name']
        descriptor_name = self.test_case_props['assembly_descriptor_name']
        create_result = self.cli_runner.invoke(cli, [
            'create', 'assemblyconfig', '-e', 'default', 
                        '--set', f'name={assembly_config_name}', 
                        '--set', f'projectId={project_id}', 
                        '--set', f'descriptorName={descriptor_name}'
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        assembly_config_id = create_result.output[len('Created: ')-1:create_result.output.index('(')].strip()
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_assembly_confs.get(assembly_config_id)
        self.assertEqual(api_get_result['name'], assembly_config_name)
        self.assertEqual(api_get_result['projectId'], project_id)
        self.assertEqual(api_get_result['descriptorName'], descriptor_name)

    def test_update_with_yaml_file(self):
        self.test_case_props['assembly_config_A']['description'] = 'Updated description for cmd testing with yaml'
        yml_file = self.tester.create_yaml_file('assembly-config-cmd-update-with.yaml', self.test_case_props['assembly_config_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'assemblyconfig', '-e', 'default', '-f', yml_file
            ])
        assembly_config_id = self.test_case_props['assembly_config_A']['id']
        assembly_config_name = self.test_case_props['assembly_config_A']['name']
        self.assert_output(update_result, f'Updated: {assembly_config_id} ({assembly_config_name})')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_assembly_confs.get(assembly_config_id)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with yaml')

    def test_update_with_json_file(self):
        self.test_case_props['assembly_config_A']['description'] = 'Updated description for cmd testing with json'
        json_file = self.tester.create_json_file('assembly-config-cmd-update-with.json', self.test_case_props['assembly_config_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'assemblyconfig', '-e', 'default', '-f', json_file
            ])
        assembly_config_id = self.test_case_props['assembly_config_A']['id']
        assembly_config_name = self.test_case_props['assembly_config_A']['name']
        self.assert_output(update_result, f'Updated: {assembly_config_id} ({assembly_config_name})')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_assembly_confs.get(assembly_config_id)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with json')

    def test_update_with_set(self):
        assembly_config_id = self.test_case_props['assembly_config_A']['id']
        assembly_config_name = self.test_case_props['assembly_config_A']['name']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'assemblyconfig', '-e', 'default', assembly_config_id, '--set', 'description=Updated descriptor for cmd testing with --set'
            ])
        self.assert_output(update_result, f'Updated: {assembly_config_id} ({assembly_config_name})')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_assembly_confs.get(assembly_config_id)
        self.assertEqual(api_get_result['description'], 'Updated descriptor for cmd testing with --set')

    def test_update_with_id_and_file(self):
        assembly_config_id = self.test_case_props['assembly_config_A']['id']
        assembly_config_name = self.test_case_props['assembly_config_A']['name']
        assembly_config = self.test_case_props['assembly_config_A'].copy()
        assembly_config['description'] = 'Updated descriptor for cmd testing with file'
        yml_file = self.tester.create_yaml_file('assembly-config-cmd-update-with-id-and-file.yaml', assembly_config)
        update_result = self.cli_runner.invoke(cli, [
            'update', 'assemblyconfig', '-e', 'default', assembly_config_id, '-f', yml_file
            ])
        self.assert_no_errors(update_result)
        self.assert_output(update_result, f'Updated: {assembly_config_id} ({assembly_config_name})')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_assembly_confs.get(assembly_config_id)
        self.assertEqual(api_get_result['description'], 'Updated descriptor for cmd testing with file')


    def test_update_with_set_and_no_id_fails(self):
        update_result = self.cli_runner.invoke(cli, [
            'update', 'assemblyconfig', '-e', 'default',  '--set', 'description=testing'
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update assemblyconfig [OPTIONS] [ID]'
        expected_output += '\nTry \'cli update assemblyconfig --help\' for help.'
        expected_output += '\n\nError: Must identify the target by specifying the "id" parameter or by including the "id" attribute in the given object/file'
        self.assert_output(update_result, expected_output)

    def test_delete_with_yaml_file(self):
        assembly_config_name = self.tester.exec_prepended_name('assembly-config-cmd-delete-with-yaml')
        assembly_config = {
            'name': assembly_config_name,
            'projectId': self.test_case_props['project_name'],
            'descriptorName': self.test_case_props['assembly_descriptor_name']
        }
        yml_file = self.tester.create_yaml_file('assembly-config-cmd-delete-with.yaml', assembly_config)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'assemblyconfig', '-e', 'default', '-f', yml_file
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        assembly_config_id = create_result.output[len('Created: ')-1:create_result.output.index('(')].strip()
        assembly_config['id'] = assembly_config_id
        yml_file = self.tester.create_yaml_file('assembly-config-cmd-delete-with.yaml', assembly_config)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assemblyconfig', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(delete_result, f'Removed: {assembly_config_id}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.behaviour_assembly_confs.get(assembly_config_id)
            self.fail('Assembly Configuration should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Assembly Configuration failed with an unexpected error: {str(e)}')
    
    def test_delete_with_json_file(self):
        assembly_config_name = self.tester.exec_prepended_name('assembly-config-cmd-delete-with-json')
        assembly_config = {
            'name': assembly_config_name,
            'projectId': self.test_case_props['project_name'],
            'descriptorName': self.test_case_props['assembly_descriptor_name']
        }
        json_file = self.tester.create_json_file('assembly-config-cmd-delete-with.json', assembly_config)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'assemblyconfig', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        assembly_config_id = create_result.output[len('Created: ')-1:create_result.output.index('(')].strip()
        assembly_config['id'] = assembly_config_id
        json_file = self.tester.create_json_file('assembly-config-cmd-delete-with.json', assembly_config)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assemblyconfig', '-e', 'default', '-f', json_file
            ])
        self.assert_output(delete_result, f'Removed: {assembly_config_id}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.behaviour_assembly_confs.get(assembly_config_id)
            self.fail('Assembly Configuration should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Assembly Configuration failed with an unexpected error: {str(e)}')
    
    def test_delete_with_id(self):
        assembly_config_name = self.tester.exec_prepended_name('assembly-config-cmd-delete-with-json')
        assembly_config = {
            'name': assembly_config_name,
            'projectId': self.test_case_props['project_name'],
            'descriptorName': self.test_case_props['assembly_descriptor_name']
        }
        json_file = self.tester.create_json_file('assembly-config-cmd-delete-with.json', assembly_config)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'assemblyconfig', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        assembly_config_id = create_result.output[len('Created: ')-1:create_result.output.index('(')].strip()
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assemblyconfig', '-e', 'default', assembly_config_id
            ])
        self.assert_output(delete_result, f'Removed: {assembly_config_id}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.behaviour_assembly_confs.get(assembly_config_id)
            self.fail('Assembly Configuration should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Assembly Configuration failed with an unexpected error: {str(e)}')
    
    def test_delete_with_no_name_or_file_fails(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assemblyconfig', '-e', 'default'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete assemblyconfig [OPTIONS] [ID]'
        expected_output += '\nTry \'cli delete assemblyconfig --help\' for help.'
        expected_output += '\n\nError: Must identify the target by specifying the "id" parameter or by including the "id" attribute in the given object/file'
        self.assert_output(delete_result, expected_output)
    
    def test_delete_with_ignore_missing(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assemblyconfig', '-e', 'default', 'NonExistentObj', '--ignore-missing'
            ])
        self.assert_no_errors(delete_result)
        self.assert_output(delete_result, f'(Ignored) Entity of type \'AssemblyConfiguration\' could not be found matching: id=NonExistentObj')