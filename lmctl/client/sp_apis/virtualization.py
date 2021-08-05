from .sp_api_base import SitePlannerAPIGroup, SitePlannerCrudAPI
from .automation_context import AutomationContextAPIMixin


class ClusterGroupsAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'virtualization.cluster_groups'

    _object_type = 'virtualization.cluster_group'

class ClusterTypesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'virtualization.cluster_types'

class ClustersAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'virtualization.clusters'
    _relation_fields = ['type', 'group', 'tenant', 'site']

    _object_type = 'virtualization.cluster'

class InterfacesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'virtualization.interfaces'
    _relation_fields = ['virtual_machine', 'untagged_vlan', 'tagged_vlans']

class VirtualMachinesAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'virtualization.virtual_machines'
    _relation_fields = ['site', 'cluster', 'role', 'tenant', 'platform', 'primary_ip', 'primary_ip4', 'primary_ip6']

    _object_type = 'virtualization.virtualmachine'

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
