from .sp_api_base import SitePlannerAPIGroup, SitePlannerAPI

class VirtualInfrastructureTypesAPI(SitePlannerAPI):
    _endpoint_chain = 'plugin.nfvi_management.virtual_infrastructure_types'

class VirtualInfrastructuresAPI(SitePlannerAPI):
    _endpoint_chain = 'plugin.nfvi_management.virtual_infrastructures'

# TODO build and teardown APIs
# TODO managed-entity-automation-process
class ManagedEntitiesAPI(SitePlannerAPI):
    _endpoint_chain = 'plugin.nfvo_automation.managed_entities'

class ManagedEntityComponentsAPI(SitePlannerAPI):
    _endpoint_chain = 'plugin.nfvo_automation.managed_entity_components'

class ManagedEntityTypesAPI(SitePlannerAPI):
    _endpoint_chain = 'plugin.nfvo_automation.managed_entity_types'

class ClusterGroupsAPI(SitePlannerAPI):
    _endpoint_chain = 'virtualization.cluster_groups'

class ClusterTypesAPI(SitePlannerAPI):
    _endpoint_chain = 'virtualization.cluster_types'

class ClustersAPI(SitePlannerAPI):
    _endpoint_chain = 'virtualization.clusters'

class InterfacesAPI(SitePlannerAPI):
    _endpoint_chain = 'virtualization.interfaces'

class VirtualMachinesAPI(SitePlannerAPI):
    _endpoint_chain = 'virtualization.virtual_machines'

class VirtualizationGroup(SitePlannerAPIGroup):

    @property
    def virtual_infrastructure_types(self):
        return VirtualInfrastructureTypesAPI(self._sp_client)

    @property
    def virtual_infrastructures(self):
        return VirtualInfrastructuresAPI(self._sp_client)

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
