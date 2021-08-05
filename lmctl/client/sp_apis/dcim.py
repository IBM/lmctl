from .sp_api_base import SitePlannerAPIGroup, SitePlannerCrudAPI
from .automation_context import AutomationContextAPIMixin

class CablesAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'dcim.cables'

    _object_type = 'dcim.cable'

# TODO connected-device, console-connections, interface-connections, power-connections

class ConsolePortTemplatesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.console_port_templates'
    _relation_fields = ['device_type']

class ConsolePortsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.console_ports'
    _relation_fields = ['device', 'cable']

class ConsoleServerPortTemplatesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.console_server_port_templates'
    _relation_fields = ['device_type']

class ConsoleServerPortsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.console_server_ports'
    _relation_fields = ['device', 'cable']

class DeviceBayTemplatesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.device_bay_templates'
    _relation_fields = ['device_type']

class DeviceBaysAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.device_bays'
    _relation_fields = ['device', 'installed_device']

class DeviceRolesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.device_roles'

class DeviceTypesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.device_types'
    _relation_fields = ['manufacturer']
    _ignore_fields_on_update = ['front_image', 'rear_image']

class DevicesAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'dcim.devices'
    _relation_fields = ['device_type', 'device_role', 'tenant', 'platform', 'site', 'rack', 'parent_device', 'primary_ip4', 'primary_ip6', 'cluster', 'virtual_chassis']
    
    _object_type = 'dcim.device'

class FrontPortTemplatesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.front_port_templates'
    _relation_fields = ['device_type', 'rear_port']

class FrontPortsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.front_ports'
    _relation_fields = ['device_type', 'rear_port', 'cable']

class InterfaceTemplatesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.interface_templates'
    _relation_fields = ['device_type']

class InterfacesAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'dcim.interfaces'
    _relation_fields = ['device', 'lag', 'untagged_vlan', 'tagged_vlans']

    _object_type = 'dcim.interface'

class InventoryItemsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.inventory_items'
    _relation_fields = ['device', 'manufacturer']

class ManufacturersAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.manufacturers'

class PlatformsAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'dcim.platforms'
    _relation_fields = ['manufacturer']

    _object_type = 'dcim.platform'

class PowerFeedsAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'dcim.power_feeds'
    _relation_fields = ['power_panel', 'rack']

    _object_type = 'dcim.powerfeed'

class PowerOutletTemplatesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.power_outlet_templates'
    _relation_fields = ['device_type', 'power_port']

class PowerOutletsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.power_outlets'
    _relation_fields = ['device', 'power_port', 'cable']

class PowerPanelsAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'dcim.power_panels'
    _relation_fields = ['site', 'rack_group']

    _object_type = 'dcim.powerpanel'

class PowerPortTemplatesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.power_port_templates'
    _relation_fields = ['device_type']

class PowerPortsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.power_ports'
    _relation_fields = ['device', 'cable']

class RackGroupsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.rack_groups'
    _relation_fields = ['parent', 'site']

class RackReservationsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.rack_reservations'
    _relation_fields = ['rack', 'user', 'tenant']

class RackRolesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.rack_roles'

class RacksAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'dcim.racks'
    _relation_fields = ['group', 'site', 'tenant', 'role']

    _object_type = 'dcim.rack'

class RearPortTemplatesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.rear_port_templates'
    _relation_fields = ['device_type']

class RearPortsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.rear_ports'
    _relation_fields = ['device', 'cable']

class RegionsAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'dcim.regions'
    _relation_fields = ['parent']

    _object_type = 'dcim.region'

class SitesAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'dcim.sites'
    _relation_fields = ['region', 'tenant']

    _object_type = 'dcim.site'

class VirtualChassisAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.virtual_chassis'
    _relation_fields = ['master']

class DCIMGroup(SitePlannerAPIGroup):

    @property
    def cables(self):
        return CablesAPI(self._sp_client)

    @property
    def console_port_templates(self):
        return ConsolePortTemplatesAPI(self._sp_client)

    @property
    def console_ports(self):
        return ConsolePortsAPI(self._sp_client)

    @property
    def console_server_port_templates(self):
        return ConsoleServerPortTemplatesAPI(self._sp_client)

    @property
    def console_server_ports(self):
        return ConsoleServerPortsAPI(self._sp_client)

    @property
    def device_bay_templates(self):
        return DeviceBayTemplatesAPI(self._sp_client)

    @property
    def device_bays(self):
        return DeviceBaysAPI(self._sp_client)

    @property
    def device_roles(self):
        return DeviceRolesAPI(self._sp_client)

    @property
    def device_types(self):
        return DeviceTypesAPI(self._sp_client)

    @property
    def devices(self):
        return DevicesAPI(self._sp_client)

    @property
    def front_port_templates(self):
        return FrontPortTemplatesAPI(self._sp_client)

    @property
    def front_ports(self):
        return FrontPortsAPI(self._sp_client)

    @property
    def interface_templates(self):
        return InterfaceTemplatesAPI(self._sp_client)

    @property
    def interfaces(self):
        return InterfacesAPI(self._sp_client)

    @property
    def inventory_items(self):
        return InventoryItemsAPI(self._sp_client)

    @property
    def manufacturers(self):
        return ManufacturersAPI(self._sp_client)

    @property
    def platforms(self):
        return PlatformsAPI(self._sp_client)

    @property
    def power_feeds(self):
        return PowerFeedsAPI(self._sp_client)

    @property
    def power_outlet_templates(self):
        return PowerOutletTemplatesAPI(self._sp_client)

    @property
    def power_outlets(self):
        return PowerOutletsAPI(self._sp_client)

    @property
    def power_panels(self):
        return PowerPanelsAPI(self._sp_client)

    @property
    def power_port_templates(self):
        return PowerPortTemplatesAPI(self._sp_client)

    @property
    def power_ports(self):
        return PowerPortsAPI(self._sp_client)

    @property
    def rack_groups(self):
        return RackGroupsAPI(self._sp_client)

    @property
    def rack_reservations(self):
        return RackReservationsAPI(self._sp_client)

    @property
    def rack_roles(self):
        return RackRolesAPI(self._sp_client)

    @property
    def racks(self):
        return RacksAPI(self._sp_client)

    @property
    def rack_groups(self):
        return RackGroupsAPI(self._sp_client)

    @property
    def rear_port_templates(self):
        return RearPortTemplatesAPI(self._sp_client)

    @property
    def rear_ports(self):
        return RearPortsAPI(self._sp_client)

    @property
    def regions(self):
        return RegionsAPI(self._sp_client)

    @property
    def sites(self):
        return SitesAPI(self._sp_client)
    
    @property
    def virtual_chassis(self):
        return VirtualChassisAPI(self._sp_client)
