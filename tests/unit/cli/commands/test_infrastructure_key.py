import os
import tempfile
import shutil
import tests.unit.cli.commands.command_testing as command_testing
import lmctl.drivers.lm.base as lm_drivers
import lmctl.cli.commands.infrastructure_key as infrastructure_key_cmds
from unittest.mock import patch
from tests.common.simulations.lm_simulator import LmSimulator

class TestInfrastructureKeyCommands(command_testing.CommandTestCase):

    def setUp(self):
        super().setUp()
        # Created simulated LM session when requested
        self.lm_sim = LmSimulator().start()
        create_lm_session_patcher = patch('lmctl.cli.ctlmgmt.create_lm_session')
        self.mock_create_lm_session = create_lm_session_patcher.start()
        self.mock_create_lm_session.return_value = self.lm_sim.as_mocked_session()
        self.addCleanup(create_lm_session_patcher.stop)

    def test_add_with_defaults(self):
        result = self.runner.invoke(infrastructure_key_cmds.add, ['TestEnv', 'testkey'])
        self.assert_no_errors(result)
        expected_id = None
        for ik_id, ik_driver in self.lm_sim.infrastructure_keys.items():
            expected_id = ik_id
        expected_output = '| id      | name    | description   | publicKey   |'
        expected_output += '\n|---------+---------+---------------+-------------|'
        expected_output += '\n| {0} | testkey |               |             |'.format(expected_id)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_infrastructure_keys_driver = self.mock_create_lm_session.return_value.infrastructure_keys_driver
        mock_infrastructure_keys_driver.add_infrastructure_key.assert_called_once_with({'name': 'testkey' })

    def test_add_with_keyfiles(self):
        tmp_dir = tempfile.mkdtemp()
        try:
            pubkey = 'ssh-rsa AAAAB3NzaC1QABAAABAQC2GhkoeKcWXG7Kp8K6AY49qmB5Yyc8CyhvQy8JYcp7FCCH3J+95cCmZ9cPXxPYHUPzPqTIbJEByFnEItIxBw22JOGFe3yx6GJOwLiKKOEgmDotbOpBOBLBIdZz8EEd2x+m1Dr9JgfzmpqWc2PFJRvxkK5NwMqJBk+7mnQwSNtlMjE/Es21pMYPu/QFyq6yjXpOaCt5G5HSuHSw5o6OW2AetXfjTp0QeXb90iYvtVPMECMpn33dttZ80TChR2oEtPDcjovugC/nYAYG7VlMirbtlZQi04eVmX2W5a/EYxvXUalUS1Hf6/pmsdxjY+rqHBkSEVbKbtLoNuty0SUSHXM3 Generated-by-Nova'
            pubkey_file = os.path.join(tmp_dir, 'testkey.pub')
            with open(pubkey_file, 'w') as f:
                f.write(pubkey)
                f.close()
            result = self.runner.invoke(infrastructure_key_cmds.add, ['TestEnv', 'testkey', '-u', pubkey_file])
            self.assert_no_errors(result)
            expected_id = None
            for ik_id, ik in self.lm_sim.infrastructure_keys.items():
                expected_id = ik_id
            expected_output = '| id      | name    | description   | publicKey                                                                                                                                                                                                                                                                                                                                                                                            |'
            expected_output += '\n|---------+---------+---------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|'
            expected_output += '\n| {0} | testkey |               | {1} |'.format(expected_id, pubkey)
            self.assert_output(result, expected_output)
            self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
            mock_dl_driver = self.mock_create_lm_session.return_value.infrastructure_keys_driver
            mock_dl_driver.add_infrastructure_key.assert_called_once_with({'name': 'testkey', 'publicKey': pubkey })
        finally:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)

    def test_get_with_defaults(self):
        ik_A_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        ik_A_name = 'testkey_a'
        self.lm_sim.add_infrastructure_key({'id': ik_A_id, 'name': ik_A_name })
        result = self.runner.invoke(infrastructure_key_cmds.get, ['TestEnv', ik_A_name])
        self.assert_no_errors(result)
        expected_output = '| id                                   | name      | description   | publicKey   |'
        expected_output += '\n|--------------------------------------+-----------+---------------+-------------|'
        expected_output += '\n| f801fa73-6278-42f0-b5d3-a0fe40675327 | testkey_a |               |             |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_infrastructure_keys_driver = self.mock_create_lm_session.return_value.infrastructure_keys_driver
        mock_infrastructure_keys_driver.get_infrastructure_key_by_name.assert_called_once_with(ik_A_name)

    def test_list_with_defaults(self):
        ik_A_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        ik_A_name = 'testkey_a'
        self.lm_sim.add_infrastructure_key({'id': ik_A_id, 'name': ik_A_name })
        ik_B_id = 'c502bc73-6278-42e0-a5e3-a0fe40674754'
        ik_B_name = 'testkey_b'
        self.lm_sim.add_infrastructure_key({'id': ik_B_id, 'name': ik_B_name })
        result = self.runner.invoke(infrastructure_key_cmds.list_keys, ['TestEnv'])
        self.assert_no_errors(result)
        expected_output = '| id                                   | name      | description   | publicKey   |'
        expected_output += '\n|--------------------------------------+-----------+---------------+-------------|'
        expected_output += '\n| f801fa73-6278-42f0-b5d3-a0fe40675327 | testkey_a |               |             |'
        expected_output += '\n| c502bc73-6278-42e0-a5e3-a0fe40674754 | testkey_b |               |             |'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_infrastructure_keys_driver = self.mock_create_lm_session.return_value.infrastructure_keys_driver
        mock_infrastructure_keys_driver.get_infrastructure_keys.assert_called_once()

    def test_delete_with_defaults(self):
        ik_id = 'f801fa73-6278-42f0-b5d3-a0fe40675327'
        ik_name = 'testkey'
        self.lm_sim.add_infrastructure_key({'name': ik_name })
        result = self.runner.invoke(infrastructure_key_cmds.delete, ['TestEnv', ik_name])
        self.assert_no_errors(result)
        expected_output = 'Deleting infrastructure key: {0}...'.format(ik_name)
        expected_output += '\nDeleted infrastructure key: {0}'.format(ik_name)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None )
        mock_infrastructure_keys_driver = self.mock_create_lm_session.return_value.infrastructure_keys_driver
        mock_infrastructure_keys_driver.delete_infrastructure_key.assert_called_once_with(ik_name)

    def test_delete_none_found(self):
        ik_name = 'testkey'
        result = self.runner.invoke(infrastructure_key_cmds.delete, ['TestEnv', ik_name])
        expected_output = 'Error: No infrastructure key with name: {0}'.format(ik_name)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
        mock_infrastructure_keys_driver = self.mock_create_lm_session.return_value.infrastructure_keys_driver

    def test_list_with_output_json_format(self):
        ik_A_id = 'testkey_a'
        ik_A_name = 'testkey_a'
        self.lm_sim.add_infrastructure_key({'id': ik_A_id, 'name': ik_A_name})
        ik_B_id = 'testkey_b'
        ik_B_name = 'testkey_b'
        self.lm_sim.add_infrastructure_key({'id': ik_B_id, 'name': ik_B_name})
        result = self.runner.invoke(infrastructure_key_cmds.list_keys, ['TestEnv', '-f', 'json'])
        self.assert_no_errors(result)
        expected_output = '{'
        expected_output += '\n  \"items\": ['
        expected_output += '\n    {'
        expected_output += '\n      \"id\": \"{0}\",'.format(ik_A_id)
        expected_output += '\n      \"name\": \"{0}\"'.format(ik_A_name)
        expected_output += '\n    },'
        expected_output += '\n    {'
        expected_output += '\n      \"id\": \"{0}\",'.format(ik_B_id)
        expected_output += '\n      \"name\": \"{0}\"'.format(ik_B_name)
        expected_output += '\n    }'
        expected_output += '\n  ]'
        expected_output += '\n}'
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)


    def test_list_with_output_yaml_format(self):
        ik_A_id = 'testkey_a'
        ik_A_name = 'testkey_a'
        self.lm_sim.add_infrastructure_key({'id': ik_A_id, 'name': ik_A_name})
        ik_B_id = 'testkey_b'
        ik_B_name = 'testkey_b'
        self.lm_sim.add_infrastructure_key({'id': ik_B_id, 'name': ik_B_name})
        result = self.runner.invoke(infrastructure_key_cmds.list_keys, ['TestEnv', '-f', 'yaml'])
        self.assert_no_errors(result)
        expected_output = 'items:'
        expected_output += '\n- id: {0}'.format(ik_A_id)
        expected_output += '\n  name: {0}'.format(ik_A_name)
        expected_output += '\n- id: {0}'.format(ik_B_id)
        expected_output += '\n  name: {0}\n'.format(ik_B_name)
        self.assert_output(result, expected_output)
        self.mock_create_lm_session.assert_called_once_with('TestEnv', None, None)
