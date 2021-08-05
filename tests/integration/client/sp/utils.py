import os

class TNCOAutomationSetup:

    def __init__(self, name, tester):
        self.tester = tester
        ## Add deployment location
        self.deployment_location = tester.default_client.deployment_locations.create({
            'name': tester.exec_prepended_name(name),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        })
        ## Upload Resource package
        res_pkg_path = tester.tmp_file('dummy_resource.zip')
        tester.build_resource_package_from(tester.test_file('dummy_resource'), res_pkg_path, suffix=name)
        self.res_pkg_id = tester.default_client.resource_packages.create(res_pkg_path)
        ## Get Resource descriptor 
        self.resource_descriptor = tester.load_descriptor_from(tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix=name)
        ## Add Assembly descriptor
        self.assembly_descriptor = tester.load_descriptor_from(tester.test_file('managed_entity_assembly.yaml'), suffix=name)
        self.assembly_descriptor['properties']['resourceManager']['default'] = 'brent'
        self.assembly_descriptor['properties']['deploymentLocation']['default'] = self.deployment_location['name']
        tester.default_client.descriptors.create(self.assembly_descriptor)

    def destroy(self):
        self.tester.default_client.deployment_locations.delete(self.deployment_location['id'])
        self.tester.default_client.resource_packages.delete(self.res_pkg_id)
        self.tester.default_client.descriptors.delete(self.resource_descriptor['name'])
        self.tester.default_client.descriptors.delete(self.assembly_descriptor['name'])


class ManagedEntityTypeSetup(TNCOAutomationSetup):
    def __init__(self, name, tester):
        super().__init__(name, tester)
        self.managed_entity_type = tester.default_sp_client.nfvo_automation.managed_entity_types.create({
            'descriptor': self.assembly_descriptor['name'],
            'comments': 'Test type',
            'tags': ['testing', 'lmctl']
        })

    def destroy(self):
        super().destroy()
        self.tester.default_sp_client.nfvo_automation.managed_entity_types.delete(self.managed_entity_type['id'])

class ManagedEntitySetup(ManagedEntityTypeSetup):
    def __init__(self, name, tester):
        super().__init__(name, tester)
        self.managed_entity = tester.default_sp_client.nfvo_automation.managed_entities.create({
            'name': self.tester.short_exec_prepended_name(name),
            'type': self.managed_entity_type['id'],
            'status': 'active',
            'properties': {
                'dummyProp': 'test',
                'dummyIntProp': 42,
            },
            'comments': 'Test',
            'tags': ['testing', 'lmctl']
        })

    def destroy(self):
        self.tester.default_sp_client.nfvo_automation.managed_entities.delete(self.managed_entity['id'])
        super().destroy()


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
        