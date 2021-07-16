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
            'u_height': 1,
            'subdevice_role': 'parent'
        })
        cls.platform = tester.default_sp_client.dcim.platforms.create({'name': tester.short_exec_prepended_name('test-devices'), 'slug': tester.short_exec_prepended_name('test-devices')})
        cls.cluster_type = tester.default_sp_client.virtualization.cluster_types.create({'name': tester.short_exec_prepended_name('test-devices'), 'slug': tester.short_exec_prepended_name('test-devices')})
        cls.cluster = tester.default_sp_client.virtualization.clusters.create({'name': tester.short_exec_prepended_name('test-devices'), 'type': cls.cluster_type['id']})

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

    def test_parent_device(self):
        device_api = self._get_api(self.tester.default_sp_client)
        device_type_api = self.tester.default_sp_client.dcim.device_types
        device_bay_api = self.tester.default_sp_client.dcim.device_bays

        # Create child DeviceType
        child_device_type = device_type_api.create({
            'manufacturer': self.manufacturer['id'], 
            'model': self.tester.short_exec_prepended_name('test-pr-device', limit=50), 
            'slug': self.tester.short_exec_prepended_name('test-pr-device', limit=50),
            'u_height': 0,
            'subdevice_role': 'child'
        })

        # Create Parent Device
        parent_device = device_api.create({
            'name': self.tester.short_exec_prepended_name('test-pr-device-pr'),
            'device_type': self.device_type['id'],
            'device_role': self.device_role['id'],
            'asset_tag': self.tester.short_exec_prepended_name('test-pr-device-pr'),
            'site': self.site['id'],
            'rack': self.rack['id'],
            'position': 1,
            'face': 'front',
            'status': 'active'
        })

        # Create Child Device
        child_device = device_api.create({
            'name': self.tester.short_exec_prepended_name('test-pr-device-ch'),
            'device_type': child_device_type['id'],
            'device_role': self.device_role['id'],
            'asset_tag': self.tester.short_exec_prepended_name('test-pr-device-ch'),
            'site': self.site['id'],
            'status': 'active'
        })

        # Create Device Bay
        device_bay = device_bay_api.create({
            'device': parent_device['id'],
            'name': self.tester.short_exec_prepended_name('test-pr-device-bay'),
            'installed_device': child_device['id']
        })

        # Check Child
        get_child_response = device_api.get(child_device['id'])
        self.assertEqual(get_child_response['parent_device']['id'], parent_device['id'])
        
        # Cleanup
        device_bay_api.delete(device_bay['id'])
        device_api.delete(child_device['id'])
        device_api.delete(parent_device['id'])
        device_type_api.delete(child_device_type['id'])
        

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

    def test_virtual_chassis(self):
        device_api = self._get_api(self.tester.default_sp_client)
        virtual_chassis_api = self.tester.default_sp_client.dcim.virtual_chassis

        # Create Master Device
        master_device = device_api.create({
            'name': self.tester.short_exec_prepended_name('test-vchass-master'),
            'device_type': self.device_type['id'],
            'device_role': self.device_role['id'],
            'asset_tag': self.tester.short_exec_prepended_name('test-vchass-master'),
            'site': self.site['id'],
            'rack': self.rack['id'],
            'position': 1,
            'face': 'front',
            'status': 'active',
            'vc_position': 1,
            'vc_priority': 1
        })

        # Create Virtual Chassis
        vchass = virtual_chassis_api.create({
            'master': master_device['id'],
            'domain': 'example'
        })

        # Create another device
        other_device = device_api.create({
            'name': self.tester.short_exec_prepended_name('test-vchass-other'),
            'device_type': self.device_type['id'],
            'device_role': self.device_role['id'],
            'asset_tag': self.tester.short_exec_prepended_name('test-vchass-other'),
            'site': self.site['id'],
            'rack': self.rack['id'],
            'position': 2,
            'face': 'front',
            'status': 'active',
            'virtual_chassis': vchass['id'],
            'vc_position': 2,
            'vc_priority': 2
        })

        # Check Device
        get_other_device = device_api.get(other_device['id'])
        self.assertEqual(other_device['virtual_chassis']['id'], vchass['id'])
        
        # Cleanup
        virtual_chassis_api.delete(vchass['id'])
        device_api.delete(other_device['id'])
        device_api.delete(master_device['id'])
