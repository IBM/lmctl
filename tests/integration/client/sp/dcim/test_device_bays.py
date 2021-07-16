from tests.integration.client.sp.common_tests import SitePlannerAPITests
from tests.integration.client.sp.utils import DeviceSetup
from lmctl.client import SitePlannerClientError


class TestDeviceBaysAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.device_setup = DeviceSetup('test-device-bays', tester)
        cls.child_device_type = tester.default_sp_client.dcim.device_types.create({
            'manufacturer': cls.device_setup.manufacturer['id'], 
            'model': tester.short_exec_prepended_name('test-device-bays-ch', limit=50), 
            'slug': tester.short_exec_prepended_name('test-device-bays-ch', limit=50),
            'u_height': 0,
            'subdevice_role': 'child'
        })
        cls.child_device = tester.default_sp_client.dcim.devices.create({
            'name': tester.short_exec_prepended_name('test-pr-device-ch'),
            'device_type': cls.child_device_type['id'],
            'device_role': cls.device_setup.device_role['id'],
            'asset_tag': tester.short_exec_prepended_name('test-pr-device-ch'),
            'site': cls.device_setup.site['id'],
            'status': 'active'
        })

    @classmethod
    def after_test_case(cls, tester):
        tester.default_sp_client.dcim.devices.delete(cls.child_device['id'])
        tester.default_sp_client.dcim.device_types.delete(cls.child_device_type['id'])
        cls.device_setup.destroy()

    def _get_api(self, sp_client):
        return sp_client.dcim.device_bays

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-device-bay-crud'),
            'device': self.device_setup.device['id'],
            'description': 'Test bay',
            'installed_device': self.child_device['id'],
            'tags': ['testing', 'lmctl']
        }

    def _build_update_data(self, obj):
        obj['description'] = 'This is an updated device bay'
        return obj
