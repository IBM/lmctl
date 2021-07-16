

class DeviceSetup:

    def __init__(self, name, tester):
        self.tester = tester
        self.site = tester.default_sp_client.dcim.sites.create({'name': tester.short_exec_prepended_name(name), 'slug': tester.short_exec_prepended_name(name)})
        self.rack = tester.default_sp_client.dcim.racks.create({'name': tester.short_exec_prepended_name(name), 'status': 'active', 'width': 10, 'u_height': 42, 'site': self.site['id']})
        self.device_role = tester.default_sp_client.dcim.device_roles.create({'name': tester.short_exec_prepended_name(name), 'slug': tester.short_exec_prepended_name(name), 'color': '000000'})
        self.manufacturer = tester.default_sp_client.dcim.manufacturers.create({'name': tester.short_exec_prepended_name(name), 'slug': tester.short_exec_prepended_name(name)})
        self.device_type = tester.default_sp_client.dcim.device_types.create({
            'manufacturer': self.manufacturer['id'], 
            'model': tester.short_exec_prepended_name(name, limit=50), 
            'slug': tester.short_exec_prepended_name(name, limit=50),
            'u_height': 1,
            'subdevice_role': 'parent'
        })
        self.device = tester.default_sp_client.dcim.devices.create({
            'name': tester.short_exec_prepended_name(name),
            'device_type': self.device_type['id'],
            'device_role': self.device_role['id'],
            'serial': '123',
            'asset_tag': self.tester.short_exec_prepended_name(name),
            'site': self.site['id'],
            'rack': self.rack['id'],
            'position': 1,
            'face': 'front',
            'status': 'active',
            'comments': 'Test device'
        })

    def destroy(self):        
        self.tester.default_sp_client.dcim.devices.delete(self.device['id'])
        self.tester.default_sp_client.dcim.device_types.delete(self.device_type['id'])
        self.tester.default_sp_client.dcim.manufacturers.delete(self.manufacturer['id'])
        self.tester.default_sp_client.dcim.device_roles.delete(self.device_role['id'])
        self.tester.default_sp_client.dcim.racks.delete(self.rack['id'])
        self.tester.default_sp_client.dcim.sites.delete(self.site['id'])
        