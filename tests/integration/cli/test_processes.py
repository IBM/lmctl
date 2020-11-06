from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict, Tuple
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat
from lmctl.client import TNCOClientHttpError
from lmctl.client.models import CreateAssemblyIntent, DeleteAssemblyIntent
from lmctl.cli.commands.targets.processes import ProcessTable
import yaml
import os
import json
import time

class TestProcesses(CLIIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add deployment location
        cls.test_case_props['deployment_location'] = tester.default_client.deployment_locations.create({
            'name': tester.exec_prepended_name('process-cmds'),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        })
        ## Upload Resource package
        res_pkg_path = tester.tmp_file('dummy_resource.zip')
        tester.build_resource_package_from(tester.test_file('dummy_resource'), res_pkg_path, suffix='process-cmds')
        cls.test_case_props['res_pkg_id'] = tester.default_client.resource_packages.create(res_pkg_path)
        ## Add Resource descriptor 
        cls.test_case_props['resource_descriptor'] = tester.load_descriptor_from(tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='process-cmds')
        tester.default_client.descriptors.create(cls.test_case_props['resource_descriptor'])
        ## Add Assembly descriptor
        cls.test_case_props['assembly_descriptor'] = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='process-cmds')
        tester.default_client.descriptors.create(cls.test_case_props['assembly_descriptor'])
        
    @classmethod
    def after_test_case(cls, tester):
        time.sleep(0.5)
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

    def _delete_and_wait(self, assembly_name: str):
        delete_process_id =  self.tester.default_client.assemblies.intent_delete(
            DeleteAssemblyIntent(assembly_name=assembly_name)
        )
        self.tester.wait_until(self._build_check_process_success(self.tester), delete_process_id)
    
    def test_get_as_yaml(self):
        assembly_name = self.tester.exec_prepended_name('process-cmd-get-yaml')
        process_id, assembly_id = self._create_assembly(assembly_name)
        result = self.cli_runner.invoke(cli, 
            ['get', 'process', '-e', 'default', process_id, '-o', 'yaml']
        )
        loaded_output = yaml.safe_load(result.output)
        self.assertEqual(loaded_output['assemblyId'], assembly_id)
        self.assertEqual(loaded_output['id'], process_id)
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)
        self._delete_and_wait(assembly_name)

    def test_get_as_json(self):
        assembly_name = self.tester.exec_prepended_name('process-cmd-get-json')
        process_id, assembly_id = self._create_assembly(assembly_name)
        result = self.cli_runner.invoke(cli, 
            ['get', 'process', '-e', 'default', process_id, '-o', 'json']
        )
        loaded_output = json.loads(result.output)
        self.assertEqual(loaded_output['assemblyId'], assembly_id)
        self.assertEqual(loaded_output['id'], process_id)
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)
        self._delete_and_wait(assembly_name)

    def test_get_by_name_as_table(self):
        assembly_name = self.tester.exec_prepended_name('process-cmd-get-table')
        process_id, assembly_id = self._create_assembly(assembly_name)
        result = self.cli_runner.invoke(cli, 
            ['get', 'process', '-e', 'default', process_id]
        )
        table_format = TableFormat(table=ProcessTable())
        target_process = self.tester.default_client.processes.get(process_id)
        expected_output = table_format.convert_element(target_process)
        self.assert_output(result, expected_output)
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)
        self._delete_and_wait(assembly_name)
    
    def test_get_shallow(self):
        assembly_name = self.tester.exec_prepended_name('process-cmd-get-shallow')
        process_id, assembly_id = self._create_assembly(assembly_name)
        result = self.cli_runner.invoke(cli, 
            ['get', 'process', '-e', 'default', process_id, '-o', 'yaml', '--shallow']
        )
        loaded_output = yaml.safe_load(result.output)
        self.assertNotIn('executionPlan', loaded_output)
        self.tester.wait_until(self._build_check_process_success(self.tester), process_id)
        self._delete_and_wait(assembly_name)