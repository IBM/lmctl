from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from lmctl.client import SitePlannerClientError

class TestDeviceRolesAPI(SitePlannerAPITests.CRUDTest):

    def _get_api(self, sp_client):
        return sp_client.dcim.device_roles

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-devroles-crud'), 
            'slug': self.tester.short_exec_prepended_name('test-devroles-crud'),
            'description': 'Test device role',
            'color': '9e9e9e',
            'vm_role': True
        }

    def _build_update_data(self, obj):
        obj['description'] = 'Updated description'
        obj['color'] = '000000'
        return obj
