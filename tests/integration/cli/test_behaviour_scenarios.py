from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat
from lmctl.client import TNCOClientHttpError
from lmctl.client.models import CreateAssemblyIntent, DeleteAssemblyIntent
from lmctl.cli.commands.targets.behaviour_scenarios import ScenarioTable
import yaml
import json
import time
import os

class TestBehaviourScenarios(CLIIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add an Assembly descriptor so a project is available
        assembly_descriptor = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='scenario-cmds')
        tester.default_client.descriptors.create(assembly_descriptor)
        cls.test_case_props['assembly_descriptor_name'] = assembly_descriptor['name']
        cls.test_case_props['project_name'] = assembly_descriptor['name']
        ## Add some Scenarios
        cls.test_case_props['scenario_A'] = tester.default_client.behaviour_scenarios.create({
            'name': tester.exec_prepended_name('scenario-cmds-A'),
            'projectId': cls.test_case_props['project_name'],
            'description': 'A test scenario'
        })
        cls.test_case_props['scenario_B'] = tester.default_client.behaviour_scenarios.create({
            'name': tester.exec_prepended_name('scenario-cmds-B'),
            'projectId': cls.test_case_props['project_name'],
            'description': 'A test scenario'
        })
        ## Scenario for testing exec request input 
        cls.test_case_props['input_scenario'] = tester.default_client.behaviour_scenarios.create({
            'name': tester.exec_prepended_name('scenario-cmds-exec-input'),
            'projectId': cls.test_case_props['project_name'],
            'assemblyActors': [
                {
                "instanceName": "InputAssembly",
                "initialState": "Active",
                "uninstallOnExit": True,
                "provided": True #Do not change
                }
            ]
        })
        ## Create an instance, needed for execution tests
        # Location needed
        cls.test_case_props['deployment_location_name'] = tester.exec_prepended_name('scenario-cmds')
        cls.test_case_props['deployment_location'] = tester.default_client.deployment_locations.create({
            'name': cls.test_case_props['deployment_location_name'],
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        })
        # Upload Resource package
        res_pkg_path = tester.tmp_file('dummy_resource.zip')
        tester.build_resource_package_from(tester.test_file('dummy_resource'), res_pkg_path, suffix='scenario-cmds')
        cls.test_case_props['res_pkg_id'] = tester.default_client.resource_packages.create(res_pkg_path)
        # Get Resource descriptor 
        resource_descriptor = tester.load_descriptor_from(tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='scenario-cmds')
        cls.test_case_props['resource_descriptor_name'] = resource_descriptor['name']
        # Create Assembly
        cls.test_case_props['assembly_name'] = tester.exec_prepended_name('scenario-cmds-A')
        create_process_id = tester.default_client.assemblies.intent_create(
            CreateAssemblyIntent(
                assembly_name=cls.test_case_props['assembly_name'],
                descriptor_name=cls.test_case_props['assembly_descriptor_name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': cls.test_case_props['deployment_location_name'],
                    'dummyProp': 'A'
                }
            )
        )
        tester.wait_until(cls._build_check_process_success(tester), create_process_id)

    @classmethod
    def after_test_case(cls, tester):
        delete_process_id =  tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=cls.test_case_props['assembly_name'])
        )
        tester.wait_until(cls._build_check_process_success(tester), delete_process_id)
        tester.default_client.descriptors.delete(cls.test_case_props['assembly_descriptor_name'])
        tester.default_client.deployment_locations.delete(cls.test_case_props['deployment_location_name'])
        tester.default_client.resource_packages.delete(cls.test_case_props['res_pkg_id'])
        tester.default_client.descriptors.delete(cls.test_case_props['resource_descriptor_name'])

    def _match_scenario(self, x: Dict, y: Dict):
        if x.get('id') != y.get('id'):
            return False
        if x.get('name') != y.get('name'):
            return False
        return True

    def test_get_all_as_yaml(self):
        result = self.cli_runner.invoke(cli, ['get', 'scenario', '-e', 'default', '--project', self.test_case_props['project_name'], '-o', 'yaml'])
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self.test_case_props['scenario_A'],
                self.test_case_props['scenario_B']
            ],
            matcher=self._match_scenario
        )
    
    def test_get_all_as_json(self):
        result = self.cli_runner.invoke(cli, ['get', 'scenario', '-e', 'default', '--project', self.test_case_props['project_name'], '-o', 'json'])
        loaded_output = json.loads(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self.test_case_props['scenario_A'],
                self.test_case_props['scenario_B']
            ],
            matcher=self._match_scenario
        )

    def test_get_by_id_as_yaml(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'scenario', self.test_case_props['scenario_A']['id'], '-e', 'default', '-o', 'yaml'
            ])
        loaded_output = yaml.safe_load(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['scenario_A']['name'])
        self.assertEqual(loaded_output['id'], self.test_case_props['scenario_A']['id'])
    
    def test_get_by_id_as_json(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'scenario', self.test_case_props['scenario_A']['id'], '-e', 'default', '-o', 'json'
            ])
        loaded_output = json.loads(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['scenario_A']['name'])
        self.assertEqual(loaded_output['id'], self.test_case_props['scenario_A']['id'])
    
    def test_get_by_id_as_table(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'scenario', self.test_case_props['scenario_A']['id'], '-e', 'default'
            ])
        table_format = TableFormat(table=ScenarioTable())
        expected_output = table_format.convert_element(self.test_case_props['scenario_A'])
        self.assert_output(result, expected_output)

    def test_get_with_id_and_project_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'scenario', 'SomeId', '--project', 'SomeProject', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get scenario [OPTIONS] [ID]'
        expected_output += '\nTry \'cli get scenario --help\' for help.'
        expected_output += '\n\nError: Do not use "ID" argument when using the "--project" option'
        self.assert_output(result, expected_output)
    
    def test_get_without_id_or_project_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'scenario', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get scenario [OPTIONS] [ID]'
        expected_output += '\nTry \'cli get scenario --help\' for help.'
        expected_output += '\n\nError: Must set either "ID" argument or "--project" option'
        self.assert_output(result, expected_output)

    def test_create_with_yaml_file(self):
        scenario_name = self.tester.exec_prepended_name('scenario-cmd-create-with-yaml')
        scenario = {
            'name': scenario_name,
            'projectId': self.test_case_props['project_name'],
            'description': 'Just testing'
        }
        yml_file = self.tester.create_yaml_file('scenario-cmd-create-with.yaml', scenario)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'scenario', '-e', 'default', '-f', yml_file
            ])
        self.assertTrue(create_result.output.startswith('Created: '))
        scenario_id = create_result.output[len('Created: ')-1:].strip()
        api_get_result = self.tester.default_client.behaviour_scenarios.get(scenario_id)
        self.assertEqual(api_get_result['name'], scenario['name'])
        self.assertEqual(api_get_result['projectId'], scenario['projectId'])
        self.assertEqual(api_get_result['description'], scenario['description'])

    def test_create_with_json_file(self):
        scenario_name = self.tester.exec_prepended_name('scenario-cmd-create-with-json')
        scenario = {
            'name': scenario_name,
            'projectId': self.test_case_props['project_name'],
            'description': 'Just testing'
        }
        json_file = self.tester.create_json_file('scenario-cmd-create-with.json', scenario)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'scenario', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        scenario_id = create_result.output[len('Created: ')-1:].strip()
        api_get_result = self.tester.default_client.behaviour_scenarios.get(scenario_id)
        self.assertEqual(api_get_result['name'], scenario['name'])
        self.assertEqual(api_get_result['projectId'], scenario['projectId'])
        self.assertEqual(api_get_result['description'], scenario['description'])

    def test_create_with_set(self):
        scenario_name = self.tester.exec_prepended_name('scenario-cmd-create-with-set')
        project_id = self.test_case_props['project_name']
        create_result = self.cli_runner.invoke(cli, [
            'create', 'scenario', '-e', 'default', 
                        '--set', f'name={scenario_name}', 
                        '--set', f'projectId={project_id}', 
                        '--set', f'description=Just testing'
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        scenario_id = create_result.output[len('Created: ')-1:].strip()
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_scenarios.get(scenario_id)
        self.assertEqual(api_get_result['name'], scenario_name)
        self.assertEqual(api_get_result['projectId'], project_id)
        self.assertEqual(api_get_result['description'], 'Just testing')

    def test_update_with_yaml_file(self):
        self.test_case_props['scenario_A']['description'] = 'Updated description for cmd testing with yaml'
        yml_file = self.tester.create_yaml_file('scenario-cmd-update-with.yaml', self.test_case_props['scenario_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'scenario', '-e', 'default', '-f', yml_file
            ])
        scenario_id = self.test_case_props['scenario_A']['id']
        self.assert_output(update_result, f'Updated: {scenario_id}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_scenarios.get(scenario_id)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with yaml')

    def test_update_with_json_file(self):
        self.test_case_props['scenario_A']['description'] = 'Updated description for cmd testing with json'
        json_file = self.tester.create_json_file('scenario-cmd-update-with.json', self.test_case_props['scenario_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'scenario', '-e', 'default', '-f', json_file
            ])
        scenario_id = self.test_case_props['scenario_A']['id']
        self.assert_output(update_result, f'Updated: {scenario_id}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_scenarios.get(scenario_id)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with json')

    def test_update_with_set(self):
        scenario_id = self.test_case_props['scenario_A']['id']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'scenario', '-e', 'default', scenario_id, '--set', 'description=Updated descriptor for cmd testing with --set'
            ])
        self.assert_output(update_result, f'Updated: {scenario_id}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_scenarios.get(scenario_id)
        self.assertEqual(api_get_result['description'], 'Updated descriptor for cmd testing with --set')

    def test_update_with_name_and_file_fails(self):
        yml_file = self.tester.create_yaml_file('scenario-cmd-update-with-name-and-file-fails.yaml', self.test_case_props['scenario_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'scenario', '-e', 'default', 'SomeName', '-f', yml_file
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update scenario [OPTIONS] [ID]'
        expected_output += '\nTry \'cli update scenario --help\' for help.'
        expected_output += '\n\nError: Do not use "ID" argument when using "-f, --file" option'
        self.assert_output(update_result, expected_output)

    def test_update_with_set_and_no_name_fails(self):
        update_result = self.cli_runner.invoke(cli, [
            'update', 'scenario', '-e', 'default',  '--set', 'description=testing'
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update scenario [OPTIONS] [ID]'
        expected_output += '\nTry \'cli update scenario --help\' for help.'
        expected_output += '\n\nError: Must set "ID" argument when no "-f, --file" option specified'
        self.assert_output(update_result, expected_output)

    def test_delete_with_yaml_file(self):
        scenario_name = self.tester.exec_prepended_name('scenario-cmd-delete-with-yaml')
        scenario = {
            'name': scenario_name,
            'projectId': self.test_case_props['project_name']
        }
        yml_file = self.tester.create_yaml_file('scenario-cmd-delete-with.yaml', scenario)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'scenario', '-e', 'default', '-f', yml_file
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        scenario_id = create_result.output[len('Created: ')-1:].strip()
        scenario['id'] = scenario_id
        yml_file = self.tester.create_yaml_file('scenario-cmd-delete-with.yaml', scenario)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'scenario', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(delete_result, f'Removed: {scenario_id}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.behaviour_scenarios.get(scenario_id)
            self.fail('Scenario should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Scenario failed with an unexpected error: {str(e)}')
    
    def test_delete_with_json_file(self):
        scenario_name = self.tester.exec_prepended_name('scenario-cmd-delete-with-json')
        scenario = {
            'name': scenario_name,
            'projectId': self.test_case_props['project_name']
        }
        json_file = self.tester.create_json_file('scenario-cmd-delete-with.json', scenario)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'scenario', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        scenario_id = create_result.output[len('Created: ')-1:].strip()
        scenario['id'] = scenario_id
        json_file = self.tester.create_json_file('scenario-cmd-delete-with.json', scenario)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'scenario', '-e', 'default', '-f', json_file
            ])
        self.assert_output(delete_result, f'Removed: {scenario_id}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.behaviour_scenarios.get(scenario_id)
            self.fail('Scenario should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Scenario failed with an unexpected error: {str(e)}')
    
    def test_delete_with_id(self):
        scenario_name = self.tester.exec_prepended_name('scenario-cmd-delete-with-json')
        scenario = {
            'name': scenario_name,
            'projectId': self.test_case_props['project_name']
        }
        json_file = self.tester.create_json_file('scenario-cmd-delete-with.json', scenario)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'scenario', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Created: '))
        scenario_id = create_result.output[len('Created: ')-1:].strip()
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'scenario', '-e', 'default', scenario_id
            ])
        self.assert_output(delete_result, f'Removed: {scenario_id}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.behaviour_scenarios.get(scenario_id)
            self.fail('Scenario should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Scenario failed with an unexpected error: {str(e)}')
    
    def test_delete_with_no_name_or_file_fails(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'scenario', '-e', 'default'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete scenario [OPTIONS] [ID]'
        expected_output += '\nTry \'cli delete scenario --help\' for help.'
        expected_output += '\n\nError: Must set "ID" argument when no "-f, --file" option specified'
        self.assert_output(delete_result, expected_output)
    
    def test_delete_with_ignore_missing(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'scenario', '-e', 'default', 'NonExistentObj', '--ignore-missing'
            ])
        self.assert_no_errors(delete_result)
        self.assert_output(delete_result, f'No Scenario found with ID NonExistentObj (ignoring)')

    def test_execute_with_scenario_id_and_file_fails(self):
        scenario_name = self.tester.exec_prepended_name('scenario-cmd-execute-with-id-and-file')
        scenario = {
            'name': scenario_name,
            'projectId': self.test_case_props['project_name']
        }
        json_file = self.tester.create_json_file('scenario-cmd-execute-with-id-and-file', scenario)
        exec_result = self.cli_runner.invoke(cli, [
            'execute', 'scenario', '-e', 'default', '-f', json_file, 'SomeID'
            ])
        self.assert_has_system_exit(exec_result)
        expected_output = 'Usage: cli execute scenario [OPTIONS] [ID]'
        expected_output += '\nTry \'cli execute scenario --help\' for help.'
        expected_output += '\n\nError: Do not use "ID" argument when using "-f, --file" option'
        self.assert_output(exec_result, expected_output)

    def test_execute_with_scenario_file_missing_id_fails(self):
        scenario_name = self.tester.exec_prepended_name('scenario-cmd-execute-with-file-missing-id')
        scenario = {
            'name': scenario_name,
            'projectId': self.test_case_props['project_name']
        }
        json_file = self.tester.create_json_file('scenario-cmd-execute-with-file-missing-id', scenario)
        exec_result = self.cli_runner.invoke(cli, [
            'execute', 'scenario', '-e', 'default', '-f', json_file
            ])
        self.assert_has_system_exit(exec_result)
        expected_output = 'Usage: cli execute scenario [OPTIONS] [ID]'
        expected_output += '\nTry \'cli execute scenario --help\' for help.'
        expected_output += '\n\nError: Object from file does not contain an "id" attribute'
        self.assert_output(exec_result, expected_output)

    def test_execute_with_missing_file_or_id_fails(self):
        exec_result = self.cli_runner.invoke(cli, [
            'execute', 'scenario', '-e', 'default'
            ])
        self.assert_has_system_exit(exec_result)
        expected_output = 'Usage: cli execute scenario [OPTIONS] [ID]'
        expected_output += '\nTry \'cli execute scenario --help\' for help.'
        expected_output += '\n\nError: Must set "ID" argument when no "-f, --file" option specified'
        self.assert_output(exec_result, expected_output)

    def test_execute_with_id(self):
        exec_result = self.cli_runner.invoke(cli, [
            'execute', 'scenario', '-e', 'default', self.test_case_props['scenario_A']['id']
            ])
        self.assert_no_errors(exec_result)
        self.assertTrue(exec_result.output.startswith('Created Scenario Execution: '))
        exec_id = exec_result.output[len('Created Scenario Execution: ')-1:].strip()
        time.sleep(0.2)
        api_get_result = self.tester.default_client.behaviour_scenario_execs.get(exec_id)
        self.assertEqual(api_get_result['scenarioId'], self.test_case_props['scenario_A']['id'])
    
    def test_execute_with_yaml_file(self):
        json_file = self.tester.create_json_file('scenario-cmd-execute-with-yaml-file', self.test_case_props['scenario_A'])
        exec_result = self.cli_runner.invoke(cli, [
            'execute', 'scenario', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(exec_result)
        self.assertTrue(exec_result.output.startswith('Created Scenario Execution: '))
        exec_id = exec_result.output[len('Created Scenario Execution: ')-1:].strip()
        time.sleep(0.5)
        api_get_result = self.tester.default_client.behaviour_scenario_execs.get(exec_id)
        self.assertEqual(api_get_result['scenarioId'], self.test_case_props['scenario_A']['id'])
    
    def test_execute_with_json_file(self):
        json_file = self.tester.create_json_file('scenario-cmd-execute-with-json-file', self.test_case_props['scenario_B'])
        exec_result = self.cli_runner.invoke(cli, [
            'execute', 'scenario', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(exec_result)
        self.assertTrue(exec_result.output.startswith('Created Scenario Execution: '))
        exec_id = exec_result.output[len('Created Scenario Execution: ')-1:].strip()
        time.sleep(0.5)
        api_get_result = self.tester.default_client.behaviour_scenario_execs.get(exec_id)
        self.assertEqual(api_get_result['scenarioId'], self.test_case_props['scenario_B']['id'])
    
    def test_execute_with_yaml_request_file(self):
        yaml_req_file = self.tester.create_yaml_file('scenario-cmd-execute-with-yaml-req-file', {'assemblyName': self.test_case_props['assembly_name']})
        exec_result = self.cli_runner.invoke(cli, [
            'execute', 'scenario', '-e', 'default', self.test_case_props['input_scenario']['id'], '-r', yaml_req_file
            ])
        self.assert_no_errors(exec_result)
        self.assertTrue(exec_result.output.startswith('Created Scenario Execution: '))
        exec_id = exec_result.output[len('Created Scenario Execution: ')-1:].strip()
        time.sleep(0.5)
        api_get_result = self.tester.default_client.behaviour_scenario_execs.get(exec_id)
        self.assertEqual(api_get_result['scenarioId'], self.test_case_props['input_scenario']['id'])
        self.tester.wait_until(self._check_exec_success, exec_id)
    
    def test_execute_with_json_request_file(self):
        json_req_file = self.tester.create_json_file('scenario-cmd-execute-with-json-req-file', {'assemblyName': self.test_case_props['assembly_name']})
        exec_result = self.cli_runner.invoke(cli, [
            'execute', 'scenario', '-e', 'default', self.test_case_props['input_scenario']['id'], '-r', json_req_file
            ])
        self.assert_no_errors(exec_result)
        self.assertTrue(exec_result.output.startswith('Created Scenario Execution: '))
        exec_id = exec_result.output[len('Created Scenario Execution: ')-1:].strip()
        time.sleep(0.5)
        api_get_result = self.tester.default_client.behaviour_scenario_execs.get(exec_id)
        self.assertEqual(api_get_result['scenarioId'], self.test_case_props['input_scenario']['id'])
        self.tester.wait_until(self._check_exec_success, exec_id)
    
    def test_execute_with_set(self):
        assembly_name = self.test_case_props['assembly_name']
        exec_result = self.cli_runner.invoke(cli, [
            'execute', 'scenario', '-e', 'default', self.test_case_props['input_scenario']['id'], '--set', f'assemblyName={assembly_name}'
            ])
        self.assert_no_errors(exec_result)
        self.assertTrue(exec_result.output.startswith('Created Scenario Execution: '))
        exec_id = exec_result.output[len('Created Scenario Execution: ')-1:].strip()
        time.sleep(0.5)
        api_get_result = self.tester.default_client.behaviour_scenario_execs.get(exec_id)
        self.assertEqual(api_get_result['scenarioId'], self.test_case_props['input_scenario']['id'])
        self.tester.wait_until(self._check_exec_success, exec_id)
    
    def test_execute_with_set_and_request_file_fails(self):
        json_req_file = self.tester.create_json_file('scenario-cmd-execute-with-json-req-file', {'assemblyName': self.test_case_props['assembly_name']})
        exec_result = self.cli_runner.invoke(cli, [
            'execute', 'scenario', self.test_case_props['input_scenario']['id'], '-e', 'default', '-r', json_req_file, '--set', 'assemblyName=someAssembly'
            ])
        self.assert_has_system_exit(exec_result)
        expected_output = 'Usage: cli execute scenario [OPTIONS] [ID]'
        expected_output += '\nTry \'cli execute scenario --help\' for help.'
        expected_output += '\n\nError: Do not use "--set" option when using "-r, --request-file" option'
        self.assert_output(exec_result, expected_output)

    def _check_exec_success(self, execution_id: str) -> bool:
        execution = self.tester.default_client.behaviour_scenario_execs.get(execution_id)
        status = execution.get('status')
        if status in ['PASS']:
            return True
        elif status in ['ABORTED', 'FAIL']:
            reason = execution.get('error')
            self.fail(f'Execution failed with status {status}, reason: {reason}')
        else:
            return False