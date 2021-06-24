from tests.integration.client.sp.common_tests import SitePlannerAPITests
from lmctl.client import SitePlannerClientError

class TestRackRolesAPI(SitePlannerAPITests.CRUDTest):

    def _get_api(self, sp_client):
        return sp_client.dcim.rack_roles

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-rroles-crud'), 
            'slug': self.tester.short_exec_prepended_name('test-rroles-crud'),
            'description': 'Test rack role',
            'color': '9e9e9e'
        }

    def _build_update_data(self, obj):
        obj['description'] = 'Updated description'
        obj['color'] = '000000'
        return obj
