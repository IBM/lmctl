from .sp_api_base import SitePlannerAPIGroup, SitePlannerCrudAPI
from .automation_context import AutomationContextAPIMixin

class TenantGroupsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'tenancy.tenant_groups'
    _relation_fields = ['parent']

class TenantsAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'tenancy.tenants'
    _relation_fields = ['group']

    _object_type = 'tenancy.tenant'

class TenancyGroup(SitePlannerAPIGroup):

    @property
    def tenant_groups(self):
        return TenantGroupsAPI(self._sp_client)

    @property
    def tenants(self):
        return TenantsAPI(self._sp_client)
