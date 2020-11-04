from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat
from lmctl.client import TNCOClientHttpError
from lmctl.cli.commands.targets.deployment_location import DeploymentLocationTable
import yaml
import json
import time

class TestDeploymentLocations(CLIIntegrationTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.test_case_props = {}
        ## Add some deployment locations
        cls.test_case_props['dl_A'] = tester.default_client.deployment_locations.create({
            'name': tester.exec_prepended_name('dl-cmds-A'),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {},
            'description': 'Test item A'
        })
        cls.test_case_props['dl_B'] = tester.default_client.deployment_locations.create({
            'name': tester.exec_prepended_name('dl-cmds-B'),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {},
            'description': 'Test item B'
        })
        cls.test_case_props['dl_C'] = tester.default_client.deployment_locations.create({
            'name': tester.exec_prepended_name('dl-cmds-C'),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {},
            'description': 'Test item C'
        })

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.deployment_locations.delete(cls.test_case_props['dl_A']['name'])
        tester.default_client.deployment_locations.delete(cls.test_case_props['dl_B']['name'])
        tester.default_client.deployment_locations.delete(cls.test_case_props['dl_C']['name'])

    def _build_deployment_location_output(self, deployment_location: Dict):
        output = {
            'id': deployment_location.get('name'),
            'name': deployment_location.get('name')
        }
        if 'description' in deployment_location:
            output['description'] = deployment_location.get('description')
        if 'resourceManager' in deployment_location:
            output['resourceManager'] = deployment_location.get('resourceManager')
        if 'infrastructureType' in deployment_location:
            output['infrastructureType'] = deployment_location.get('infrastructureType')
        return output

    def test_get_all_as_yaml(self):
        result = self.cli_runner.invoke(cli, ['get', 'deploymentlocation', '-e', 'default', '-o', 'yaml'])
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self._build_deployment_location_output(self.test_case_props['dl_A']),
                self._build_deployment_location_output(self.test_case_props['dl_B']),
                self._build_deployment_location_output(self.test_case_props['dl_C'])
            ]
        )
    
    def test_get_all_as_json(self):
        result = self.cli_runner.invoke(cli, ['get', 'deploymentlocation', '-e', 'default', '-o', 'json'])
        loaded_output = json.loads(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self._build_deployment_location_output(self.test_case_props['dl_A']),
                self._build_deployment_location_output(self.test_case_props['dl_B']),
                self._build_deployment_location_output(self.test_case_props['dl_C'])
            ]
        )

    def test_get_by_name_as_yaml(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'deploymentlocation', self.test_case_props['dl_A']['name'], '-e', 'default', '-o', 'yaml'
            ])
        loaded_output = yaml.safe_load(result.output)
        self.assertEqual(loaded_output, self._build_deployment_location_output(self.test_case_props['dl_A']))
    
    def test_get_by_name_as_json(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'deploymentlocation', self.test_case_props['dl_A']['name'], '-e', 'default', '-o', 'json'
            ])
        loaded_output = json.loads(result.output)
        self.assertEqual(loaded_output, self._build_deployment_location_output(self.test_case_props['dl_A']))
    
    def test_get_by_name_as_table(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'deploymentlocation', self.test_case_props['dl_A']['name'], '-e', 'default'
            ])
        table_format = TableFormat(table=DeploymentLocationTable())
        expected_output = table_format.convert_element(self._build_deployment_location_output(self.test_case_props['dl_A']))
        self.assert_output(result, expected_output)

    def test_get_by_name_containing(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'deploymentlocation', '--name-contains', self.tester.execution_id, '-e', 'default', '-o', 'yaml'
            ])
        loaded_output = yaml.safe_load(result.output)
        self._find_in_list_output(
            parsed_list_output=loaded_output.get('items'), 
            items_to_find=[
                self._build_deployment_location_output(self.test_case_props['dl_A']),
                self._build_deployment_location_output(self.test_case_props['dl_B']),
                self._build_deployment_location_output(self.test_case_props['dl_C'])
            ]
        )

    def test_get_with_name_and_name_contains_fails(self):
        result = self.cli_runner.invoke(cli, [
            'get', 'deploymentlocation', 'SomeName', '--name-contains', 'SomeValue', '-e', 'default', '-o', 'yaml'
            ])
        self.assert_has_system_exit(result)
        expected_output = 'Usage: cli get deploymentlocation [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli get deploymentlocation --help\' for help.'
        expected_output += '\n\nError: Do not use "NAME" argument when using the "--name-contains" option'
        self.assert_output(result, expected_output)

    def test_create_with_yaml_file(self):
        dl_file = self.tester.render_template_file(self.tester.test_file('dummy_dl.yaml'), self.tester.tmp_file('dummy_dl.yaml'), suffix='cmds-create-with-yaml')
        # Load the file so we can verify against the get result
        with open(dl_file, 'r') as f:
            dl = yaml.safe_load(f.read())
            dl_name = dl['name']
        create_result = self.cli_runner.invoke(cli, [
            'create', 'deploymentlocation', '-e', 'default', '-f', dl_file
            ])
        self.assert_output(create_result, f'Created: {dl_name}')
        ## Get the location to confirm it was created
        api_get_result = self.tester.default_client.deployment_locations.get(dl_name)
        self.assertEqual(api_get_result['name'], dl['name'])
        self.assertEqual(api_get_result['infrastructureType'], dl['infrastructureType'])
        self.assertEqual(api_get_result['resourceManager'], dl['resourceManager'])
        self.assertEqual(api_get_result['description'], dl['description'])
        self.tester.default_client.deployment_locations.delete(dl_name)

    def test_create_with_json_file(self):
        dl_file = self.tester.render_template_file(self.tester.test_file('dummy_dl.json'), self.tester.tmp_file('dummy_dl.json'), suffix='cmds-create-with-json')
        # Load the file so we can verify against the get result
        with open(dl_file, 'r') as f:
            dl = json.loads(f.read())
            dl_name = dl['name']
        create_result = self.cli_runner.invoke(cli, [
            'create', 'deploymentlocation', '-e', 'default', '-f', dl_file
            ])
        self.assert_output(create_result, f'Created: {dl_name}')
        ## Get the location to confirm it was created
        time.sleep(0.5)
        api_get_result = self.tester.default_client.deployment_locations.get(dl_name)
        self.assertEqual(api_get_result['name'], dl['name'])
        self.assertEqual(api_get_result['infrastructureType'], dl['infrastructureType'])
        self.assertEqual(api_get_result['resourceManager'], dl['resourceManager'])
        self.assertEqual(api_get_result['description'], dl['description'])
        self.tester.default_client.deployment_locations.delete(dl_name)

    def test_create_with_set(self):
        dl_name = self.tester.exec_prepended_name('dl-cmds-create-with-set')
        create_result = self.cli_runner.invoke(cli, [
            'create', 'deploymentlocation', '-e', 'default', 
                        '--set', f'name={dl_name}', 
                        '--set', 'infrastructureType=Other', 
                        '--set', 'resourceManager=brent',
                        '--set', 'description=Test create with --set'
            ])
        self.assert_output(create_result, f'Created: {dl_name}')
        ## Get the location to confirm it was created
        time.sleep(0.5)
        api_get_result = self.tester.default_client.deployment_locations.get(dl_name)
        self.assertEqual(api_get_result['name'], dl_name)
        self.assertEqual(api_get_result['infrastructureType'], 'Other')
        self.assertEqual(api_get_result['resourceManager'], 'brent')
        self.assertEqual(api_get_result['description'], 'Test create with --set')
        self.tester.default_client.deployment_locations.delete(dl_name)

    def test_update_with_yaml_file(self):
        dl_file = self.tester.tmp_file('cmd_update_dl.yaml')
        self.test_case_props['dl_A']['description'] = 'Updated description for cmd testing with yaml'
        with open(dl_file, 'w') as f:
            f.write(yaml.safe_dump(self.test_case_props['dl_A']))
        update_result = self.cli_runner.invoke(cli, [
            'update', 'deploymentlocation', '-e', 'default', '-f', dl_file
            ])
        dl_name = self.test_case_props['dl_A']['name']
        self.assert_output(update_result, f'Updated: {dl_name}')
        ## Get the location to confirm it was updated
        time.sleep(0.5)
        api_get_result = self.tester.default_client.deployment_locations.get(dl_name)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with yaml')

    def test_update_with_json_file(self):
        dl_file = self.tester.tmp_file('cmd_update_dl.json')
        self.test_case_props['dl_A']['description'] = 'Updated description for cmd testing with json'
        with open(dl_file, 'w') as f:
            f.write(json.dumps(self.test_case_props['dl_A']))
        update_result = self.cli_runner.invoke(cli, [
            'update', 'deploymentlocation', '-e', 'default', '-f', dl_file
            ])
        dl_name = self.test_case_props['dl_A']['name']
        self.assert_output(update_result, f'Updated: {dl_name}')
        ## Get the location to confirm it was updated
        time.sleep(0.5)
        api_get_result = self.tester.default_client.deployment_locations.get(dl_name)
        self.assertEqual(api_get_result['description'], 'Updated description for cmd testing with json')
 
    def test_update_with_set(self):
        dl_name = self.test_case_props['dl_A']['name']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'deploymentlocation', '-e', 'default', dl_name, '--set', 'description=Updated descriptor for cmd testing with --set'
            ])
        self.assert_output(update_result, f'Updated: {dl_name}')
        ## Get the location to confirm it was updated
        time.sleep(0.5)
        api_get_result = self.tester.default_client.deployment_locations.get(dl_name)
        self.assertEqual(api_get_result['description'], 'Updated descriptor for cmd testing with --set')

    def test_update_with_name_and_file_fails(self):
        dl_file = self.tester.render_template_file(self.tester.test_file('dummy_dl.json'), self.tester.tmp_file('dummy_dl.json'), suffix='cmds-update-with-name-and-file')
        with open(dl_file, 'r') as f:
            dl = json.loads(f.read())
            dl_name = dl['name']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'deploymentlocation', '-e', 'default', dl_name, '-f', dl_file
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update deploymentlocation [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli update deploymentlocation --help\' for help.'
        expected_output += '\n\nError: Do not use "NAME" argument when using "-f, --file" option'
        self.assert_output(update_result, expected_output)

    def test_update_with_set_and_no_name_fails(self):
        update_result = self.cli_runner.invoke(cli, [
            'update', 'deploymentlocation', '-e', 'default',  '--set', 'description=testing'
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update deploymentlocation [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli update deploymentlocation --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument when no "-f, --file" option specified'
        self.assert_output(update_result, expected_output)

    def test_delete_with_yaml_file(self):
        dl_file = self.tester.render_template_file(self.tester.test_file('dummy_dl.yaml'), self.tester.tmp_file('dummy_dl.yaml'), suffix='cmds-delete-with-yaml')
        with open(dl_file, 'r') as f:
            dl = yaml.safe_load(f.read())
            dl_name = dl['name']
        create_result = self.cli_runner.invoke(cli, [
            'create', 'deploymentlocation', '-e', 'default', '-f', dl_file
            ])
        self.assert_no_errors(create_result)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'deploymentlocation', '-e', 'default', '-f', dl_file
            ])
        self.assert_output(delete_result, f'Removed: {dl_name}')
        ## Get the location to confirm it was deleted
        time.sleep(0.5)
        try:
            api_get_result = self.tester.default_client.deployment_locations.get(dl_name)
            self.fail('Deployment location should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the deployment location failed with an unexpected error: {str(e)}')
    
    def test_delete_with_json_file(self):
        dl_file = self.tester.render_template_file(self.tester.test_file('dummy_dl.json'), self.tester.tmp_file('dummy_dl.json'), suffix='cmds-delete-with-json')
        with open(dl_file, 'r') as f:
            dl = yaml.safe_load(f.read())
            dl_name = dl['name']
        create_result = self.cli_runner.invoke(cli, [
            'create', 'deploymentlocation', '-e', 'default', '-f', dl_file
            ])
        self.assert_no_errors(create_result)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'deploymentlocation', '-e', 'default', '-f', dl_file
            ])
        self.assert_output(delete_result, f'Removed: {dl_name}')
        ## Get the location to confirm it was deleted
        time.sleep(0.5)
        try:
            api_get_result = self.tester.default_client.deployment_locations.get(dl_name)
            self.fail('Deployment location should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the deployment location failed with an unexpected error: {str(e)}')

    def test_delete_with_name(self):
        dl_file = self.tester.render_template_file(self.tester.test_file('dummy_dl.json'), self.tester.tmp_file('dummy_dl.json'), suffix='cmds-delete-with-json')
        with open(dl_file, 'r') as f:
            dl = yaml.safe_load(f.read())
            dl_name = dl['name']
        create_result = self.cli_runner.invoke(cli, [
            'create', 'deploymentlocation', '-e', 'default', '-f', dl_file
            ])
        self.assert_no_errors(create_result)
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'deploymentlocation', '-e', 'default', dl_name
            ])
        self.assert_output(delete_result, f'Removed: {dl_name}')
        ## Get the location to confirm it was deleted
        time.sleep(0.5)
        try:
            api_get_result = self.tester.default_client.deployment_locations.get(dl_name)
            self.fail('Deployment location should have been deleted but it can still be found')
        except TNCOClientHttpError as e:
            if e.status_code != 404:
                self.fail(f'Retrieving the deployment location failed with an unexpected error: {str(e)}')
    
    def test_delete_with_no_name_or_file_fails(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'deploymentlocation', '-e', 'default'
            ])
        self.assert_has_system_exit(delete_result)
        expected_output = 'Usage: cli delete deploymentlocation [OPTIONS] [NAME]'
        expected_output += '\nTry \'cli delete deploymentlocation --help\' for help.'
        expected_output += '\n\nError: Must set "NAME" argument when no "-f, --file" option specified'
        self.assert_output(delete_result, expected_output)

    def test_delete_with_ignore_missing(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'deploymentlocation', '-e', 'default', 'NonExistentObj', '--ignore-missing'
            ])
        self.assert_no_errors(delete_result)
        self.assert_output(delete_result, f'No Deployment Location found with name NonExistentObj (ignoring)')