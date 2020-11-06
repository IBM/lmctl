from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat
from lmctl.client import TNCOClientHttpError
from lmctl.cli.commands.targets.resource_managers import ResourceManagerTable
import yaml
import json
import time

class TestResourceManagers(CLIIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        # Add some Resource Managers
        cls.test_case_props['resource_manager_A'] = {
            'name': tester.exec_prepended_name('rm-cmd-A'),
            'type': 'Brent',
            'url': 'https://brent:8291/api/resource-manager'
        }
        tester.default_client.resource_managers.create(cls.test_case_props['resource_manager_A'])
        cls.test_case_props['resource_manager_B'] = {
            'name': tester.exec_prepended_name('rm-cmd-B'),
            'type': 'Brent',
            'url': 'https://brent:8291/api/resource-manager'
        }
        tester.default_client.resource_managers.create(cls.test_case_props['resource_manager_B'])
        ## Add deployment location
        cls.test_case_props['deployment_location_A'] = tester.default_client.deployment_locations.create({
            'name': tester.exec_prepended_name('rm-cmd-A'),
            'infrastructureType': 'Other',
            'resourceManager': cls.test_case_props['resource_manager_A']['name'],
            'properties': {}
        })
        cls.test_case_props['deployment_location_B'] = tester.default_client.deployment_locations.create({
            'name': tester.exec_prepended_name('rm-cmd-B'),
            'infrastructureType': 'Other',
            'resourceManager': cls.test_case_props['resource_manager_B']['name'],
            'properties': {}
        })
        ## Upload Resource package
        res_pkg_path = tester.tmp_file('dummy_resource.zip')
        tester.build_resource_package_from(tester.test_file('dummy_resource'), res_pkg_path, suffix='rm-cmd')
        cls.test_case_props['dummy_res_pkg_id'] = tester.default_client.resource_packages.create(res_pkg_path)

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.deployment_locations.delete(cls.test_case_props['deployment_location_A']['name'])
        tester.default_client.deployment_locations.delete(cls.test_case_props['deployment_location_B']['name'])
        tester.default_client.resource_managers.delete(cls.test_case_props['resource_manager_A']['name'])
        tester.default_client.resource_managers.delete(cls.test_case_props['resource_manager_B']['name'])
        
    def _match_rm(self, x: Dict, y: Dict):
        if x.get('name') != y.get('name'):
            return False
        return True

    def test_get_all_as_yaml(self):
        result = self.cli_runner.invoke(cli, ['get', 'resourcemanager', '-e', 'default', '-o', 'yaml'])
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self.test_case_props['resource_manager_A'],
                self.test_case_props['resource_manager_B']
            ],
            matcher=self._match_rm
        )
    
    def test_get_all_as_json(self):
        result = self.cli_runner.invoke(cli, ['get', 'resourcemanager', '-e', 'default', '-o', 'json'])
        loaded_output = json.loads(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self.test_case_props['resource_manager_A'],
                self.test_case_props['resource_manager_B']
            ],
            matcher=self._match_rm
        )

    def test_get_by_name_as_yaml(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'resourcemanager', self.test_case_props['resource_manager_A']['name'], '-e', 'default', '-o', 'yaml'
            ])
        loaded_output = yaml.safe_load(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['resource_manager_A']['name'])
        self.assertEqual(loaded_output['url'], self.test_case_props['resource_manager_A']['url'])
    
    def test_get_by_name_as_json(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'resourcemanager', self.test_case_props['resource_manager_A']['name'], '-e', 'default', '-o', 'json'
            ])
        loaded_output = json.loads(result.output)
        self.assertEqual(loaded_output['name'], self.test_case_props['resource_manager_A']['name'])
        self.assertEqual(loaded_output['url'], self.test_case_props['resource_manager_A']['url'])
    
    def test_get_by_name_as_table(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'resourcemanager', self.test_case_props['resource_manager_A']['name'], '-e', 'default'
            ])
        table_format = TableFormat(table=ResourceManagerTable())
        expected_output = table_format.convert_element(self.test_case_props['resource_manager_A'])
        self.assert_output(result, expected_output)

    def test_create_with_yaml_file(self):
        rm_name = self.tester.exec_prepended_name('rm-cmd-create-with-yaml')
        resource_manager = {
            'name': rm_name,
            'type': 'Brent',
            'url': 'https://brent:8291/api/resource-manager'
        }
        yml_file = self.tester.create_yaml_file('rm-cmd-create-with.yaml', resource_manager)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcemanager', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(create_result, f'Created: {rm_name}')
        api_get_result = self.tester.default_client.resource_managers.get(rm_name)
        self.assertEqual(api_get_result['name'], resource_manager['name'])
        self.assertEqual(api_get_result['url'], resource_manager['url'])
    
    def test_create_with_json_file(self):
        rm_name = self.tester.exec_prepended_name('rm-cmd-create-with-json')
        resource_manager = {
            'name': rm_name,
            'type': 'Brent',
            'url': 'https://brent:8291/api/resource-manager'
        }
        json_file = self.tester.create_json_file('rm-cmd-create-with.json', resource_manager)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcemanager', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {rm_name}')
        api_get_result = self.tester.default_client.resource_managers.get(rm_name)
        self.assertEqual(api_get_result['name'], resource_manager['name'])
        self.assertEqual(api_get_result['url'], resource_manager['url'])
    
    def test_create_with_set(self):
        rm_name = self.tester.exec_prepended_name('rm-cmd-create-with-set')
        url = 'https://brent:8291/api/resource-manager'
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcemanager', '-e', 'default', 
                        '--set', f'name={rm_name}', 
                        '--set', f'url={url}'
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {rm_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.resource_managers.get(rm_name)
        self.assertEqual(api_get_result['name'], rm_name)
        self.assertEqual(api_get_result['url'], url)

    def test_create_print_report_as_yaml(self):
        rm_name = self.tester.exec_prepended_name('rm-cmd-yaml-report')
        resource_manager = {
            'name': rm_name,
            'type': 'Brent',
            'url': 'https://brent:8291/api/resource-manager'
        }
        yml_file = self.tester.create_yaml_file('rm-cmd-yaml-report.yaml', resource_manager)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcemanager', '-e', 'default', '-f', yml_file, '--print-report', '-o', 'yaml'
            ])
        report = yaml.safe_load(create_result.output)
        self.assertIn('deploymentLocations', report)
        self.assertIn('resourceTypes', report)
    
    def test_create_print_report_as_json(self):
        rm_name = self.tester.exec_prepended_name('rm-cmd-json-report')
        resource_manager = {
            'name': rm_name,
            'type': 'Brent',
            'url': 'https://brent:8291/api/resource-manager'
        }
        yml_file = self.tester.create_yaml_file('rm-cmd-json-report.yaml', resource_manager)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcemanager', '-e', 'default', '-f', yml_file, '--print-report', '-o', 'json'
            ])
        report = json.loads(create_result.output)
        self.assertIn('deploymentLocations', report)
        self.assertIn('resourceTypes', report)

    def test_create_print_report_as_table(self):
        rm_name = self.tester.exec_prepended_name('rm-cmd-create-tbl-rprt')
        resource_manager = {
            'name': rm_name,
            'type': 'Brent',
            'url': 'https://brent:8291/api/resource-manager'
        }
        yml_file = self.tester.create_yaml_file('rm-cmd-create-yaml-print-report.yaml', resource_manager)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcemanager', '-e', 'default', '-f', yml_file, '--print-report'
            ])
        report = create_result.output
        # Difficult to verify table output with unknown number of dls and resource types
        self.assertIn('| Name', report)
        self.assertIn('| Operation', report)
        self.assertIn('| Success', report)
        self.assertIn('| Failure Reason', report)

    def test_update_with_yaml_file(self):
        yml_file = self.tester.create_yaml_file('rm-cmd-update-with.yaml', self.test_case_props['resource_manager_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'resourcemanager', '-e', 'default', '-f', yml_file
            ])
        rm_name = self.test_case_props['resource_manager_A']['name']
        self.assert_output(update_result, f'Updated: {rm_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.resource_managers.get(rm_name)
        self.assertEqual(api_get_result['name'], self.test_case_props['resource_manager_A']['name'])
        self.assertEqual(api_get_result['url'], self.test_case_props['resource_manager_A']['url'])
    
    def test_update_with_json_file(self):
        json_file = self.tester.create_json_file('rm-cmd-update-with.json', self.test_case_props['resource_manager_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'resourcemanager', '-e', 'default', '-f', json_file
            ])
        rm_name = self.test_case_props['resource_manager_A']['name']
        self.assert_output(update_result, f'Updated: {rm_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.resource_managers.get(rm_name)
        self.assertEqual(api_get_result['name'], self.test_case_props['resource_manager_A']['name'])
        self.assertEqual(api_get_result['url'], self.test_case_props['resource_manager_A']['url'])
    
    def test_update_with_set(self):
        rm_name = self.test_case_props['resource_manager_A']['name']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'resourcemanager', '-e', 'default', rm_name, '--set', 'url=https://brent:8291/api/resource-manager'
            ])
        self.assert_output(update_result, f'Updated: {rm_name}')
        time.sleep(0.2)
        api_get_result = self.tester.default_client.resource_managers.get(rm_name)
        self.assertEqual(api_get_result['name'], self.test_case_props['resource_manager_A']['name'])
        self.assertEqual(api_get_result['url'], self.test_case_props['resource_manager_A']['url'])
    
    def test_update_with_name_and_file_fails(self):
        yml_file = self.tester.create_yaml_file('rm-cmd-update-with-name-and-file-fails.yaml', self.test_case_props['resource_manager_A'])
        update_result = self.cli_runner.invoke(cli, [
            'update', 'resourcemanager', '-e', 'default', 'SomeName', '-f', yml_file
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update resourcemanager [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli update resourcemanager --help\' for help.'
        expected_output += '\n\nError: Do not use "NAME" argument when using "-f, --file" option'
        self.assert_output(update_result, expected_output)

    def test_update_with_set_and_no_name_fails(self):
        update_result = self.cli_runner.invoke(cli, [
            'update', 'resourcemanager', '-e', 'default',  '--set', 'url=example'
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update resourcemanager [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli update resourcemanager --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument when no "-f, --file" option specified'
        self.assert_output(update_result, expected_output)
    
    def test_update_print_report_as_yaml(self):
        rm_name = self.test_case_props['resource_manager_A']['name']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'resourcemanager', '-e', 'default', rm_name, '--print-report', '-o', 'yaml'
            ])
        report = yaml.safe_load(update_result.output)
        self.assertIn('deploymentLocations', report)
        self.assertIn('resourceTypes', report)

    def test_update_print_report_as_json(self):
        rm_name = self.test_case_props['resource_manager_A']['name']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'resourcemanager', '-e', 'default', rm_name, '--print-report', '-o', 'json'
            ])
        report = json.loads(update_result.output)
        self.assertIn('deploymentLocations', report)
        self.assertIn('resourceTypes', report)

    def test_update_print_report_as_table(self):
        rm_name = self.test_case_props['resource_manager_A']['name']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'resourcemanager', '-e', 'default', rm_name, '--print-report'
            ])
        report = update_result.output
        # Difficult to verify table output with unknown number of dls and resource types
        self.assertIn('| Name', report)
        self.assertIn('| Operation', report)
        self.assertIn('| Success', report)
        self.assertIn('| Failure Reason', report)

    def test_delete_with_yaml_file(self):
        rm_name = self.tester.exec_prepended_name('rm-cmd-delete-with-yaml')
        resource_manager = {
            'name': rm_name,
            'url': 'https://brent:8291/api/resource-manager'
        }
        yml_file = self.tester.create_yaml_file('rm-cmd-delete-with.yaml', resource_manager)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcemanager', '-e', 'default', '-f', yml_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {rm_name}')
        yml_file = self.tester.create_yaml_file('rm-cmd-delete-with.yaml', resource_manager)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcemanager', '-e', 'default', '-f', yml_file
            ])
        self.assert_output(delete_result, f'Removed: {rm_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.resource_managers.get(rm_name)
            self.fail('Resource Manager should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Resource Manager failed with an unexpected error: {str(e)}')
    
    def test_delete_with_json_file(self):
        rm_name = self.tester.exec_prepended_name('rm-cmd-delete-with-json')
        resource_manager = {
            'name': rm_name,
            'url': 'https://brent:8291/api/resource-manager'
        }
        json_file = self.tester.create_json_file('rm-cmd-delete-with.json', resource_manager)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcemanager', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {rm_name}')
        json_file = self.tester.create_json_file('rm-cmd-delete-with.json', resource_manager)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcemanager', '-e', 'default', '-f', json_file
            ])
        self.assert_output(delete_result, f'Removed: {rm_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.resource_managers.get(rm_name)
            self.fail('Resource Manager should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Resource Manager failed with an unexpected error: {str(e)}')
    
    def test_delete_with_name(self):
        rm_name = self.tester.exec_prepended_name('rm-cmd-delete-with-json')
        resource_manager = {
            'name': rm_name,
            'url': 'https://brent:8291/api/resource-manager'
        }
        json_file = self.tester.create_json_file('rm-cmd-delete-with.json', resource_manager)
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcemanager', '-e', 'default', '-f', json_file
            ])
        self.assert_no_errors(create_result)
        self.assert_output(create_result, f'Created: {rm_name}')
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcemanager', '-e', 'default', rm_name
            ])
        self.assert_output(delete_result, f'Removed: {rm_name}')
        time.sleep(0.2)
        try:
            api_get_result = self.tester.default_client.resource_managers.get(rm_name)
            self.fail('Resource Manager should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the Resource Manager failed with an unexpected error: {str(e)}')
    
    def test_delete_with_no_name_or_file_fails(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcemanager', '-e', 'default'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete resourcemanager [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli delete resourcemanager --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument when no "-f, --file" option specified'
        self.assert_output(delete_result, expected_output)
    
    def test_delete_with_ignore_missing(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcemanager', '-e', 'default', 'NonExistentObj', '--ignore-missing'
            ])
        self.assert_no_errors(delete_result)
        self.assert_output(delete_result, f'No Resource Manager found with name NonExistentObj (ignoring)')