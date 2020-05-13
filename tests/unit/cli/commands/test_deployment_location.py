import tests.unit.cli.commands.command_testing as command_testing
import lmctl.drivers.lm.base as lm_drivers
import lmctl.cli.commands.deployment_location as deployment_cmds
import tempfile
import shutil
import os
import json
import yaml
from unittest.mock import patch
from tests.common.simulations.lm_simulator import LmSimulator

class TestDeploymentLocationCommands(command_testing.CommandTestCase):

    def setUp(self):
        super().setUp()
        # Created simulated LM session when requested
        self.lm_sim = LmSimulator().start()
        create_lm_session_patcher = patch('lmctl.cli.ctlmgmt.create_lm_session')
        self.mock_create_lm_session = create_lm_session_patcher.start()
        self.mock_create_lm_session.return_value = self.lm_sim.as_mocked_session()
        self.addCleanup(create_lm_session_patcher.stop)
        self.lm_sim.add_rm({'name': 'rm123'})

    def test_add_with_defaults(self):
        result = self.runner.invoke(deployment_cmds.add, ['TestEnv', 'testdl', '--rm', 'rm123'])
        self.assert_no_errors(result)
        expected_id = None
        for dl_id, dl in self.lm_sim.deployment_locations.items():
            expected_id = dl_id
        expected_output = '| id                                   | name   | resourceManager   | infrastructureType   | description   |'
        expected_output += '\n|--------------------------------------+--------+-------------------+----------------------+---------------|'
        expected_output += '\n| {0} | testdl | rm123             |                      |               |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_dl_driver = self.mock_create_lm_session.return_value.deployment_location_driver
        mock_dl_driver.add_location.assert_called_once_with({'name': 'testdl', 'description': None, 'resourceManager': 'rm123', 'infrastructureType': None, 'infrastructureSpecificProperties': {}})

    def test_add_with_params(self):
        result = self.runner.invoke(deployment_cmds.add, ['TestEnv', 'testdl', '--rm', 'rm123', '-i', 'Openstack', '-d', 'test location'])
        self.assert_no_errors(result)
        expected_id = None
        for dl_id, dl in self.lm_sim.deployment_locations.items():
            expected_id = dl_id
        expected_output = '| id                                   | name   | resourceManager   | infrastructureType   | description   |'
        expected_output += '\n|--------------------------------------+--------+-------------------+----------------------+---------------|'
        expected_output += '\n| {0} | testdl | rm123             | Openstack            | test location |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_dl_driver = self.mock_create_lm_session.return_value.deployment_location_driver
        mock_dl_driver.add_location.assert_called_once_with({'name': 'testdl', 'description': 'test location', 'resourceManager': 'rm123', 'infrastructureType': 'Openstack', 'infrastructureSpecificProperties': {}})

    def test_add_with_json_properties(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            properties_dict = {
                'propA': 'valueA'
            } 
            properties_file = os.path.join(tmp_dir, 'props.json')
            with open(properties_file, 'w') as f:
                json.dump(properties_dict, f)
            result = self.runner.invoke(deployment_cmds.add, ['TestEnv', 'testdl', '--rm', 'rm123', '-p', properties_file])
            self.assert_no_errors(result)
            expected_id = None
            for dl_id, dl in self.lm_sim.deployment_locations.items():
                expected_id = dl_id
            expected_output = '| id                                   | name   | resourceManager   | infrastructureType   | description   |'
            expected_output += '\n|--------------------------------------+--------+-------------------+----------------------+---------------|'
            expected_output += '\n| {0} | testdl | rm123             |                      |               |'.format(expected_id)
            self.assert_output(result, expected_output)
            self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
            mock_dl_driver = self.mock_create_lm_session.return_value.deployment_location_driver
            mock_dl_driver.add_location.assert_called_once_with({'name': 'testdl', 'description': None, 'resourceManager': 'rm123', 'infrastructureType': None, 'infrastructureSpecificProperties': properties_dict})
        finally:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)

    def test_add_with_yaml_properties(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            properties_dict = {
                'propA': 'valueA'
            } 
            properties_file = os.path.join(tmp_dir, 'props.yaml')
            with open(properties_file, 'w') as f:
                yaml.dump(properties_dict, f)
            result = self.runner.invoke(deployment_cmds.add, ['TestEnv', 'testdl', '--rm', 'rm123', '-p', properties_file])
            self.assert_no_errors(result)
            expected_id = None
            for dl_id, dl in self.lm_sim.deployment_locations.items():
                expected_id = dl_id
            expected_output = '| id                                   | name   | resourceManager   | infrastructureType   | description   |'
            expected_output += '\n|--------------------------------------+--------+-------------------+----------------------+---------------|'
            expected_output += '\n| {0} | testdl | rm123             |                      |               |'.format(expected_id)
            self.assert_output(result, expected_output)
            self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
            mock_dl_driver = self.mock_create_lm_session.return_value.deployment_location_driver
            mock_dl_driver.add_location.assert_called_once_with({'name': 'testdl', 'description': None, 'resourceManager': 'rm123', 'infrastructureType': None, 'infrastructureSpecificProperties': properties_dict})
        finally:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)

    def test_add_with_config(self):
        result = self.runner.invoke(deployment_cmds.add, ['TestEnv', 'testdl', '--rm', 'rm123', '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_id = None
        for dl_id, dl in self.lm_sim.deployment_locations.items():
                expected_id = dl_id
        expected_output = '| id                                   | name   | resourceManager   | infrastructureType   | description   |'
        expected_output += '\n|--------------------------------------+--------+-------------------+----------------------+---------------|'
        expected_output += '\n| {0} | testdl | rm123             |                      |               |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_add_with_pwd(self):
        result = self.runner.invoke(deployment_cmds.add, ['TestEnv', 'testdl', '--rm', 'rm123', '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_id = None
        for dl_id, dl in self.lm_sim.deployment_locations.items():
                expected_id = dl_id
        expected_output = '| id                                   | name   | resourceManager   | infrastructureType   | description   |'
        expected_output += '\n|--------------------------------------+--------+-------------------+----------------------+---------------|'
        expected_output += '\n| {0} | testdl | rm123             |                      |               |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_add_with_output_json_format(self):
        result = self.runner.invoke(deployment_cmds.add, ['TestEnv', 'testdl', '--rm', 'rm123', '-f', 'json'])
        self.assert_no_errors(result)
        expected_id = None
        for dl_id, dl in self.lm_sim.deployment_locations.items():
            expected_id = dl_id
        expected_output = '{'
        expected_output += '\n  \"name\": \"testdl\",'
        expected_output += '\n  \"description\": null,'
        expected_output += '\n  \"resourceManager\": \"rm123\",'
        expected_output += '\n  \"infrastructureType\": null,'
        expected_output += '\n  \"infrastructureSpecificProperties\": {},'
        expected_output += '\n  \"id\": \"{0}\"'.format(expected_id)
        expected_output += '\n}'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_add_with_output_yaml_format(self):
        result = self.runner.invoke(deployment_cmds.add, ['TestEnv', 'testdl', '--rm', 'rm123', '-f', 'yaml'])
        self.assert_no_errors(result)
        expected_id = None
        for dl_id, dl in self.lm_sim.deployment_locations.items():
            expected_id = dl_id
        expected_output = 'name: testdl'
        expected_output += '\ndescription: null'
        expected_output += '\nresourceManager: rm123'
        expected_output += '\ninfrastructureType: null'
        expected_output += '\ninfrastructureSpecificProperties: {}'
        expected_output += '\nid: {0}\n'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_add_handles_lm_driver_error(self):
        self.mock_create_lm_session.return_value.deployment_location_driver.add_location.side_effect = lm_drivers.LmDriverException('Mocked error')
        result = self.runner.invoke(deployment_cmds.add, ['TestEnv', 'testdl', '--rm', 'rm123'])
        self.assert_has_system_exit(result)
        expected_output = 'LM error occurred: Mocked error'
        self.assert_output(result, expected_output)
        
    def test_delete_with_defaults(self):
        dl_id = '123'
        dl_name = 'abc'
        self.lm_sim.add_deployment_location({'id': dl_id, 'name': dl_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.delete, ['TestEnv', dl_name])
        self.assert_no_errors(result)
        expected_output = 'Deleting deployment location: {0}...'.format(dl_id)
        expected_output += '\nDeleted deployment location: {0}'.format(dl_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_dl_driver = self.mock_create_lm_session.return_value.deployment_location_driver
        mock_dl_driver.get_locations_by_name.assert_called_once_with(dl_name)
        mock_dl_driver.delete_location.assert_called_once_with(dl_id)
    
    def test_delete_with_config(self):
        dl_id = '123'
        dl_name = 'abc'
        self.lm_sim.add_deployment_location({'id': dl_id, 'name': dl_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.delete, ['TestEnv', dl_name, '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_output = 'Deleting deployment location: {0}...'.format(dl_id)
        expected_output += '\nDeleted deployment location: {0}'.format(dl_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_delete_with_pwd(self):
        dl_id = '123'
        dl_name = 'abc'
        self.lm_sim.add_deployment_location({'id': dl_id, 'name': dl_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.delete, ['TestEnv', dl_name, '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_output = 'Deleting deployment location: {0}...'.format(dl_id)
        expected_output += '\nDeleted deployment location: {0}'.format(dl_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_delete_handles_lm_driver_error(self):
        result = self.runner.invoke(deployment_cmds.delete, ['TestEnv', 'SomeDl'])
        self.assert_has_system_exit(result)
        expected_output = 'Error: No deployment location with name: SomeDl'
        self.assert_output(result, expected_output)

    def test_get_with_defaults(self):
        dl_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        dl_name = 'testdl'
        self.lm_sim.add_deployment_location({'id': dl_id, 'name': dl_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.get, ['TestEnv', dl_name])
        self.assert_no_errors(result)
        expected_output = '| id                                   | name   | resourceManager   | infrastructureType   | description   |'
        expected_output += '\n|--------------------------------------+--------+-------------------+----------------------+---------------|'
        expected_output += '\n| {0} | testdl | rm123             |                      |               |'.format(dl_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_dl_driver = self.mock_create_lm_session.return_value.deployment_location_driver
        mock_dl_driver.get_locations_by_name.assert_called_once_with(dl_name)

    def test_get_with_config(self):
        dl_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        dl_name = 'testdl'
        self.lm_sim.add_deployment_location({'id': dl_id, 'name': dl_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.get, ['TestEnv', dl_name, '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_output = '| id                                   | name   | resourceManager   | infrastructureType   | description   |'
        expected_output += '\n|--------------------------------------+--------+-------------------+----------------------+---------------|'
        expected_output += '\n| {0} | testdl | rm123             |                      |               |'.format(dl_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_get_with_pwd(self):
        dl_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        dl_name = 'testdl'
        self.lm_sim.add_deployment_location({'id': dl_id, 'name': dl_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.get, ['TestEnv', dl_name, '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_output = '| id                                   | name   | resourceManager   | infrastructureType   | description   |'
        expected_output += '\n|--------------------------------------+--------+-------------------+----------------------+---------------|'
        expected_output += '\n| {0} | testdl | rm123             |                      |               |'.format(dl_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_get_not_found(self):
        result = self.runner.invoke(deployment_cmds.get, ['TestEnv', 'SomeDl'])
        self.assert_has_system_exit(result)
        expected_output = 'Error: No deployment location with name: SomeDl'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
    
    def test_get_with_output_json_format(self):
        dl_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        dl_name = 'testdl'
        self.lm_sim.add_deployment_location({'id': dl_id, 'name': dl_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.get, ['TestEnv', dl_name, '-f', 'json'])
        self.assert_no_errors(result)
        expected_output = '{'
        expected_output += '\n  \"id\": \"{0}\",'.format(dl_id)
        expected_output += '\n  \"name\": \"{0}\",'.format(dl_name)
        expected_output += '\n  \"resourceManager\": \"rm123\"'
        expected_output += '\n}'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_get_with_output_yaml_format(self):
        dl_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        dl_name = 'testdl'
        self.lm_sim.add_deployment_location({'id': dl_id, 'name': dl_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.get, ['TestEnv', dl_name, '-f', 'yaml'])
        self.assert_no_errors(result)
        expected_output = 'id: {0}'.format(dl_id)
        expected_output += '\nname: {0}'.format(dl_name)
        expected_output += '\nresourceManager: rm123\n'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)

    def test_list_with_defaults(self):
        dl_A_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        dl_A_name = 'testdl_a'
        self.lm_sim.add_deployment_location({'id': dl_A_id, 'name': dl_A_name, 'resourceManager': 'rm123'})
        dl_B_id = 'c502bc73-6278-42e0-a5e3-a0fe40674754'
        dl_B_name = 'testdl_b'
        self.lm_sim.add_deployment_location({'id': dl_B_id, 'name': dl_B_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.list_locations, ['TestEnv'])
        self.assert_no_errors(result)
        expected_output = '| id                                   | name     | resourceManager   | infrastructureType   | description   |'
        expected_output += '\n|--------------------------------------+----------+-------------------+----------------------+---------------|'
        expected_output += '\n| f801fa73-6278-42f0-b5d3-a0fe40675327 | testdl_a | rm123             |                      |               |'
        expected_output += '\n| c502bc73-6278-42e0-a5e3-a0fe40674754 | testdl_b | rm123             |                      |               |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_dl_driver = self.mock_create_lm_session.return_value.deployment_location_driver
        mock_dl_driver.get_locations.assert_called_once()
    
    def test_list_with_config(self):
        dl_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        dl_name = 'testdl'
        self.lm_sim.add_deployment_location({'id': dl_id, 'name': dl_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.list_locations, ['TestEnv', '--config', 'my/config/file'])
        self.assert_no_errors(result)
        expected_output = '| id                                   | name   | resourceManager   | infrastructureType   | description   |'
        expected_output += '\n|--------------------------------------+--------+-------------------+----------------------+---------------|'
        expected_output += '\n| {0} | testdl | rm123             |                      |               |'.format(dl_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, 'my/config/file')

    def test_get_with_pwd(self):
        dl_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        dl_name = 'testdl'
        self.lm_sim.add_deployment_location({'id': dl_id, 'name': dl_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.list_locations, ['TestEnv', '--pwd', 'secret'])
        self.assert_no_errors(result)
        expected_output = '| id                                   | name   | resourceManager   | infrastructureType   | description   |'
        expected_output += '\n|--------------------------------------+--------+-------------------+----------------------+---------------|'
        expected_output += '\n| {0} | testdl | rm123             |                      |               |'.format(dl_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', 'secret', None)

    def test_list_with_output_json_format(self):
        dl_A_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        dl_A_name = 'testdl_a'
        self.lm_sim.add_deployment_location({'id': dl_A_id, 'name': dl_A_name, 'resourceManager': 'rm123'})
        dl_B_id = 'c502bc73-6278-42e0-a5e3-a0fe40674754'
        dl_B_name = 'testdl_b'
        self.lm_sim.add_deployment_location({'id': dl_B_id, 'name': dl_B_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.list_locations, ['TestEnv', '-f', 'json'])
        self.assert_no_errors(result)
        expected_output = '{'
        expected_output += '\n  \"items\": ['
        expected_output += '\n    {'
        expected_output += '\n      \"id\": \"{0}\",'.format(dl_A_id)
        expected_output += '\n      \"name\": \"{0}\",'.format(dl_A_name)
        expected_output += '\n      \"resourceManager\": \"rm123\"'
        expected_output += '\n    },'
        expected_output += '\n    {'
        expected_output += '\n      \"id\": \"{0}\",'.format(dl_B_id)
        expected_output += '\n      \"name\": \"{0}\",'.format(dl_B_name)
        expected_output += '\n      \"resourceManager\": \"rm123\"'
        expected_output += '\n    }'
        expected_output += '\n  ]'
        expected_output += '\n}'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
    
    def test_list_with_output_yaml_format(self):
        dl_A_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        dl_A_name = 'testdl_a'
        self.lm_sim.add_deployment_location({'id': dl_A_id, 'name': dl_A_name, 'resourceManager': 'rm123'})
        dl_B_id = 'c502bc73-6278-42e0-a5e3-a0fe40674754'
        dl_B_name = 'testdl_b'
        self.lm_sim.add_deployment_location({'id': dl_B_id, 'name': dl_B_name, 'resourceManager': 'rm123'})
        result = self.runner.invoke(deployment_cmds.list_locations, ['TestEnv', '-f', 'yaml'])
        self.assert_no_errors(result)
        expected_output = 'items:'
        expected_output += '\n- id: {0}'.format(dl_A_id)
        expected_output += '\n  name: {0}'.format(dl_A_name)
        expected_output += '\n  resourceManager: rm123'
        expected_output += '\n- id: {0}'.format(dl_B_id)
        expected_output += '\n  name: {0}'.format(dl_B_name)
        expected_output += '\n  resourceManager: rm123\n'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
