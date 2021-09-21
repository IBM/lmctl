import logging
from .sp_api_base import SitePlannerAPIGroup, SitePlannerCrudAPI
from .automation_context import AutomationContextAPIMixin
from lmctl.client.utils import read_response_location_header
from lmctl.client.exceptions import SitePlannerClientError
from typing import Dict


logger = logging.getLogger(__name__)

class ClusterGroupsAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'virtualization.cluster_groups'

    _object_type = 'virtualization.cluster_group'

class ClusterTypesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'virtualization.cluster_types'

    def get_by_name(self, name: str) -> Dict:
        override_url = self._pynb_endpoint.url + f'/?name={name}'
        resp = self._make_direct_http_call(
            verb='get',
            override_url=override_url,
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

class ClustersAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'virtualization.clusters'
    _relation_fields = ['type', 'group', 'tenant', 'site']

    _object_type = 'virtualization.cluster'

    def get_by_name(self, name: str) -> Dict:
        override_url = self._pynb_endpoint.url + f'/?name={name}'
        resp = self._make_direct_http_call(
            verb='get',
            override_url=override_url,
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

class InterfacesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'virtualization.interfaces'
    _relation_fields = ['virtual_machine', 'untagged_vlan', 'tagged_vlans']

class VirtualMachinesAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'virtualization.virtual_machines'
    _relation_fields = ['site', 'cluster', 'role', 'tenant', 'platform', 'primary_ip', 'primary_ip4', 'primary_ip6']

    _object_type = 'virtualization.virtualmachine'

    def get_by_name(self, name: str) -> Dict:
        override_url = self._pynb_endpoint.url + f'/?name={name}'
        resp = self._make_direct_http_call(
            verb='get',
            override_url=override_url,
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


class CloudAccountTypesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'virtualization.cloudaccounttypes'

    def get_by_name(self, name: str) -> Dict:
        override_url = self._pynb_endpoint.url + f'/?name={name}'
        resp = self._make_direct_http_call(
            verb='get',
            override_url=override_url,
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


class CloudAccountsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'virtualization.cloudaccounts'

    def get_by_name(self, name: str) -> Dict:
        override_url = self._pynb_endpoint.url + f'/?name={name}'
        logger.info(f'CloudAccounts name={name} override_url={override_url}')
        resp = self._make_direct_http_call(
            verb='get',
            override_url=override_url,
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

    def build(self, id: str) -> str:
        response = self._make_direct_http_call(
            verb='post',
            override_url=self._pynb_endpoint.url + f'/{id}/build/',
            data={}
        )
        return read_response_location_header(response, error_class=SitePlannerClientError)

    def teardown(self, id: str) -> str:
        response = self._make_direct_http_call(
            verb='post',
            override_url=self._pynb_endpoint.url + f'/{id}/teardown/',
            data={}
        )
        return read_response_location_header(response, error_class=SitePlannerClientError)


class VPCsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'virtualization.vpcs'

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

    def get_by_cloud_provider_id(self, id: str) -> Dict:
        resp = self._make_direct_http_call(
            verb='get',
            override_url=self._pynb_endpoint.url + f'/?cloud_provider_id={id}',
        ).json()
        count = resp.get('count', 0)
        if count == 0:
            return None
        if count > 1:
            raise SitePlannerClientError(f'Too many matches on cloud_provider_id: {id}')
        results = resp.get('results', None)
        if results is None:
            return None
        obj = results[0]
        return self._record_to_dict(obj)

    def build(self, id: str) -> str:
        response = self._make_direct_http_call(
            verb='post',
            override_url=self._pynb_endpoint.url + f'/{id}/build/',
            data={}
        )
        return read_response_location_header(response, error_class=SitePlannerClientError)

    def teardown(self, id: str) -> str:
        response = self._make_direct_http_call(
            verb='post',
            override_url=self._pynb_endpoint.url + f'/{id}/teardown/',
            data={}
        )
        return read_response_location_header(response, error_class=SitePlannerClientError)


class VirtualizationGroup(SitePlannerAPIGroup):

    @property
    def cluster_groups(self):
        return ClusterGroupsAPI(self._sp_client)

    @property
    def cluster_types(self):
        return ClusterTypesAPI(self._sp_client)

    @property
    def clusters(self):
        return ClustersAPI(self._sp_client)

    @property
    def interfaces(self):
        return InterfacesAPI(self._sp_client)

    @property
    def virtual_machines(self):
        return VirtualMachinesAPI(self._sp_client)

    @property
    def cloud_account_types(self):
        return CloudAccountTypesAPI(self._sp_client)    

    @property
    def cloud_accounts(self):
        return CloudAccountsAPI(self._sp_client)    

    @property
    def vpcs(self):
        return VPCsAPI(self._sp_client)