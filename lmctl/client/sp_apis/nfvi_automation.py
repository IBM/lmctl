from .sp_api_base import SitePlannerAPIGroup
from .automation_context import AutomationContextProcessesAPI, AutomationContextsAPI

class NFVIAutomationGroup(SitePlannerAPIGroup):

    @property
    def automation_contexts(self):
        return AutomationContextsAPI(self._sp_client)

    @property
    def automation_context_processes(self):
        return AutomationContextProcessesAPI(self._sp_client)
