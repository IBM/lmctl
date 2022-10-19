from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat, Table
from lmctl.client import TNCOClientHttpError
from lmctl.cli.commands.assemblies import default_columns
from lmctl.client.models import CreateAssemblyIntent, DeleteAssemblyIntent
import yaml
import os
import json
import time
import unittest

class TestAssemblies(CLIIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        cls.test_case_props['assembly_tidyup_bucket'] = []
        ## Add deployment location
        cls.test_case_props['deployment_location'] = tester.default_client.deployment_locations.create({
            'name': tester.exec_prepended_name('assembly-cmds'),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        })
        ## Upload Resource package
        res_pkg_path = tester.tmp_file('dummy_resource.zip')
        tester.build_resource_package_from(tester.test_file('dummy_resource'), res_pkg_path, suffix='assembly-cmds')
        cls.test_case_props['res_pkg_id'] = tester.default_client.resource_packages.create(res_pkg_path)
        ## Get Resource descriptor 
        cls.test_case_props['resource_descriptor'] = tester.load_descriptor_from(tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='assembly-cmds')
        ## Add Assembly descriptor
        cls.test_case_props['assembly_descriptor'] = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='assembly-cmds')
        tester.default_client.descriptors.create(cls.test_case_props['assembly_descriptor'])
        ## Create an Assembly
        cls.test_case_props['assembly_A_name'] = tester.exec_prepended_name('assembly-cmds-A')
        create_A_process_id = tester.default_client.assemblies.intent_create(
            CreateAssemblyIntent(
                assembly_name=cls.test_case_props['assembly_A_name'],
                descriptor_name=cls.test_case_props['assembly_descriptor']['name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': cls.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
            )
        )
        create_A_process = tester.default_client.processes.get(create_A_process_id)
        cls.test_case_props['assembly_A_id'] = create_A_process.get('assemblyId')
        cls.test_case_props['assembly_B_name'] = tester.exec_prepended_name('assembly-cmds-B')
        create_B_process_id = tester.default_client.assemblies.intent_create(
            CreateAssemblyIntent(
                assembly_name=cls.test_case_props['assembly_B_name'],
                descriptor_name=cls.test_case_props['assembly_descriptor']['name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': cls.test_case_props['deployment_location']['name'],
                    'dummyProp': 'B'
                }
            )
        )
        create_B_process = tester.default_client.processes.get(create_B_process_id)
        cls.test_case_props['assembly_B_id'] = create_B_process.get('assemblyId')
        tester.wait_until(cls._build_check_process_success(tester), create_A_process_id)
        tester.wait_until(cls._build_check_process_success(tester), create_B_process_id)
    
    @classmethod
    def after_test_case(cls, tester):
        delete_A_process_id =  tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=cls.test_case_props['assembly_A_name'])
        )
        delete_B_process_id =  tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=cls.test_case_props['assembly_B_name'])
        )
        tester.wait_until(cls._build_check_process_success(tester), delete_A_process_id)
        tester.wait_until(cls._build_check_process_success(tester), delete_B_process_id)
        for name in cls.test_case_props['assembly_tidyup_bucket']:
            delete_process_id =  tester.default_client.assemblies.intent_delete(
                DeleteAssemblyIntent(assembly_name=name)
            )
            tester.wait_until(cls._build_check_process_success(tester), delete_process_id)
        time.sleep(1.5)
        tester.default_client.resource_packages.delete(cls.test_case_props['res_pkg_id'])
        tester.default_client.descriptors.delete(cls.test_case_props['assembly_descriptor']['name'])
        tester.default_client.descriptors.delete(cls.test_case_props['resource_descriptor']['name'])
        tester.default_client.deployment_locations.delete(cls.test_case_props['deployment_location']['name'])
    
    def _match_assembly(self, x: Dict, y: Dict):
        if x.get('id') != y.get('id'):
            return False
        if x.get('name') != y.get('name'):
            return False
        return True

    def test_get_by_name_as_yaml(self):
        result = self.cli_runner.invoke(cli, 
            ['get', 'assembly', '-e', 'default', self.test_case_props['assembly_A_name'], '-o', 'yaml']
        )
        loaded_output = yaml.safe_load(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['assembly_A_name'])
        self.assertEqual(loaded_output['id'], self.test_case_props['assembly_A_id'])
    
    def test_get_by_name_as_json(self):
        result = self.cli_runner.invoke(cli, 
            ['get', 'assembly', '-e', 'default', self.test_case_props['assembly_A_name'], '-o', 'json']
        )
        loaded_output = json.loads(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['assembly_A_name'])
        self.assertEqual(loaded_output['id'], self.test_case_props['assembly_A_id'])
    
    def test_get_by_name_as_table(self):
        target_assembly = self.tester.default_client.assemblies.get_by_name(self.test_case_props['assembly_A_name'])
        result = self.cli_runner.invoke(cli, 
            ['get', 'assembly', '-e', 'default', self.test_case_props['assembly_A_name']]
        )
        table_format = TableFormat(table=Table(columns=default_columns))
        expected_output = table_format.convert_element(target_assembly)
        self.assert_output(result, expected_output)

    def test_get_by_id(self):
        target_assembly = self.tester.default_client.assemblies.get(self.test_case_props['assembly_A_id'])
        result = self.cli_runner.invoke(cli, 
            ['get', 'assembly', '-e', 'default', '--id', self.test_case_props['assembly_A_id']]
        )
        table_format = TableFormat(table=Table(columns=default_columns))
        expected_output = table_format.convert_element(target_assembly)
        self.assert_output(result, expected_output)

    def test_get_by_name_contains(self):
        target_assembly_A = self.tester.default_client.assemblies.get(self.test_case_props['assembly_A_id'])
        target_assembly_B = self.tester.default_client.assemblies.get(self.test_case_props['assembly_B_id'])
        result = self.cli_runner.invoke(cli, 
            ['get', 'assembly', '-e', 'default', '--name-contains', 'assembly-cmds', '-o', 'yaml']
        )
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                target_assembly_A,
                target_assembly_B
            ],
            matcher=self._match_assembly
        )
    
    def test_get_topN(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-create-for-topN')
        create_process_id = self.tester.default_client.assemblies.intent_create(
            CreateAssemblyIntent(
                assembly_name=assembly_name,
                descriptor_name=self.test_case_props['assembly_descriptor']['name'],
                intended_state='Active',
                properties={
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'B'
                }
            )
        )
        create_process = self.tester.default_client.processes.get(create_process_id)
        assembly_id = create_process.get('assemblyId')
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        target_assembly = self.tester.default_client.assemblies.get(assembly_id)
        result = self.cli_runner.invoke(cli, 
            ['get', 'assembly', '-e', 'default', '--topN', '-o', 'yaml']
        )
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                target_assembly
            ],
            matcher=self._match_assembly
        )
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)

    def test_get_with_id_and_name_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assembly', 'SomeName', '--id', 'SomeId', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli get assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "--id" with "name" as they are mutually exclusive'
        self.assert_output(result, expected_output)
    
    def test_get_with_id_and_name_contains_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assembly', '--id', 'SomeId', '--name-contains', 'SomeName', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli get assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "--name-contains" with "--id" as they are mutually exclusive'
        self.assert_output(result, expected_output)
    
    def test_get_with_id_and_topN_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assembly', '--id', 'SomeId', '--topN', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli get assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "--topN" with "--id" as they are mutually exclusive'
        self.assert_output(result, expected_output)
    
    def test_get_with_name_and_name_contains_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assembly', 'SomeName', '--name-contains', 'SomeName', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli get assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "--name-contains" with "name" as they are mutually exclusive'
        self.assert_output(result, expected_output)
    
    def test_get_with_name_and_topN_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assembly', 'SomeName', '--topN', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli get assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "--topN" with "name" as they are mutually exclusive'
        self.assert_output(result, expected_output)
    
    def test_get_with_name_contains_and_topN_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assembly', '--name-contains', 'SomeName', '--topN', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli get assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "--topN" with "--name-contains" as they are mutually exclusive'
        self.assert_output(result, expected_output)
    
    def test_get_without_id_or_name_or_name_contains_or_topN_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'assembly', '-e', 'default'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli get assembly --help\' for help.'
        expected_output += '\n\nError: Must identify the target by specifying one parameter from ["name", "--id", "--name-contains", "--topN"] or by including one of the following attributes ["assemblyName", "assemblyId"] in the given object/file'
        self.assert_output(result, expected_output)
    
    def test_create_with_yaml_file(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-create-with-yaml')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        yml_file = self.tester.create_yaml_file('assembly-cmd-create-with.yaml', assembly)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'assembly', '-e', 'default', '-f', yml_file
            ])
        self.assertTrue(create_result.output.startswith('Accepted - Process: '))
        process_id = create_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_create_with_json_file(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-create-with-json')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        json_file = self.tester.create_yaml_file('assembly-cmd-create-with.json', assembly)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'assembly', '-e', 'default', '-f', json_file
            ])
        self.assertTrue(create_result.output.startswith('Accepted - Process: '))
        process_id = create_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_create_with_set(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-create-with-set')
        descriptor_name = self.test_case_props['assembly_descriptor']['name']
        intended_state = 'Active'
        deployment_location = self.test_case_props['deployment_location']['name']
        create_result = self.cli_runner.invoke(cli, [
            'create', 'assembly', '-e', 'default', 
                        '--set', f'assemblyName={assembly_name}', 
                        '--set', f'descriptorName={descriptor_name}', 
                        '--set', f'intendedState={intended_state}',
                        '--prop', f'deploymentLocation={deployment_location}',
                        '--prop', 'resourceManager=brent',
                        '--prop', 'dummyProp=A'
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Accepted - Process: '))
        process_id = create_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_create_with_file_and_set_merges(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-create-with-file-and-set')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        yml_file = self.tester.create_yaml_file('assembly-cmd-create-with-file-and-set.yaml', assembly)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'assembly', '-e', 'default', '-f', yml_file, '--set', 'intendedState=Inactive'
            ])

        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Accepted - Process: '))
        process_id = create_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)
        #Get the Assembly and confirm the update
        get_api_result = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertEqual(get_api_result['state'], 'Inactive')
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_create_with_file_and_prop_merges(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-create-with-file-and-prop')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        yml_file = self.tester.create_yaml_file('assembly-cmd-create-with-file-and-prop.yaml', assembly)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'assembly', '-e', 'default', '-f', yml_file, '--prop', 'dummyProp=B'
            ])
        self.assert_no_errors(create_result)
        self.assertTrue(create_result.output.startswith('Accepted - Process: '))
        process_id = create_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)
        #Get the Assembly and confirm the update
        get_api_result = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertCountEqual(get_api_result['properties'], [
            {'name': 'resourceManager', 'type': 'string', 'value': 'brent'},
            {'name': 'deploymentLocation', 'type': 'string', 'value': self.test_case_props['deployment_location']['name']},
            {'name': 'dummyProp', 'type': 'string', 'value': 'B'}
        ])
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    
    def test_update_with_yaml_file(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-update-with-yaml')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        assembly['properties']['dummyProp'] = 'B'
        yml_file = self.tester.create_yaml_file('assembly-cmd-update-with.yaml', assembly)
        update_result = self.cli_runner.invoke(cli, [
            'update', 'assembly', '-e', 'default', '-f', yml_file
            ])
        self.assertTrue(update_result.output.startswith('Accepted - Process: '))
        update_process_id = update_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), update_process_id)
        #Get the Assembly and confirm the update
        get_api_result = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertCountEqual(get_api_result['properties'], [
            {'name': 'resourceManager', 'type': 'string', 'value': 'brent'},
            {'name': 'deploymentLocation', 'type': 'string', 'value': self.test_case_props['deployment_location']['name']},
            {'name': 'dummyProp', 'type': 'string', 'value': 'B'}
        ])
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_update_with_json_file(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-update-with-json')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        assembly['properties']['dummyProp'] = 'B'
        json_file = self.tester.create_json_file('assembly-cmd-update-with.json', assembly)
        update_result = self.cli_runner.invoke(cli, [
            'update', 'assembly', '-e', 'default', '-f', json_file
            ])
        self.assertTrue(update_result.output.startswith('Accepted - Process: '))
        update_process_id = update_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), update_process_id)
        #Get the Assembly and confirm the update
        get_api_result = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertCountEqual(get_api_result['properties'], [
            {'name': 'resourceManager', 'type': 'string', 'value': 'brent'},
            {'name': 'deploymentLocation', 'type': 'string', 'value': self.test_case_props['deployment_location']['name']},
            {'name': 'dummyProp', 'type': 'string', 'value': 'B'}
        ])
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_update_with_name_and_setprop(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-update-with-name-and-set')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        assembly['properties']['dummyProp'] = 'B'
        update_result = self.cli_runner.invoke(cli, [
            'update', 'assembly', '-e', 'default', assembly_name, '--prop', 'dummyProp=B'
            ])
        self.assertTrue(update_result.output.startswith('Accepted - Process: '))
        update_process_id = update_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), update_process_id)
        #Get the Assembly and confirm the update
        get_api_result = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertCountEqual(get_api_result['properties'], [
            {'name': 'resourceManager', 'type': 'string', 'value': 'brent'},
            {'name': 'deploymentLocation', 'type': 'string', 'value': self.test_case_props['deployment_location']['name']},
            {'name': 'dummyProp', 'type': 'string', 'value': 'B'}
        ])
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    @unittest.skip("Currently can --set anything mutable on update")
    def test_update_with_file_and_set_merges(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-update-with-file-and-set')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        assembly['properties']['dummyProp'] = 'B'
        yml_file = self.tester.create_yaml_file('assembly-cmd-update-with-file-and-set.yaml', assembly)
        update_result = self.cli_runner.invoke(cli, [
            'update', 'assembly', '-e', 'default', '-f', yml_file, '--set', 'dummyProp=C'
            ])
        update_process_id = update_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), update_process_id)
        #Get the Assembly and confirm the update
        get_api_result = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertCountEqual(get_api_result['properties'], [
            {'name': 'resourceManager', 'type': 'string', 'value': 'brent'},
            {'name': 'deploymentLocation', 'type': 'string', 'value': self.test_case_props['deployment_location']['name']},
            {'name': 'dummyProp', 'type': 'string', 'value': 'C'}
        ])
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_update_with_file_and_prop_merges(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-update-with-file-and-prop')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        assembly['properties']['dummyProp'] = 'B'
        yml_file = self.tester.create_yaml_file('assembly-cmd-update-with-file-and-set.yaml', assembly)
        update_result = self.cli_runner.invoke(cli, [
            'update', 'assembly', '-e', 'default', '-f', yml_file, '--prop', 'dummyProp=C'
            ])
        update_process_id = update_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), update_process_id)
        #Get the Assembly and confirm the update
        get_api_result = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertCountEqual(get_api_result['properties'], [
            {'name': 'resourceManager', 'type': 'string', 'value': 'brent'},
            {'name': 'deploymentLocation', 'type': 'string', 'value': self.test_case_props['deployment_location']['name']},
            {'name': 'dummyProp', 'type': 'string', 'value': 'C'}
        ])
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_delete_with_name(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-delete-with-name')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assembly', '-e', 'default', assembly_name
            ])
        self.assert_no_errors(delete_result)
        self.assertTrue(delete_result.output.startswith('Accepted - Process: '))
        delete_process_id = delete_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_delete_with_id(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-delete-with-id')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        process = self.tester.default_client.processes.get(create_process_id)
        assembly_id = process.get('assemblyId')
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assembly', '-e', 'default', '--id', assembly_id
            ])
        self.assert_no_errors(delete_result)
        self.assertTrue(delete_result.output.startswith('Accepted - Process: '))
        delete_process_id = delete_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_delete_with_name_and_id_fails(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assembly', '-e', 'default', 'SomeName', '--id', 'SomeId'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli delete assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "--id" with "name" as they are mutually exclusive'
        self.assert_output(delete_result, expected_output)
    
    def test_delete_with_yaml_file(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-delete-with-yaml')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        yml_file = self.tester.create_yaml_file('assembly-cmd-delete-with.yaml', assembly)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assembly', '-e', 'default', '-f', yml_file
            ])
        self.assertTrue(delete_result.output.startswith('Accepted - Process: '))
        delete_process_id = delete_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_delete_with_json_file(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-delete-with-json')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        json_file = self.tester.create_json_file('assembly-cmd-delete-with.json', assembly)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assembly', '-e', 'default', '-f', json_file
            ])
        self.assertTrue(delete_result.output.startswith('Accepted - Process: '))
        delete_process_id = delete_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_delete_with_file_including_id(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-delete-with-id-in-file')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        create_process = self.tester.default_client.processes.get(create_process_id)
        assembly_id = create_process.get('assemblyId')
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        assembly['assemblyId'] = assembly_id
        del assembly['assemblyName']
        yml_file = self.tester.create_yaml_file('assembly-cmd-delete-with-id-in-file.yaml', assembly)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assembly', '-e', 'default', '-f', yml_file
            ])
        self.assertTrue(delete_result.output.startswith('Accepted - Process: '))
        delete_process_id = delete_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)

    def test_delete_with_id_and_file_fails(self):
        assembly = {
            'assemblyId': '123',
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        yml_file = self.tester.create_yaml_file('assembly-cmd-delete-id-and-file.yaml', assembly)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assembly', '-e', 'default', '-f', yml_file, '--id', 'SomeOtherId'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli delete assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "-f,--file" with "--id" as they are mutually exclusive'
        self.assert_output(delete_result, expected_output)
    
    def test_delete_with_name_and_file(self):
        assembly = {
            'assemblyName': 'Test',
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        yml_file = self.tester.create_yaml_file('assembly-cmd-delete-name-and-file.yaml', assembly)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'assembly', '-e', 'default', '-f', yml_file, 'SomeOtherName'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli delete assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "-f,--file" with "name" as they are mutually exclusive'
        self.assert_output(delete_result, expected_output)
    
    def test_changestate_with_name(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-changestate-with-name')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Inactive',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        changestate_result = self.cli_runner.invoke(cli, [
            'changestate', 'assembly', '-e', 'default', assembly_name, '--state', 'Active'
            ])
        self.assert_no_errors(changestate_result)
        self.assertTrue(changestate_result.output.startswith('Accepted - Process: '))
        changestate_process_id = changestate_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), changestate_process_id)
        assembly = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertEqual(assembly['state'], 'Active')
        delete_process_id = self.tester.default_client.assemblies.intent_delete(DeleteAssemblyIntent(assembly_name=assembly_name))
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_changestate_with_id(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-changestate-with-id')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Inactive',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        process = self.tester.default_client.processes.get(create_process_id)
        assembly_id = process.get('assemblyId')
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        changestate_result = self.cli_runner.invoke(cli, [
            'changestate', 'assembly', '-e', 'default', '--id', assembly_id, '--state', 'Active'
            ])
        self.assert_no_errors(changestate_result)
        self.assertTrue(changestate_result.output.startswith('Accepted - Process: '))
        changestate_process_id = changestate_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), changestate_process_id)
        assembly = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertEqual(assembly['state'], 'Active')
        delete_process_id = self.tester.default_client.assemblies.intent_delete(DeleteAssemblyIntent(assembly_name=assembly_name))
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_changestate_with_name_and_id_fails(self):
        changestate_result = self.cli_runner.invoke(cli, [
            'changestate', 'assembly', '-e', 'default', 'SomeName', '--id', 'SomeId', '--state', 'Active'
            ])
        self.assert_has_system_exit(changestate_result)
        expected_output = 'Usage: cli changestate assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli changestate assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "--id" with "name" as they are mutually exclusive'
        self.assert_output(changestate_result, expected_output)
    
    def test_changestate_with_yaml_file(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-changestate-with-yaml')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Inactive',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        assembly['intendedState'] = 'Active'
        yml_file = self.tester.create_yaml_file('assembly-cmd-changestate-with.yaml', assembly)
        changestate_result = self.cli_runner.invoke(cli, [
            'changestate', 'assembly', '-e', 'default', '-f', yml_file
            ])
        self.assert_no_errors(changestate_result)
        self.assertTrue(changestate_result.output.startswith('Accepted - Process: '))
        changestate_process_id = changestate_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), changestate_process_id)
        assembly = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertEqual(assembly['state'], 'Active')
        delete_process_id = self.tester.default_client.assemblies.intent_delete(DeleteAssemblyIntent(assembly_name=assembly_name))
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_changestate_with_json_file(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-changestate-with-json')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Inactive',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        assembly['intendedState'] = 'Active'
        json_file = self.tester.create_json_file('assembly-cmd-changestate-with.json', assembly)
        changestate_result = self.cli_runner.invoke(cli, [
            'changestate', 'assembly', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(changestate_result)
        self.assertTrue(changestate_result.output.startswith('Accepted - Process: '))
        changestate_process_id = changestate_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), changestate_process_id)
        assembly = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertEqual(assembly['state'], 'Active')
        delete_process_id = self.tester.default_client.assemblies.intent_delete(DeleteAssemblyIntent(assembly_name=assembly_name))
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_changestate_with_file_including_id(self):
        assembly_name = self.tester.exec_prepended_name('assembly-cmd-changestate-with-id-in-file')
        assembly = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Inactive',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id = self.tester.default_client.assemblies.intent_create(assembly)
        create_process = self.tester.default_client.processes.get(create_process_id)
        assembly_id = create_process.get('assemblyId')
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        assembly['assemblyId'] = assembly_id
        assembly['intendedState'] = 'Active'
        del assembly['assemblyName']
        yml_file = self.tester.create_yaml_file('assembly-cmd-changestate-with-id-in-file.yaml', assembly)
        changestate_result = self.cli_runner.invoke(cli, [
            'changestate', 'assembly', '-e', 'default', '-f', yml_file
            ])
        self.assert_no_errors(changestate_result)
        self.assertTrue(changestate_result.output.startswith('Accepted - Process: '))
        changestate_process_id = changestate_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), changestate_process_id)
        assembly = self.tester.default_client.assemblies.get_by_name(assembly_name)
        self.assertEqual(assembly['state'], 'Active')
        delete_process_id = self.tester.default_client.assemblies.intent_delete(DeleteAssemblyIntent(assembly_name=assembly_name))
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)

    def test_changestate_with_id_and_file_fails(self):
        assembly = {
            'assemblyId': '123',
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        yml_file = self.tester.create_yaml_file('assembly-cmd-changestate-id-and-file.yaml', assembly)
        changestate_result = self.cli_runner.invoke(cli, [
            'changestate', 'assembly', '-e', 'default', '-f', yml_file, '--id', 'SomeOtherId'
            ])
        self.assert_has_system_exit(changestate_result)
        expected_output = 'Usage: cli changestate assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli changestate assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "-f,--file" with "--id" as they are mutually exclusive'
        self.assert_output(changestate_result, expected_output)
    
    def test_changestate_with_name_and_file_fails(self):
        assembly = {
            'assemblyName': 'Test',
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        yml_file = self.tester.create_yaml_file('assembly-cmd-changestate-id-and-file.yaml', assembly)
        changestate_result = self.cli_runner.invoke(cli, [
            'changestate', 'assembly', '-e', 'default', '-f', yml_file, 'SomeOtherName'
            ])
        self.assert_has_system_exit(changestate_result)
        expected_output = 'Usage: cli changestate assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli changestate assembly --help\' for help.'
        expected_output += '\n\nError: Cannot use "-f,--file" with "name" as they are mutually exclusive'
        self.assert_output(changestate_result, expected_output)
        
    def test_changestate_with_no_state_fails(self):
        assembly = {
            'assemblyName': 'Test',
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        yml_file = self.tester.create_yaml_file('assembly-cmd-changestate-with-no-state.yaml', assembly)
        changestate_result = self.cli_runner.invoke(cli, [
            'changestate', 'assembly', '-e', 'default', '-f', yml_file
            ])
        self.assert_has_system_exit(changestate_result)
        expected_output = 'Usage: cli changestate assembly [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli changestate assembly --help\' for help.'
        expected_output += '\n\nError: Must set "--intended-state, --state" option or include "intendedState" attribute in content of file passed to "-f, --file" option to change Assembly state'
        self.assert_output(changestate_result, expected_output)
    