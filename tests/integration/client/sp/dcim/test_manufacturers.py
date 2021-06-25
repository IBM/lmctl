from tests.integration.client.sp.common_tests import SitePlannerAPITests
from lmctl.client import SitePlannerClientError

class TestManufacturersAPI(SitePlannerAPITests.CRUDTest):

    def _get_api(self, sp_client):
        return sp_client.dcim.manufacturers

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-manf-crud'), 
            'slug': self.tester.short_exec_prepended_name('test-manf-crud'),
            'description': 'Test manufacturer'
        }

    def _build_update_data(self, obj):
        obj['description'] = 'Updated description'
        return obj
