from tests.integration.integration_test_base import IntegrationTest
from lmctl.client import SitePlannerClientError


class SitePlannerAPITests:

    class CRUDTest(IntegrationTest):
        _pk_field = 'id'
        _compare_ignore_fields = ['created', 'last_updated']
        _compare_relation_fields = []

        def _get_api(self, sp_client):
            raise NotImplementedError()

        def _build_create_data(self):
            raise NotImplementedError()
        
        def _build_update_data(self, obj):
            raise NotImplementedError()

        def _compare(self, sent_data, retrieved_data, is_update=False):
            for k,v in sent_data.items():
                self._compare_field(k, sent_data.get(k), retrieved_data.get(k, None))

        def _compare_field(self, field_name, expected_value, retrieved_value):
            if field_name not in self._compare_ignore_fields:
                api = self._get_api(self.tester.default_sp_client)
                if field_name in api._relation_fields and retrieved_value is not None:
                    if isinstance(retrieved_value, list):
                        retrieved_value = [r.get('id', None) for r in retrieved_value]
                        retrieved_value.sort()
                        expected_value = [e.get('id', None) if isinstance(e, dict) else e for e in expected_value]
                        expected_value.sort()
                    else:
                        retrieved_value = retrieved_value.get('id', None)
                        expected_value = expected_value.get('id', None) if isinstance(expected_value, dict) else expected_value
                elif isinstance(retrieved_value, dict) and 'value' in retrieved_value.keys() and 'label' in retrieved_value.keys():
                    retrieved_value = retrieved_value.get('value', None)
                if isinstance(expected_value, dict) and 'value' in expected_value.keys() and 'label' in expected_value.keys():
                    expected_value = expected_value.get('value', None)
                self.assertEqual(retrieved_value, expected_value, msg=f'Assertion failure on field {field_name}')

        def test_crud(self):
            obj = self._build_create_data()

            api = self._get_api(self.tester.default_sp_client)
            
            ## Create
            create_response = api.create(obj)
            self.assertIn(self._pk_field, create_response)
            pk_value = create_response.get(self._pk_field)

            ## Read
            get_response = api.get(pk_value)
            self.assertIsNotNone(get_response)
            self._compare(obj, get_response)

            ## Update
            updated_obj = self._build_update_data(get_response.copy())
            api.update(updated_obj)
            get_response = api.get(pk_value)
            self._compare(updated_obj, get_response, is_update=True)

            ## Delete
            delete_response = api.delete(pk_value)
            self.assertIsNone(delete_response)

            with self.assertRaises(SitePlannerClientError) as ctx:
                api.get(pk_value)
            self.assertEqual(str(ctx.exception), f'Could not find object with {self._pk_field}: {pk_value}')
        