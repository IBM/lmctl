from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict, Tuple
from lmctl.cli.entry import cli
from lmctl.client import LmClientHttpError
from lmctl.client.models import CreateAssemblyIntent, HealAssemblyIntent, DeleteAssemblyIntent
import yaml
import os
import json
import time

class TestResources(CLIIntegrationTest):
  
    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add deployment location
        cls.test_case_props['deployment_location'] = tester.default_client.deployment_locations.create({
            'name': tester.exec_prepended_name('resource-cmds'),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        })
        ## Upload Resource package
        res_pkg_path = tester.tmp_file('dummy_resource.zip')
        tester.build_resource_package_from(tester.test_file('dummy_resource'), res_pkg_path, suffix='resource-cmds')
        cls.test_case_props['res_pkg_id'] = tester.default_client.resource_packages.create(res_pkg_path)
        ## Add Resource descriptor 
        cls.test_case_props['resource_descriptor'] = tester.load_descriptor_from(tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='resource-cmds')
        tester.default_client.descriptors.create(cls.test_case_props['resource_descriptor'])
        ## Add Assembly descriptor
        cls.test_case_props['assembly_descriptor'] = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='resource-cmds')
        tester.default_client.descriptors.create(cls.test_case_props['assembly_descriptor'])

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.deployment_locations.delete(cls.test_case_props['deployment_location']['name'])
        tester.default_client.resource_packages.delete(cls.test_case_props['res_pkg_id'])
        tester.default_client.descriptors.delete(cls.test_case_props['assembly_descriptor']['name'])
        tester.default_client.descriptors.delete(cls.test_case_props['resource_descriptor']['name'])
    
    def _create_assembly(self, assembly_name: str) -> Tuple[str,str]:
        assembly_name = assembly_name
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
        time.sleep(0.3)
        return create_process_id, assembly_id

    def _confirm_process_success(self, cmd_result):
        self.assertTrue(cmd_result.output.startswith('Accepted - Process: '), msg=f'Output was actually: {cmd_result.output}')
        process_id = cmd_result.output[len('Accepted - Process: ')-1:].strip()
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)
        return process_id
    
    def _get_child(self, assembly: Dict, name: str) -> Dict:
        for child in assembly.get('children', []):
            if child['name'].endswith(f'__{name}'):
                return child
        assembly_name = assembly.get('name', None)
        raise Exception(f'No child found  with name "{name}" in Assembly "{assembly_name}""')

    def _delete_and_wait(self, assembly_name: str):
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)

    def test_heal_with_id(self):
        assembly_name = self.tester.exec_prepended_name('resource-cmd-heal-with-name')
        self._create_assembly(assembly_name)
        assembly = self.tester.default_client.assemblies.get_by_name(assembly_name)
        child_resource = self._get_child(assembly, 'A')
        child_resource_id = child_resource.get('id')
        heal_result = self.cli_runner.invoke(cli, [
            'heal', 'resource', '-e', 'default', '--id', child_resource_id,'--assembly-name', assembly_name
            ])
        self._confirm_process_success(heal_result)
        self._delete_and_wait(assembly_name)
    
    def test_heal_with_metric_key(self):
        assembly_name = self.tester.exec_prepended_name('resource-cmd-heal-with-metric-key')
        self._create_assembly(assembly_name)
        assembly = self.tester.default_client.assemblies.get_by_name(assembly_name)
        child_resource = self._get_child(assembly, 'A')
        child_resource_id = child_resource.get('id')
        heal_result = self.cli_runner.invoke(cli, [
            'heal', 'resource', '-e', 'default', '--metric-key', child_resource_id,'--assembly-name', assembly_name
            ])
        self._confirm_process_success(heal_result)
        self._delete_and_wait(assembly_name)
    
    def test_heal_with_assembly_name(self):
        assembly_name = self.tester.exec_prepended_name('resource-cmd-heal-assembly-name')
        self._create_assembly(assembly_name)
        assembly = self.tester.default_client.assemblies.get_by_name(assembly_name)
        child_resource = self._get_child(assembly, 'A')
        child_resource_name = child_resource.get('name')
        heal_result = self.cli_runner.invoke(cli, [
            'heal', 'resource', '-e', 'default', child_resource_name, '--assembly-name', assembly_name
            ])
        self._confirm_process_success(heal_result)
        self._delete_and_wait(assembly_name)
    
    def test_heal_with_assembly_id(self):
        assembly_name = self.tester.exec_prepended_name('resource-cmd-heal-assembly-id')
        _, assembly_id = self._create_assembly(assembly_name)
        assembly = self.tester.default_client.assemblies.get_by_name(assembly_name)
        child_resource = self._get_child(assembly, 'A')
        child_resource_name = child_resource.get('name')
        heal_result = self.cli_runner.invoke(cli, [
            'heal', 'resource', '-e', 'default', child_resource_name, '--assembly-id', assembly_id
            ])
        self._confirm_process_success(heal_result)
        self._delete_and_wait(assembly_name)
    
    def test_heal_with_id_and_name_fails(self):
        heal_result = self.cli_runner.invoke(cli, [
            'heal', 'resource', '-e', 'default', 'B', '--id', 'SomeId', '--assembly-name', 'SomeName'
            ])
        self.assert_has_system_exit(heal_result)
        expected_output = 'Usage: cli heal resource [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli heal resource --help\' for help.'
        expected_output += '\n\nError: Do not use "NAME" argument when using "--id" option'
        self.assert_output(heal_result, expected_output)
    
    def test_heal_with_metric_key_and_name_fails(self):
        heal_result = self.cli_runner.invoke(cli, [
            'heal', 'resource', '-e', 'default', 'B', '--metric-key', 'SomeKey', '--assembly-name', 'SomeName',
            ])
        self.assert_has_system_exit(heal_result)
        expected_output = 'Usage: cli heal resource [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli heal resource --help\' for help.'
        expected_output += '\n\nError: Do not use "NAME" argument when using "--metric-key" option'
        self.assert_output(heal_result, expected_output)
    
    def test_heal_with_id_and_name_fails(self):
        heal_result = self.cli_runner.invoke(cli, [
            'heal', 'resource', '-e', 'default', '--metric-key', 'SomeKey', '--id', 'SomeId', '--assembly-name', 'SomeName'
            ])
        self.assert_has_system_exit(heal_result)
        expected_output = 'Usage: cli heal resource [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli heal resource --help\' for help.'
        expected_output += '\n\nError: Do not use "--id" option when using "--metric-key" option'
        self.assert_output(heal_result, expected_output)
    
    def test_heal_with_assembly_id_and_name_fails(self):
        heal_result = self.cli_runner.invoke(cli, [
            'heal', 'resource', '-e', 'default', 'B', '--assembly-name', 'SomeName', '--assembly-id', 'SomeId'
            ])
        self.assert_has_system_exit(heal_result)
        expected_output = 'Usage: cli heal resource [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli heal resource --help\' for help.'
        expected_output += '\n\nError: Do not use "--assembly-name" option when using "--assembly-id" option'
        self.assert_output(heal_result, expected_output)
    
    def test_heal_without_name_id_or_metric_key_fails(self):
        heal_result = self.cli_runner.invoke(cli, [
            'heal', 'resource', '-e', 'default', '--assembly-name', 'SomeName'
            ])
        self.assert_has_system_exit(heal_result)
        expected_output = 'Usage: cli heal resource [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli heal resource --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument or "--id" option or "--metric-key" to identify the Resource to be healed'
        self.assert_output(heal_result, expected_output)
    