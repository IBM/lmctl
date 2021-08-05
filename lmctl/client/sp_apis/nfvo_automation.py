from .sp_api_base import SitePlannerAPIGroup, SitePlannerCrudAPI, SitePlannerAPI, SitePlannerGetMixin, SitePlannerDeleteMixin, SitePlannerListMixin
from lmctl.client.utils import read_response_location_header
from lmctl.client.exceptions import SitePlannerClientError

class ManagedEntitiesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'plugins.nfvo-automation.managed_entities'
    _relation_fields = ['type', 'components']

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

class ManagedEntityComponentsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'plugins.nfvo-automation.managed_entity_components'
    # "managed_entity" is currently returned as an int, rather than a nested object, so we don't need to specify this relation
    #_relation_fields = ['managed_entity']

class ManagedEntityTypesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'plugins.nfvo-automation.managed_entity_types'
    _ignore_fields_on_update = ['display_name']

class ManagedEntityAutomationProcesses(SitePlannerAPI, SitePlannerGetMixin, SitePlannerDeleteMixin, SitePlannerListMixin):
    _endpoint_chain = 'plugins.nfvo-automation.managed_entity_automation-processes'
    _relation_fields = ['managed_entity']

class NFVOAutomationGroup(SitePlannerAPIGroup):

    @property
    def managed_entities(self):
        return ManagedEntitiesAPI(self._sp_client)

    @property
    def managed_entity_components(self):
        return ManagedEntityComponentsAPI(self._sp_client)

    @property
    def managed_entity_types(self):
        return ManagedEntityTypesAPI(self._sp_client)

    @property
    def managed_entity_automation_processes(self):
        return ManagedEntityAutomationProcesses(self._sp_client)
