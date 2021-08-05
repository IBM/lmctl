from .sp_api_base import SitePlannerAPIGroup, SitePlannerCrudAPI

class ConfigContextsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'extras.config_contexts'
    _relation_fields = ['sites', 'roles', 'platforms', 'cluster_groups', 'clusters', 'tenant_groups', 'tenants']

class ExportTemplatesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'extras.export_templates'

class TagsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'extras.tags'

class ExtrasGroup(SitePlannerAPIGroup):

    @property
    def config_contexts(self):
        return ConfigContextsAPI(self._sp_client)

    @property
    def export_templates(self):
        return ExportTemplatesAPI(self._sp_client)

    @property
    def tags(self):
        return TagsAPI(self._sp_client)

