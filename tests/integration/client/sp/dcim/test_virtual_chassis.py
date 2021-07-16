from tests.integration.client.sp.common_tests import SitePlannerAPITests
from tests.integration.client.sp.utils import DeviceSetup
from lmctl.client import SitePlannerClientError

class TestVirtualChassisAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.device_setup = DeviceSetup('test-device-bays', tester)

    @classmethod
    def after_test_case(cls, tester):
        cls.device_setup.destroy()

    def _get_api(self, sp_client):
        return sp_client.dcim.virtual_chassis

    def _build_create_data(self):
        return {
            'master': self.device_setup.device['id'],
            'domain': 'example'
        }

    def _build_update_data(self, obj):
        obj['domain'] = 'updated-example'
        return obj
