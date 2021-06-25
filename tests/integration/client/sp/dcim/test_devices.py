from tests.integration.client.sp.common_tests import SitePlannerAPITests
from lmctl.client import SitePlannerClientError
import ipaddress
import random

class TestDevicesAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.site = tester.default_sp_client.dcim.sites.create({'name': tester.short_exec_prepended_name('test-devices'), 'slug': tester.short_exec_prepended_name('test-devices')})
        cls.rack = tester.default_sp_client.dcim.racks.create({'name': tester.short_exec_prepended_name('test-devices'), 'status': 'active', 'width': 10, 'u_height': 42, 'site': cls.site['id']})
        cls.tenant = tester.default_sp_client.tenancy.tenants.create({'name': tester.short_exec_prepended_name('test-devices'), 'slug': tester.short_exec_prepended_name('test-devices')})
        cls.device_role = tester.default_sp_client.dcim.device_roles.create({'name': tester.short_exec_prepended_name('test-devices'), 'slug': tester.short_exec_prepended_name('test-devices'), 'color': '000000'})
        cls.manufacturer = tester.default_sp_client.dcim.manufacturers.create({'name': tester.short_exec_prepended_name('test-devices'), 'slug': tester.short_exec_prepended_name('test-devices')})
        cls.device_type = tester.default_sp_client.dcim.device_types.create({
            'manufacturer': cls.manufacturer['id'], 
            'model': tester.short_exec_prepended_name('test-devices', limit=50), 
            'slug': tester.short_exec_prepended_name('test-devices', limit=50),
            'u_height': 1
        })
        cls.platform = tester.default_sp_client.dcim.platforms.create({'name': tester.short_exec_prepended_name('test-devices'), 'slug': tester.short_exec_prepended_name('test-devices')})
        cls.cluster_type = tester.default_sp_client.virtualization.cluster_types.create({'name': tester.short_exec_prepended_name('test-devices'), 'slug': tester.short_exec_prepended_name('test-devices')})
        cls.cluster = tester.default_sp_client.virtualization.clusters.create({'name': tester.short_exec_prepended_name('test-devices'), 'type': cls.cluster_type['id']})

    #TODO test Virtual Chassis, Parent Device and IP addresses

    @classmethod
    def after_test_case(cls, tester):
        tester.default_sp_client.virtualization.clusters.delete(cls.cluster['id'])
        tester.default_sp_client.virtualization.cluster_types.delete(cls.cluster_type['id'])
        tester.default_sp_client.dcim.platforms.delete(cls.platform['id'])
        tester.default_sp_client.dcim.device_types.delete(cls.device_type['id'])
        tester.default_sp_client.dcim.manufacturers.delete(cls.manufacturer['id'])
        tester.default_sp_client.dcim.device_roles.delete(cls.device_role['id'])
        tester.default_sp_client.dcim.racks.delete(cls.rack['id'])
        tester.default_sp_client.dcim.sites.delete(cls.site['id'])
        tester.default_sp_client.tenancy.tenants.delete(cls.tenant['id'])
        
    def _get_api(self, sp_client):
        return sp_client.dcim.devices

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-device-crud'),
            'device_type': self.device_type['id'],
            'device_role': self.device_role['id'],
            'tenant': self.tenant['id'],
            'platform': self.platform['id'],
            'serial': '123',
            'asset_tag': self.tester.short_exec_prepended_name('test-device-crud'),
            'site': self.site['id'],
            'rack': self.rack['id'],
            'position': 1,
            'face': 'front',
            'status': 'active',
            'cluster': self.cluster['id'],
            'comments': 'Test device',
            'local_context_data': {'testing': 'true'},
            'tags': ['testing', 'lmctl']
        }

    def _build_update_data(self, obj):
        obj['comments'] = 'This is an updated lmctl test device'
        return obj


    def test_ip_addresses(self):
        device = {
            'name': self.tester.short_exec_prepended_name('test-device-ipaddr'),
            'device_type': self.device_type['id'],
            'device_role': self.device_role['id'],
            'asset_tag': self.tester.short_exec_prepended_name('test-device-crud'),
            'site': self.site['id'],
            'rack': self.rack['id'],
            'position': 1,
            'face': 'front',
            'status': 'active'
        }

        device_api = self._get_api(self.tester.default_sp_client)
        interface_api = self.tester.default_sp_client.dcim.interfaces
        ip_addr_api = self.tester.default_sp_client.ipam.ip_addresses

        # Create Device
        device = device_api.create(device)

        # Create Interfaces
        interface_a = interface_api.create({'device': device['id'], 'name': self.tester.short_exec_prepended_name('test-device-ipaddr-A'), 'type': '10gbase-t'})
        interface_b = interface_api.create({'device': device['id'], 'name': self.tester.short_exec_prepended_name('test-device-ipaddr-B'), 'type': '10gbase-t'})

        # Create IPAddrs
        ipv4_address = ipaddress.IPv4Address._string_from_ip_int(random.randint(0, ipaddress.IPv4Address._ALL_ONES))
        ipv4 = ip_addr_api.create({'address': ipv4_address, 'status': 'active', 'interface': interface_a['id']})
        ipv6_address = ipaddress.IPv6Address._string_from_ip_int(random.randint(0, ipaddress.IPv6Address._ALL_ONES))
        ipv6 = ip_addr_api.create({'address': ipv6_address, 'status': 'active', 'interface': interface_b['id']})

        # Set primary IPs on Device
        device = device_api.get(device['id'])
        device['primary_ip4'] = ipv4['id']
        device['primary_ip6'] = ipv6['id']
        device_api.update(device)

        get_response = device_api.get(device['id'])
        self.assertEqual(get_response['primary_ip']['id'], ipv6['id'])
        self.assertEqual(get_response['primary_ip4']['id'], ipv4['id'])
        self.assertEqual(get_response['primary_ip6']['id'], ipv6['id'])

        # Cleanup
        ip_addr_api.delete(ipv4['id'])
        ip_addr_api.delete(ipv6['id'])
        interface_api.delete(interface_a['id'])
        interface_api.delete(interface_b['id'])
        device_api.delete(device['id'])

        

        
