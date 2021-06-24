from .sp_api_base import SitePlannerAPIGroup, SitePlannerAPI

class TenantGroupsAPI(SitePlannerAPI):
    _endpoint_chain = 'tenancy.tenant_groups'

class TenantsAPI(SitePlannerAPI):
    _endpoint_chain = 'tenancy.tenants'

class TenancyGroup(SitePlannerAPIGroup):

    @property
    def tenant_groups(self):
        return TenantGroupsAPI(self._sp_client)

    @property
    def tenants(self):
        return TenantsAPI(self._sp_client)
