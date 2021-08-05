from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from lmctl.client import SitePlannerClientError


class TestDeviceBayTemplatesAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.manufacturer = tester.default_sp_client.dcim.manufacturers.create({'name': tester.short_exec_prepended_name('test-dbay-tmpl'), 'slug': tester.short_exec_prepended_name('test-dbay-tmpl')})
        cls.device_type = tester.default_sp_client.dcim.device_types.create({
            'manufacturer': cls.manufacturer['id'], 
            'model': tester.short_exec_prepended_name('test-dbay-tmpl', limit=50), 
            'slug': tester.short_exec_prepended_name('test-dbay-tmpl', limit=50),
            'u_height': 1,
            'subdevice_role': 'parent'
        })

    @classmethod
    def after_test_case(cls, tester):
        tester.default_sp_client.dcim.device_types.delete(cls.device_type['id'])
        tester.default_sp_client.dcim.manufacturers.delete(cls.manufacturer['id'])
        
    def _get_api(self, sp_client):
        return sp_client.dcim.device_bay_templates

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-dbay-tmpl-crud'),
            'device_type': self.device_type['id']
        }

    def _build_update_data(self, obj):
        obj['name'] = self.tester.short_exec_prepended_name('test-dbay-tmpl-upd')
        return obj

