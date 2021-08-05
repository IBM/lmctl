from .sp_api_base import SitePlannerAPIGroup, SitePlannerCrudAPI
from .automation_context import AutomationContextAPIMixin

class AggregatesAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'ipam.aggregates'
    _relation_fields = ['rir']

    _object_type = 'ipam.aggregate'


class IPAddressesAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'ipam.ip_addresses'
    _relation_fields = ['vrf', 'tenant', 'interface', 'nat_inside', 'nat_outside']

    _object_type = 'ipam.ipaddress'

# TODO - prefixes/available-ips, prefixes/available-prefixes

class PrefixesAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'ipam.prefixes'
    _relation_fields = ['site', 'vrf', 'tenant', 'role']

    _object_type = 'ipam.prefix'

class RirsAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'ipam.rirs'

    _object_type = 'ipam.rir'

class RolesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'ipam.roles'

class ServicesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'ipam.services'
    _relation_fields = ['device', 'virtual_machine']

class VlanGroupsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'ipam.vlan_groups'
    _relation_fields = ['site']

class VlansAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'ipam.vlans'
    _relation_fields = ['site', 'group', 'tenant', 'role']

    _object_type = 'ipam.vlan'

class VrfsAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'ipam.vrfs'
    _relation_fields = ['tenant']

    _object_type = 'ipam.vrf'


class IPAMGroup(SitePlannerAPIGroup):

    @property
    def aggregates(self):
        return AggregatesAPI(self._sp_client)

    @property
    def ip_addresses(self):
        return IPAddressesAPI(self._sp_client)

    @property
    def prefixes(self):
        return PrefixesAPI(self._sp_client)

    @property
    def rirs(self):
        return RirsAPI(self._sp_client)

    @property
    def roles(self):
        return RolesAPI(self._sp_client)

    @property
    def services(self):
        return ServicesAPI(self._sp_client)

    @property
    def vlan_groups(self):
        return VlanGroupsAPI(self._sp_client)

    @property
    def vlans(self):
        return VlansAPI(self._sp_client)

    @property
    def vrfs(self):
        return VrfsAPI(self._sp_client)
