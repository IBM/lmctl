from .sp_api_base import SitePlannerAPIGroup, SitePlannerAPI

class VirtualInfrastructureTypesAPI(SitePlannerAPI):
    _endpoint_chain = 'plugins.nfvi_management.virtual_infrastructure_types'

class VirtualInfrastructuresAPI(SitePlannerAPI):
    _endpoint_chain = 'plugins.nfvi_management.virtual_infrastructures'
    _relation_fields = ['cluster', 'cluster_group']

# TODO build and teardown APIs
# TODO managed-entity-automation-process
class ManagedEntitiesAPI(SitePlannerAPI):
    _endpoint_chain = 'plugins.nfvo_automation.managed_entities'
    _relation_fields = ['type', 'components']

class ManagedEntityComponentsAPI(SitePlannerAPI):
    _endpoint_chain = 'plugins.nfvo_automation.managed_entity_components'
    _relation_fields = ['managed_entity']

class ManagedEntityTypesAPI(SitePlannerAPI):
    _endpoint_chain = 'plugins.nfvo_automation.managed_entity_types'

class ClusterGroupsAPI(SitePlannerAPI):
    _endpoint_chain = 'virtualization.cluster_groups'

class ClusterTypesAPI(SitePlannerAPI):
    _endpoint_chain = 'virtualization.cluster_types'

class ClustersAPI(SitePlannerAPI):
    _endpoint_chain = 'virtualization.clusters'
    _relation_fields = ['type', 'group', 'tenant', 'site']

class InterfacesAPI(SitePlannerAPI):
    _endpoint_chain = 'virtualization.interfaces'
    _relation_fields = ['virtual_machine', 'untagged_vlan', 'tagged_vlans']

class VirtualMachinesAPI(SitePlannerAPI):
    _endpoint_chain = 'virtualization.virtual_machines'
    _relation_fields = ['site', 'cluster', 'role', 'tenant', 'platform', 'primary_ip', 'primary_ip4', 'primary_ip6']

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
