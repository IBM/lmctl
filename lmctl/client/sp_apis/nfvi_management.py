from .sp_api_base import SitePlannerAPIGroup, SitePlannerCrudAPI
from .automation_context import AutomationContextAPIMixin

class ExternalServicesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'plugins.nfvi-management.external_services'

class VirtualInfrastructureTypesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'plugins.nfvi-management.virtual_infrastructure_types'

class VirtualInfrastructuresAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'plugins.nfvi-management.virtual_infrastructures'
    _relation_fields = ['cluster', 'cluster_group']

    _object_type = 'nfvi_management.virtualinfrastructure'


class NFVIManagementGroup(SitePlannerAPIGroup):
    
    @property
    def external_services(self):
        return ExternalServicesAPI(self._sp_client)

    @property
    def virtual_infrastructure_types(self):
        return VirtualInfrastructureTypesAPI(self._sp_client)

    @property
    def virtual_infrastructures(self):
        return VirtualInfrastructuresAPI(self._sp_client)
