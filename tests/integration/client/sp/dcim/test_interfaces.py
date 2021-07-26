import random
from tests.integration.client.sp.common_tests import SitePlannerAPITests
from tests.integration.client.sp.utils import DeviceSetup
from lmctl.client import SitePlannerClientError

class TestInterfacesAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.device_setup = DeviceSetup('test-interfaces', tester)
        cls.vlan_1 = tester.default_sp_client.ipam.vlans.create({'name': tester.short_exec_prepended_name('test-ifaces-vlan1'), 'vid': random.randint(1,4000)})
        cls.vlan_2 = tester.default_sp_client.ipam.vlans.create({'name': tester.short_exec_prepended_name('test-ifaces-vlan2'), 'vid': random.randint(1,4000)})
        cls.vlan_3 = tester.default_sp_client.ipam.vlans.create({'name': tester.short_exec_prepended_name('test-ifaces-vlan3'), 'vid': random.randint(1,4000)})
        cls.vlan_4 = tester.default_sp_client.ipam.vlans.create({'name': tester.short_exec_prepended_name('test-ifaces-vlan4'), 'vid': random.randint(1,4000)})

    @classmethod
    def after_test_case(cls, tester):
        cls.device_setup.destroy()

    def _get_api(self, sp_client):
        return sp_client.dcim.interfaces

    def _build_create_data(self):
        return {
            'device': self.device_setup.device['id'],
            'name': self.tester.short_exec_prepended_name('test-interfaces-crud'),
            'type': '10gbase-t',
            'enabled': True,
            'mtu': 1000,
            'mac_address': '2C:54:91:88:C9:E3',
            'mgmt_only': False,
            'description': 'Testing',
            'mode': 'access',
            'untagged_vlan': self.vlan_1['id'],
            'tagged_vlans': [self.vlan_2['id'], self.vlan_3['id'], self.vlan_4['id']],
            'tags': ['lmctl', 'testing']
        }

    def _build_update_data(self, obj):
        obj['description'] = 'Updated description'
        return obj
