from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict, Tuple
from lmctl.cli.entry import cli
from lmctl.client import TNCOClientHttpError
from lmctl.client.models import CreateAssemblyIntent, DeleteAssemblyIntent
import yaml
import os
import json
import time

class TestIntents(CLIIntegrationTest):
  
    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add deployment location
        cls.test_case_props['deployment_location'] = tester.default_client.deployment_locations.create({
            'name': tester.exec_prepended_name('intent-cmds'),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        })
        ## Upload Resource package
        res_pkg_path = tester.tmp_file('dummy_resource.zip')
        tester.build_resource_package_from(tester.test_file('dummy_resource'), res_pkg_path, suffix='intent-cmds')
        cls.test_case_props['res_pkg_id'] = tester.default_client.resource_packages.create(res_pkg_path)
        ## Get Resource descriptor 
        cls.test_case_props['resource_descriptor'] = tester.load_descriptor_from(tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='intent-cmds')
        ## Add Assembly descriptor
        cls.test_case_props['assembly_descriptor'] = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='intent-cmds')
        tester.default_client.descriptors.create(cls.test_case_props['assembly_descriptor'])

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.deployment_locations.delete(cls.test_case_props['deployment_location']['name'])
        tester.default_client.resource_packages.delete(cls.test_case_props['res_pkg_id'])
        tester.default_client.descriptors.delete(cls.test_case_props['assembly_descriptor']['name'])
        tester.default_client.descriptors.delete(cls.test_case_props['resource_descriptor']['name'])
    
    def _confirm_process_success(self, cmd_result):
        self.assertTrue(cmd_result.output.startswith('Accepted - Process: '), msg=f'Output was actually: {cmd_result.output}')
        process_id = cmd_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)
        return process_id

    def _delete_and_wait(self, assembly_name: str):
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_create_with_yaml_file(self):
        assembly_name = self.tester.exec_prepended_name('intent-cmd-create-with-yaml-file')
        intent = {
            'intentType': 'createAssembly',
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        yml_file = self.tester.create_yaml_file('intent-cmd-create-with.yaml', intent)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'intent', '-e', 'default', '-f', yml_file
            ])
        process_id = self._confirm_process_success(create_result)
        process = self.tester.default_client.processes.get(process_id)
        self.assertEqual(process['assemblyName'], assembly_name)
        self.assertEqual(process['intentType'], 'CreateAssembly')
        self.assertEqual(process['assemblyType'], self.test_case_props['assembly_descriptor']['name'])
        self.assertEqual(process['assemblyProperties']['resourceManager'], 'brent')
        self.assertEqual(process['assemblyProperties']['deploymentLocation'], self.test_case_props['deployment_location']['name'])
        self.assertEqual(process['assemblyProperties']['dummyProp'], 'A')
        self._delete_and_wait(assembly_name)

    def test_create_with_json_file(self):
        assembly_name = self.tester.exec_prepended_name('intent-cmd-create-with-json-file')
        intent = {
            'intentType': 'createAssembly',
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        json_file = self.tester.create_json_file('intent-cmd-create-with.json', intent)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'intent', '-e', 'default', '-f', json_file
            ])
        process_id = self._confirm_process_success(create_result)
        process = self.tester.default_client.processes.get(process_id)
        self.assertEqual(process['assemblyName'], assembly_name)
        self.assertEqual(process['intentType'], 'CreateAssembly')
        self.assertEqual(process['assemblyType'], self.test_case_props['assembly_descriptor']['name'])
        self.assertEqual(process['assemblyProperties']['resourceManager'], 'brent')
        self.assertEqual(process['assemblyProperties']['deploymentLocation'], self.test_case_props['deployment_location']['name'])
        self.assertEqual(process['assemblyProperties']['dummyProp'], 'A')
        self._delete_and_wait(assembly_name)
    
    def test_create_with_set(self):
        assembly_name = self.tester.exec_prepended_name('intent-cmd-create-with-set')
        create_intent = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        create_process_id =  self.tester.default_client.assemblies.intent_create(create_intent)
        self.tester.wait_until(self._build_check_process_success(self.tester), create_process_id)
        create_intent_result = self.cli_runner.invoke(cli, [
            'create', 'intent', '-e', 'default', '--set', 'intentType=deleteAssembly', '--set', f'assemblyName={assembly_name}'
            ])
        process_id = self._confirm_process_success(create_intent_result)
        process = self.tester.default_client.processes.get(process_id)
        self.assertEqual(process['assemblyName'], assembly_name)
        self.assertEqual(process['intentType'], 'DeleteAssembly')
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)

    def test_create_with_set_and_file_merges(self):
        assembly_name = self.tester.exec_prepended_name('intent-cmd-create-with-set-and-file')
        intent = {
            'intentType': 'createAssembly',
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        json_file = self.tester.create_json_file('intent-cmd-create-with-set-and-file.json', intent)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'intent', '-e', 'default', '-f', json_file, '--set', f'assemblyName={assembly_name}'
            ])
        process_id = self._confirm_process_success(create_result)
        process = self.tester.default_client.processes.get(process_id)
        self.assertEqual(process['assemblyName'], assembly_name)
        self.assertEqual(process['intentType'], 'CreateAssembly')
        self.assertEqual(process['assemblyType'], self.test_case_props['assembly_descriptor']['name'])
        self.assertEqual(process['assemblyProperties']['resourceManager'], 'brent')
        self.assertEqual(process['assemblyProperties']['deploymentLocation'], self.test_case_props['deployment_location']['name'])
        self.assertEqual(process['assemblyProperties']['dummyProp'], 'A')
        self._delete_and_wait(assembly_name)
    
    def test_create_with_file_missing_intent_type_fails(self):
        assembly_name = self.tester.exec_prepended_name('intent-cmd-create-with-file-missing-intent')
        intent = {
            'assemblyName': assembly_name,
            'descriptorName': self.test_case_props['assembly_descriptor']['name'],
            'intendedState': 'Active',
            'properties': {
                    'resourceManager': 'brent',
                    'deploymentLocation': self.test_case_props['deployment_location']['name'],
                    'dummyProp': 'A'
                }
        }
        json_file = self.tester.create_json_file('intent-cmd-create-with-file-missing-intent.json', intent)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'intent', '-e', 'default', '-f', json_file
            ])
        self.assert_has_system_exit(create_result)
        expected_output = 'Usage: cli create intent [OPTIONS]'
        expected_output += '\nTry \'cli create intent --help\' for help.'
        expected_output += '\n\nError: Must include "intentType" in contents of "-f, --file" or with "--set intentType=<type>"'
        self.assert_output(create_result, expected_output)
    
    def test_create_with_set_missing_intent_type_fails(self):
        assembly_name = self.tester.exec_prepended_name('intent-cmd-create-with-set-missing-intent')
        create_result = self.cli_runner.invoke(cli, [
            'create', 'intent', '-e', 'default', '--set', 'assemblyName=SomeName'
            ])
        self.assert_has_system_exit(create_result)
        expected_output = 'Usage: cli create intent [OPTIONS]'
        expected_output += '\nTry \'cli create intent --help\' for help.'
        expected_output += '\n\nError: Must include "intentType" in contents of "-f, --file" or with "--set intentType=<type>"'
        self.assert_output(create_result, expected_output)
    