from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat
from lmctl.client import TNCOClientHttpError
from lmctl.cli.commands.targets.descriptor_templates import DescriptorTemplatesTable
import yaml
import json
import time

class TestDescriptorTemplates(CLIIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add an Assembly Template descriptor
        cls.test_case_props['template_A'] = tester.load_descriptor_from(tester.test_file('dummy_template.yaml'), suffix='template-cmds-A')
        tester.default_client.descriptor_templates.create(cls.test_case_props['template_A'])
        cls.test_case_props['template_B'] = tester.load_descriptor_from(tester.test_file('dummy_template.yaml'), suffix='template-cmds-B')
        tester.default_client.descriptor_templates.create(cls.test_case_props['template_B'])
        cls.test_case_props['template_raw_output'] = {
            'name': 'assembly-template::' + tester.exec_prepended_name('template-cmd-render-raw') + '::1.0', 
            'template': 'NotValidOutput'
        }
        tester.default_client.descriptor_templates.create(cls.test_case_props['template_raw_output'])

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.descriptor_templates.delete(cls.test_case_props['template_A']['name'])
        tester.default_client.descriptor_templates.delete(cls.test_case_props['template_B']['name'])
        tester.default_client.descriptor_templates.delete(cls.test_case_props['template_raw_output']['name'])

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
        result = self.cli_runner.invoke(cli, ['get', 'descriptortemplate', '-e', 'default', '-o', 'yaml'])
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self._build_descriptor_summary(self.test_case_props['template_A']),
                self._build_descriptor_summary(self.test_case_props['template_B']),
            ],
            matcher=self._match_descriptor_summary
        )
    
    def test_get_all_as_json(self):
        result = self.cli_runner.invoke(cli, ['get', 'descriptortemplate', '-e', 'default', '-o', 'json'])
        loaded_output = json.loads(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self._build_descriptor_summary(self.test_case_props['template_A']),
                self._build_descriptor_summary(self.test_case_props['template_B']),
            ],
            matcher=self._match_descriptor_summary
        )

    def test_get_by_name_as_yaml(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'descriptortemplate', self.test_case_props['template_A']['name'], '-e', 'default', '-o', 'yaml'
            ])
        loaded_output = yaml.safe_load(result.output)
        self.assertEqual(loaded_output, self.test_case_props['template_A'])
    
    def test_get_by_name_as_json(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'descriptortemplate', self.test_case_props['template_A']['name'], '-e', 'default', '-o', 'json'
            ])
        loaded_output = json.loads(result.output)
        self.assertEqual(loaded_output, self.test_case_props['template_A'])
    
    def test_get_by_name_as_table(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'descriptortemplate', self.test_case_props['template_A']['name'], '-e', 'default'
            ])
        table_format = TableFormat(table=DescriptorTemplatesTable())
        expected_output = table_format.convert_element(self.test_case_props['template_A'])
        self.assert_output(result, expected_output)

    def test_create_with_yaml_file(self):
        descriptor_name = 'assembly-template::' + self.tester.exec_prepended_name('template-cmd-create-with-yaml') + '::1.0'
        descriptor = {
            'name': descriptor_name,
            'description': 'A test descriptor',
            'template': 'name: assembly::test::1.0'
        }
        yml_file = self.tester.create_yaml_file('template-cmd-create-with.yaml', descriptor)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptortemplate', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(create_result, f'Created: {descriptor_name}')
        api_get_result = self.tester.default_client.descriptor_templates.get(descriptor_name)
        self.assertEqual(api_get_result['name'], descriptor['name'])
        self.assertEqual(api_get_result['description'], descriptor['description'])

    def test_create_with_json_file(self):
        descriptor_name = 'assembly-template::' + self.tester.exec_prepended_name('template-cmd-create-with-json') + '::1.0'
        descriptor = {
            'name': descriptor_name,
            'description': 'A test descriptor',
            'template': 'name: assembly::test::1.0'
        }
        json_file = self.tester.create_json_file('template-cmd-create-with.json', descriptor)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptortemplate', '-e', 'default', '-f', json_file
            ])
        self.assert_output(create_result, f'Created: {descriptor_name}')
        api_get_result = self.tester.default_client.descriptor_templates.get(descriptor_name)
        self.assertEqual(api_get_result['name'], descriptor['name'])
        self.assertEqual(api_get_result['description'], descriptor['description'])

    def test_create_with_set(self):
        descriptor_name = 'assembly-template::' + self.tester.exec_prepended_name('template-cmd-create-with-set') + '::1.0'
        description = 'Just testing cmds'
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptortemplate', '-e', 'default', 
                        '--set', f'name={descriptor_name}', 
                        '--set', f'description={description}',
                        '--set', f'template=name: assembly::testing::1.0'
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {descriptor_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.descriptor_templates.get(descriptor_name)
        self.assertEqual(api_get_result['name'], descriptor_name)
        self.assertEqual(api_get_result['description'], description)
        self.assertEqual(api_get_result['template'], 'name: assembly::testing::1.0')

    def test_update_with_yaml_file(self):
        self.test_case_props['template_A']['description'] = 'Updated description for cmd testing with yaml'
        yml_file = self.tester.create_yaml_file('template-cmd-update-with.yaml', self.test_case_props['template_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'descriptortemplate', '-e', 'default', '-f', yml_file
            ])
        descriptor_name = self.test_case_props['template_A']['name']
        self.assert_output(update_result, f'Updated: {descriptor_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.descriptor_templates.get(descriptor_name)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with yaml')

    def test_update_with_json_file(self):
        self.test_case_props['template_A']['description'] = 'Updated description for cmd testing with json'
        json_file = self.tester.create_json_file('template-cmd-update-with.json', self.test_case_props['template_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'descriptortemplate', '-e', 'default', '-f', json_file
            ])
        descriptor_name = self.test_case_props['template_A']['name']
        self.assert_output(update_result, f'Updated: {descriptor_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.descriptor_templates.get(descriptor_name)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with json')

    def test_update_with_set(self):
        descriptor_name = self.test_case_props['template_A']['name']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'descriptortemplate', '-e', 'default', descriptor_name, '--set', 'description=Updated descriptor for cmd testing with --set'
            ])
        self.assert_output(update_result, f'Updated: {descriptor_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.descriptor_templates.get(descriptor_name)
        self.assertEqual(api_get_result['description'], 'Updated descriptor for cmd testing with --set')

    def test_update_with_name_and_file_fails(self):
        yml_file = self.tester.create_yaml_file('template-cmd-update-with-name-and-file-fails.yaml', self.test_case_props['template_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'descriptortemplate', '-e', 'default', 'SomeName', '-f', yml_file
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update descriptortemplate [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli update descriptortemplate --help\' for help.'
        expected_output += '\n\nError: Do not use "NAME" argument when using "-f, --file" option'
        self.assert_output(update_result, expected_output)

    def test_update_with_set_and_no_name_fails(self):
        update_result = self.cli_runner.invoke(cli, [
            'update', 'descriptortemplate', '-e', 'default',  '--set', 'description=testing'
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update descriptortemplate [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli update descriptortemplate --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument when no "-f, --file" option specified'
        self.assert_output(update_result, expected_output)

    def test_delete_with_yaml_file(self):
        descriptor_name = 'assembly-template::' + self.tester.exec_prepended_name('template-cmd-delete-with-yaml') + '::1.0'
        descriptor = {
            'name': descriptor_name,
            'description': 'Just testing',
            'template': 'name: assembly::test::1.0'
        }
        yml_file = self.tester.create_yaml_file('template-cmd-delete-with.yaml', descriptor)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptortemplate', '-e', 'default', '-f', yml_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {descriptor_name}')
        descriptor['name'] = descriptor_name
        yml_file = self.tester.create_yaml_file('template-cmd-delete-with.yaml', descriptor)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'descriptortemplate', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(delete_result, f'Removed: {descriptor_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.descriptor_templates.get(descriptor_name)
            self.fail('Descriptor Template should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Descriptor Template failed with an unexpected error: {str(e)}')
    
    def test_delete_with_json_file(self):
        descriptor_name = 'assembly-template::' +  self.tester.exec_prepended_name('template-cmd-delete-with-json') + '::1.0'
        descriptor = {
            'name': descriptor_name,
            'description': 'Just testing',
            'template': 'name: assembly::test::1.0'
        }
        json_file = self.tester.create_json_file('template-cmd-delete-with.json', descriptor)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptortemplate', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {descriptor_name}')
        descriptor['name'] = descriptor_name
        json_file = self.tester.create_json_file('template-cmd-delete-with.json', descriptor)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'descriptortemplate', '-e', 'default', '-f', json_file
            ])
        self.assert_output(delete_result, f'Removed: {descriptor_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.descriptor_templates.get(descriptor_name)
            self.fail('Descriptor Template should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Descriptor Template failed with an unexpected error: {str(e)}')
    
    def test_delete_with_name(self):
        descriptor_name = 'assembly-template::' + self.tester.exec_prepended_name('template-cmd-delete-with-json') + '::1.0'
        descriptor = {
            'name': descriptor_name,
            'description': 'Just testing',
            'template': 'name: assembly::test::1.0'
        }
        json_file = self.tester.create_json_file('template-cmd-delete-with.json', descriptor)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'descriptortemplate', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {descriptor_name}')
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'descriptortemplate', '-e', 'default', descriptor_name
            ])
        self.assert_output(delete_result, f'Removed: {descriptor_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.descriptor_templates.get(descriptor_name)
            self.fail('Descriptor Template should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Descriptor Template failed with an unexpected error: {str(e)}')
    
    def test_delete_with_no_name_or_file_fails(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'descriptortemplate', '-e', 'default'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete descriptortemplate [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli delete descriptortemplate --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument when no "-f, --file" option specified'
        self.assert_output(delete_result, expected_output)
    
    def test_delete_with_ignore_missing(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'descriptortemplate', '-e', 'default', 'assembly-template::nonexistent::1.0', '--ignore-missing'
            ])
        self.assert_no_errors(delete_result)
        self.assert_output(delete_result, f'No Descriptor Template found with name assembly-template::nonexistent::1.0 (ignoring)')

    def test_render_with_name_and_prop(self):
        render_result = self.cli_runner.invoke(cli, [
            'render', 'descriptortemplate', self.test_case_props['template_A']['name'], '-e', 'default', '--prop', 'dummyProp=A'
            ])
        self.assert_no_errors(render_result)
        loaded_output = yaml.safe_load(render_result.output)
        self.assertEqual(loaded_output['name'], 'assembly::JustTesting::1.0')
        self.assertEqual(loaded_output['description'], 'Adding a value from template properties -> A')

    def test_render_with_yaml_template_file(self):
        yaml_file = self.tester.create_yaml_file('template-cmd-render-with.yaml', self.test_case_props['template_A'])
        render_result = self.cli_runner.invoke(cli, [
            'render', 'descriptortemplate', '-e', 'default', '-f', yaml_file, '--prop', 'dummyProp=A'
            ])
        self.assert_no_errors(render_result)
        loaded_output = yaml.safe_load(render_result.output)
        self.assertEqual(loaded_output['name'], 'assembly::JustTesting::1.0')
        self.assertEqual(loaded_output['description'], 'Adding a value from template properties -> A')
    
    def test_render_with_json_template_file(self):
        json_file = self.tester.create_json_file('template-cmd-render-with.json', self.test_case_props['template_A'])
        render_result = self.cli_runner.invoke(cli, [
            'render', 'descriptortemplate', '-e', 'default', '-f', json_file, '--prop', 'dummyProp=B'
            ])
        self.assert_no_errors(render_result)
        loaded_output = yaml.safe_load(render_result.output)
        self.assertEqual(loaded_output['name'], 'assembly::JustTesting::1.0')
        self.assertEqual(loaded_output['description'], 'Adding a value from template properties -> B')
    
    def test_render_with_template_file_and_name_fails(self):
        json_file = self.tester.create_json_file('template-cmd-render-with-name-and-template.json', self.test_case_props['template_A'])
        render_result = self.cli_runner.invoke(cli, [
            'render', 'descriptortemplate', self.test_case_props['template_A']['name'], '-e', 'default', '-f', json_file, '--prop', 'dummyProp=B'
            ])
        self.assert_has_system_exit(render_result)
        expected_output = 'Usage: cli render descriptortemplate [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli render descriptortemplate --help\' for help.'
        expected_output += '\n\nError: Do not use "NAME" argument when using "-f, --file" option'
        self.assert_output(render_result, expected_output)
    
    def test_render_with_template_file_missing_name_fails(self):
        template = {'description': 'No name'}
        json_file = self.tester.create_json_file('template-cmd-render-with-file-missing-name.json', template)
        render_result = self.cli_runner.invoke(cli, [
            'render', 'descriptortemplate', '-e', 'default', '-f', json_file, '--prop', 'dummyProp=B'
            ])
        self.assert_has_system_exit(render_result)
        expected_output = 'Usage: cli render descriptortemplate [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli render descriptortemplate --help\' for help.'
        expected_output += '\n\nError: Object from file does not contain a "name" attribute'
        self.assert_output(render_result, expected_output)
    
    def test_render_with_without_template_or_name_fails(self):
        render_result = self.cli_runner.invoke(cli, [
            'render', 'descriptortemplate', '-e', 'default', '--prop', 'dummyProp=B'
            ])
        self.assert_has_system_exit(render_result)
        expected_output = 'Usage: cli render descriptortemplate [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli render descriptortemplate --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument when no "-f, --file" option specified'
        self.assert_output(render_result, expected_output)
    
    def test_render_with_yaml_request_file(self):
        request = {
            'properties': {'dummyProp': 'C'}
        }
        yaml_file = self.tester.create_yaml_file('template-cmd-render-request-with.yaml', request)
        render_result = self.cli_runner.invoke(cli, [
            'render', 'descriptortemplate', self.test_case_props['template_A']['name'], '-e', 'default', '-r', yaml_file
            ])
        self.assert_no_errors(render_result)
        loaded_output = yaml.safe_load(render_result.output)
        self.assertEqual(loaded_output['name'], 'assembly::JustTesting::1.0')
        self.assertEqual(loaded_output['description'], 'Adding a value from template properties -> C')
    
    def test_render_with_json_request_file(self):
        request = {
            'properties': {'dummyProp': 'C'}
        }
        json_file = self.tester.create_json_file('template-cmd-render-request-with.json', request)
        render_result = self.cli_runner.invoke(cli, [
            'render', 'descriptortemplate', self.test_case_props['template_A']['name'], '-e', 'default', '-r', json_file
            ])
        self.assert_no_errors(render_result)
        loaded_output = yaml.safe_load(render_result.output)
        self.assertEqual(loaded_output['name'], 'assembly::JustTesting::1.0')
        self.assertEqual(loaded_output['description'], 'Adding a value from template properties -> C')
    
    def test_render_with_request_file_and_prop_fails(self):
        request = {
            'properties': {'dummyProp': 'C'}
        }
        json_file = self.tester.create_json_file('template-cmd-render-request-with.json', request)
        render_result = self.cli_runner.invoke(cli, [
            'render', 'descriptortemplate', self.test_case_props['template_A']['name'], '-e', 'default', '-r', json_file, '--prop', 'dummyProp=D'
            ])
        self.assert_has_system_exit(render_result)
        expected_output = 'Usage: cli render descriptortemplate [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli render descriptortemplate --help\' for help.'
        expected_output += '\n\nError: Do not use "--prop" option when using "-r, --request-file" option'
        self.assert_output(render_result, expected_output)
    
    def test_render_with_to_json_output(self):
        render_result = self.cli_runner.invoke(cli, [
            'render', 'descriptortemplate', '-o', 'json', self.test_case_props['template_A']['name'], '-e', 'default', '--prop', 'dummyProp=A'
            ])
        self.assert_no_errors(render_result)
        loaded_output = json.loads(render_result.output)
        self.assertEqual(loaded_output['name'], 'assembly::JustTesting::1.0')
        self.assertEqual(loaded_output['description'], 'Adding a value from template properties -> A')
    
    def test_render_raw(self):
        render_result = self.cli_runner.invoke(cli, [
            'render', 'descriptortemplate', self.test_case_props['template_raw_output']['name'], '-e', 'default', '--prop', 'dummyProp=A', '--raw'
            ])
        self.assert_no_errors(render_result)
        self.assert_output(render_result, 'NotValidOutput')