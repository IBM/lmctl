from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from lmctl.client import SitePlannerClientError

class TestDeviceTypesAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.manufacturer = tester.default_sp_client.dcim.manufacturers.create({'name': tester.short_exec_prepended_name('test-devtypes'), 'slug': tester.short_exec_prepended_name('test-devtypes')})
       
    @classmethod
    def after_test_case(cls, tester):
        tester.default_sp_client.dcim.manufacturers.delete(cls.manufacturer['id'])

    def _get_api(self, sp_client):
        return sp_client.dcim.device_types

    def _build_create_data(self):
        return {
            'manufacturer': self.manufacturer['id'],
            'model': self.tester.short_exec_prepended_name('test-devtypes-crud', limit=50), 
            'slug': self.tester.short_exec_prepended_name('test-devtypes-crud', limit=50),
            'part_number': '123',
            'u_height': 1,
            'is_full_depth': True,
            'subdevice_role': 'parent',
            'comments': 'Test device type',
            'tags': ['testing', 'lmctl']
        }

    def _build_update_data(self, obj):
        obj['comments'] = 'Updated comments'
        return obj
