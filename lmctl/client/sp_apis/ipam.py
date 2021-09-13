import logging
from typing import Dict
from .sp_api_base import SitePlannerAPIGroup, SitePlannerCrudAPI
from .automation_context import AutomationContextAPIMixin
from lmctl.client.exceptions import SitePlannerClientError

logger = logging.getLogger(__name__)



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

class SubnetRolesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'ipam.subnetroles'

    def get_by_name(self, name: str) -> Dict:
        resp = self._make_direct_http_call(
            verb='get',
            override_url=self._pynb_endpoint.url + f'/?name={name}',
        ).json()
        count = resp.get('count', 0)
        if count == 0:
            return None
        if count > 1:
            raise SitePlannerClientError(f'Too many matches on name: {name}')
        results = resp.get('results', None)
        if results is None:
            return None
        obj = results[0]
        return self._record_to_dict(obj)


class SubnetsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'ipam.subnets'

    def get_by_name(self, name: str) -> Dict:
        resp = self._make_direct_http_call(
            verb='get',
            override_url=self._pynb_endpoint.url + f'/?name={name}',
        ).json()
        count = resp.get('count', 0)
        if count == 0:
            return None
        if count > 1:
            raise SitePlannerClientError(f'Too many matches on name: {name}')
        results = resp.get('results', None)
        if results is None:
            return None
        obj = results[0]
        return self._record_to_dict(obj)

    def get_by_cidr(self, cidr: str) -> Dict:
        resp = self._make_direct_http_call(
            verb='get',
            override_url=self._pynb_endpoint.url + f'/?cidr={cidr}',
        ).json()
        count = resp.get('count', 0)
        if count == 0:
            return None
        if count > 1:
            raise SitePlannerClientError(f'Too many matches on cidr: {cidr}')
        results = resp.get('results', None)
        if results is None:
            return None
        obj = results[0]
        return self._record_to_dict(obj)


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

    @property
    def subnets(self):
        return SubnetsAPI(self._sp_client)

    @property
    def subnet_roles(self):
        return SubnetRolesAPI(self._sp_client)