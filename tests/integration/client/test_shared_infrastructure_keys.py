import time
from tests.integration.integration_test_base import IntegrationTest

class TestSharedInfrastructureKeysAPI(IntegrationTest):

    def test_crud(self):
        pubkey = 'ssh-rsa AAAAB3NzaC1QABAAABAQC2GhkoeKcWXG7Kp8K6AY49qmB5Yyc8CyhvQy8JYcp7FCCH3J+95cCmZ9cPXxPYHUPzPqTIbJEByFnEItIxBw22JOGFe3yx6GJOwLiKKOEgmDotbOpBOBLBIdZz8EEd2x+m1Dr9JgfzmpqWc2PFJRvxkK5NwMqJBk+7mnQwSNtlMjE/Es21pMYPu/QFyq6yjXpOaCt5G5HSuHSw5o6OW2AetXfjTp0QeXb90iYvtVPMECMpn33dttZ80TChR2oEtPDcjovugC/nYAYG7VlMirbtlZQi04eVmX2W5a/EYxvXUalUS1Hf6/pmsdxjY+rqHBkSEVbKbtLoNuty0SUSHXM3 Generated-by-Nova'
        inf_key = {
            'name': self.tester.exec_prepended_name('inf-key-crud'),
            'publicKey': pubkey
        }
        ## Create
        create_response = self.tester.default_client.shared_inf_keys.create(inf_key)
        self.assertIn('name', create_response)
        inf_key_id = create_response['name']
        ## Read
        get_response = self.tester.default_client.shared_inf_keys.get(inf_key_id)
        self.assertIsNotNone(get_response)
        self.assertEqual(get_response['name'], inf_key['name'])
        self.assertEqual(get_response['publicKey'], inf_key['publicKey'])
        ## Update
        updated_inf_key = get_response.copy()
        updated_pubkey = 'ssh-rsa AAAAB3NzaC1QABCCCBAQC2GjauiKcWXG7Kp8K6AY49qmB5Yyc8CyhvQy8JYcp7FCCH3J+95cCmZ9cPXxPYHUPzPqTIbJEByFnEItIxBw22JOGFe3yx6GJOwLiKKOEgmDotbOpBOBLBIdZz8EEd2x+m1Dr9JgfzmpqWc2PFJRvxkK5NwMqJBk+7mnQwSNtlMjE/Es21pMYPu/QFyq6yjXpOaCt5G5HSuHSw5o6OW2AetXfjTp0QeXb90iYvtVPMECMpn33dttZ80TChR2oEtPDcjovugC/nYAYG7VlMirbtlZQi04eVmX2W5a/EYxvXUalUS1Hf6/pmsdxjY+rqHBkSEVbKbtLoNuty0SUSHXM3 Generated-by-Nova'
        updated_inf_key['publicKey'] = updated_pubkey
        update_response = self.tester.default_client.shared_inf_keys.update(updated_inf_key)
        self.assertIsNone(update_response)
        get_response = self.tester.default_client.shared_inf_keys.get(inf_key_id)
        self.assertEqual(get_response['publicKey'], updated_pubkey)
        ## Delete
        delete_response = self.tester.default_client.shared_inf_keys.delete(inf_key_id)
        self.assertIsNone(delete_response)

    def test_all(self):
        inf_key_A = {
            'name': self.tester.exec_prepended_name('inf-key-all-A')
        }
        self.tester.default_client.shared_inf_keys.create(inf_key_A)
        inf_key_B = {
            'name': self.tester.exec_prepended_name('inf-key-all-B')
        }
        self.tester.default_client.shared_inf_keys.create(inf_key_B)
        time.sleep(1)
        all_response = self.tester.default_client.shared_inf_keys.all()
        # Might be other keys
        self.assertTrue(len(all_response) > 0)
        names = []
        for key in all_response:
            names.append(key['name'])
        self.assertIn(inf_key_A['name'], names)
        self.assertIn(inf_key_B['name'], names)
        self.tester.default_client.shared_inf_keys.delete(inf_key_A['name'])
        self.tester.default_client.shared_inf_keys.delete(inf_key_B['name'])
