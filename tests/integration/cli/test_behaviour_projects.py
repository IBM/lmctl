from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat, Table
from lmctl.client import TNCOClientHttpError
from lmctl.cli.commands.behaviour_projects import default_columns
import yaml
import json
import time

class TestBehaviourProjects(CLIIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Create a Project
        cls.test_case_props['project_A'] = tester.default_client.behaviour_projects.create({
            'name': tester.exec_prepended_name('project-cmds-A'),
            'description': 'LMCTL testing'
        })
        cls.test_case_props['project_B'] = tester.default_client.behaviour_projects.create({
            'name': tester.exec_prepended_name('project-cmds-B'),
            'description': 'LMCTL testing'
        })

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.behaviour_projects.delete(cls.test_case_props['project_A']['id'])
        tester.default_client.behaviour_projects.delete(cls.test_case_props['project_B']['id'])

    def _match_project(self, x: Dict, y: Dict):
        if x.get('id') != y.get('id'):
            return False
        if x.get('name') != y.get('name'):
            return False
        return True

    def test_get_all_as_yaml(self):
        result = self.cli_runner.invoke(cli, ['get', 'behaviourproject', '-e', 'default', '-o', 'yaml'])
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self.test_case_props['project_A'],
                self.test_case_props['project_B']
            ],
            matcher=self._match_project
        )
    
    def test_get_all_as_json(self):
        result = self.cli_runner.invoke(cli, ['get', 'behaviourproject', '-e', 'default', '-o', 'json'])
        loaded_output = json.loads(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self.test_case_props['project_A'],
                self.test_case_props['project_B']
            ],
            matcher=self._match_project
        )

    def test_get_by_name_as_yaml(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'behaviourproject', self.test_case_props['project_A']['id'], '-e', 'default', '-o', 'yaml'
            ])
        loaded_output = yaml.safe_load(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['project_A']['name'])
        self.assertEqual(loaded_output['id'], self.test_case_props['project_A']['id'])
        self.assertEqual(loaded_output['description'], self.test_case_props['project_A']['description'])
    
    def test_get_by_name_as_json(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'behaviourproject', self.test_case_props['project_A']['id'], '-e', 'default', '-o', 'json'
            ])
        loaded_output = json.loads(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['project_A']['name'])
        self.assertEqual(loaded_output['id'], self.test_case_props['project_A']['id'])
        self.assertEqual(loaded_output['description'], self.test_case_props['project_A']['description'])
    
    def test_get_by_name_as_table(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'behaviourproject', self.test_case_props['project_A']['id'], '-e', 'default'
            ])
        table_format = TableFormat(table=Table(columns=default_columns))
        expected_output = table_format.convert_element(self.test_case_props['project_A'])
        self.assert_output(result, expected_output)
        
    def test_create_with_yaml_file(self):
        project_name = self.tester.exec_prepended_name('project-cmd-create-with-yaml')
        project = {
            'name': project_name,
            'description': 'Testing create cmds'
        }
        yml_file = self.tester.create_yaml_file('project-cmd-create-with.yaml', project)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'behaviourproject', '-e', 'default', '-f', yml_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {project_name}')
        api_get_result = self.tester.default_client.behaviour_projects.get(project_name)
        self.assertEqual(api_get_result['name'], project['name'])
        self.assertEqual(api_get_result['description'], project['description'])

    def test_create_with_json_file(self):
        project_name = self.tester.exec_prepended_name('project-cmd-create-with-json')
        project = {
            'name': project_name,
            'description': 'Testing create cmds'
        }
        json_file = self.tester.create_json_file('project-cmd-create-with.json', project)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'behaviourproject', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {project_name}')
        api_get_result = self.tester.default_client.behaviour_projects.get(project_name)
        self.assertEqual(api_get_result['name'], project['name'])
        self.assertEqual(api_get_result['description'], project['description'])

    def test_create_with_set(self):
        project_name = self.tester.exec_prepended_name('project-cmd-create-with-set')
        create_result = self.cli_runner.invoke(cli, [
            'create', 'behaviourproject', '-e', 'default', 
                        '--set', f'name={project_name}', 
                        '--set', f'description=Testing set'
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {project_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_projects.get(project_name)
        self.assertEqual(api_get_result['name'], project_name)
        self.assertEqual(api_get_result['description'], 'Testing set')

    def test_update_with_yaml_file(self):
        self.test_case_props['project_A']['description'] = 'Updated description for cmd testing with yaml'
        yml_file = self.tester.create_yaml_file('project-cmd-update-with.yaml', self.test_case_props['project_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'behaviourproject', '-e', 'default', '-f', yml_file
            ])
        project_name = self.test_case_props['project_A']['id']
        self.assert_output(update_result, f'Updated: {project_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_projects.get(project_name)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with yaml')

    def test_update_with_json_file(self):
        self.test_case_props['project_A']['description'] = 'Updated description for cmd testing with json'
        json_file = self.tester.create_json_file('project-cmd-update-with.json', self.test_case_props['project_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'behaviourproject', '-e', 'default', '-f', json_file
            ])
        project_name = self.test_case_props['project_A']['id']
        self.assert_output(update_result, f'Updated: {project_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_projects.get(project_name)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with json')

    def test_update_with_set(self):
        project_name = self.test_case_props['project_A']['id']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'behaviourproject', '-e', 'default', project_name, '--set', 'description=Updated descriptor for cmd testing with --set'
            ])
        self.assert_output(update_result, f'Updated: {project_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_projects.get(project_name)
        self.assertEqual(api_get_result['description'], 'Updated descriptor for cmd testing with --set')

    def test_update_with_name_and_file(self):
        project_name = self.test_case_props['project_A']['id']
        project = self.test_case_props['project_A'].copy()
        project['name'] = None
        project['description'] = 'Updated descriptor for cmd testing with file' 
        yml_file = self.tester.create_yaml_file('project-cmd-update-with-name-and-file.yaml', project)
        update_result = self.cli_runner.invoke(cli, [
            'update', 'behaviourproject', '-e', 'default', project_name, '-f', yml_file
            ])
        self.assert_output(update_result, f'Updated: {project_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_projects.get(project_name)
        self.assertEqual(api_get_result['description'], 'Updated descriptor for cmd testing with file')

    def test_update_with_set_and_no_name_fails(self):
        update_result = self.cli_runner.invoke(cli, [
            'update', 'behaviourproject', '-e', 'default',  '--set', 'description=testing'
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update behaviourproject [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli update behaviourproject --help\' for help.'
        expected_output += '\n\nError: Must identify the target by specifying the "name" parameter or by including the "name" attribute in the given object/file'
        self.assert_output(update_result, expected_output)

    def test_delete_with_yaml_file(self):
        project_name = self.tester.exec_prepended_name('project-cmd-delete-with-yaml')
        project = {
            'name': project_name,
            'description': 'Testing cmds'
        }
        yml_file = self.tester.create_yaml_file('project-cmd-delete-with.yaml', project)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'behaviourproject', '-e', 'default', '-f', yml_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {project_name}')
        project['id'] = project_name
        yml_file = self.tester.create_yaml_file('project-cmd-delete-with.yaml', project)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'behaviourproject', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(delete_result, f'Removed: {project_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.behaviour_projects.get(project_name)
            self.fail('Project should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Project failed with an unexpected error: {str(e)}')
    
    def test_delete_with_json_file(self):
        project_name = self.tester.exec_prepended_name('project-cmd-delete-with-json')
        project = {
            'name': project_name,
            'description': 'Testing cmds'
        }
        json_file = self.tester.create_json_file('project-cmd-delete-with.json', project)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'behaviourproject', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {project_name}')
        project['id'] = project_name
        json_file = self.tester.create_json_file('project-cmd-delete-with.json', project)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'behaviourproject', '-e', 'default', '-f', json_file
            ])
        self.assert_output(delete_result, f'Removed: {project_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.behaviour_projects.get(project_name)
            self.fail('Project should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Project failed with an unexpected error: {str(e)}')
    
    def test_delete_with_id(self):
        project_name = self.tester.exec_prepended_name('project-cmd-delete-with-json')
        project = {
            'name': project_name,
            'description': 'Testing cmds'
        }
        json_file = self.tester.create_json_file('project-cmd-delete-with.json', project)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'behaviourproject', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {project_name}')
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'behaviourproject', '-e', 'default', project_name
            ])
        self.assert_output(delete_result, f'Removed: {project_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.behaviour_projects.get(project_name)
            self.fail('Project should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Project failed with an unexpected error: {str(e)}')
    
    def test_delete_with_no_name_or_file_fails(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'behaviourproject', '-e', 'default'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete behaviourproject [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli delete behaviourproject --help\' for help.'
        expected_output += '\n\nError: Must identify the target by specifying the "name" parameter or by including the "name" attribute in the given object/file'
        self.assert_output(delete_result, expected_output)
    
    def test_delete_with_ignore_missing(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'behaviourproject', '-e', 'default', 'NonExistentObj', '--ignore-missing'
            ])
        self.assert_no_errors(delete_result)
        self.assert_output(delete_result, f'(Ignored) Entity of type \'Project\' could not be found matching: id=NonExistentObj')