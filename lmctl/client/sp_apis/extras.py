from .sp_api_base import SitePlannerAPIGroup, SitePlannerAPI


class ConfigContextsAPI(SitePlannerAPI):
    _endpoint_chain = 'extras.config_contexts'
    _relation_fields = ['sites', 'roles', 'platforms', 'cluster_groups', 'clusters', 'tenant_groups', 'tenants']

class ExportTemplatesAPI(SitePlannerAPI):
    _endpoint_chain = 'extras.export_templates'

class TagsAPI(SitePlannerAPI):
    _endpoint_chain = 'extras.tags'

# TODO automation_context_processes

class AutomationContextsAPI(SitePlannerAPI):
    _endpoint_chain = 'plugins.nfvi_automation.automation_contexts'

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

    @property
    def automation_contexts(self):
        return AutomationContextsAPI(self._sp_client)
