from .sp_api_base import SitePlannerAPIGroup, SitePlannerAPI

class AggregatesAPI(SitePlannerAPI):
    _endpoint_chain = 'ipam.aggregates'
    _relation_fields = ['rir']

class ExternalServicesAPI(SitePlannerAPI):
    _endpoint_chain = 'plugins.nfvi_management.external_services'

class IPAddressesAPI(SitePlannerAPI):
    _endpoint_chain = 'ipam.ip_addresses'
    _relation_fields = ['vrf', 'tenant', 'interface', 'nat_inside', 'nat_outside']

# TODO - prefixes/available-ips, prefixes/available-prefixes

class PrefixesAPI(SitePlannerAPI):
    _endpoint_chain = 'ipam.prefixes'
    _relation_fields = ['site', 'vrf', 'tenant', 'role']

class RirsAPI(SitePlannerAPI):
    _endpoint_chain = 'ipam.rirs'

class RolesAPI(SitePlannerAPI):
    _endpoint_chain = 'ipam.roles'

class ServicesAPI(SitePlannerAPI):
    _endpoint_chain = 'ipam.services'
    _relation_fields = ['device', 'virtual_machine']

class VlanGroupsAPI(SitePlannerAPI):
    _endpoint_chain = 'ipam.vlan_groups'
    _relation_fields = ['site']

class VlansAPI(SitePlannerAPI):
    _endpoint_chain = 'ipam.vlans'
    _relation_fields = ['site', 'group', 'tenant', 'role']

class VrfsAPI(SitePlannerAPI):
    _endpoint_chain = 'ipam.vrfs'
    _relation_fields = ['tenant']


class IPAMGroup(SitePlannerAPIGroup):

    @property
    def aggregates(self):
        return AggregatesAPI(self._sp_client)

    @property
    def external_services(self):
        return ExternalServicesAPI(self._sp_client)

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
