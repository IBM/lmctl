from .sp_api_base import SitePlannerAPIGroup, SitePlannerCrudAPI
from .automation_context import AutomationContextAPIMixin

class CircuitTerminationsAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'circuits.circuit_terminations'
    _relation_fields = ['circuit', 'site', 'cable']

class CircuitTypesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'circuits.circuit_types'

class CircuitsAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'circuits.circuits'
    _relation_fields = ['provider', 'type']

    _object_type = 'circuits.circuit'

class ProvidersAPI(SitePlannerCrudAPI, AutomationContextAPIMixin):
    _endpoint_chain = 'circuits.providers'

    _object_type = 'circuits.provider'

class CircuitsGroup(SitePlannerAPIGroup):

    @property
    def circuit_terminations(self):
        return CircuitTerminationsAPI(self._sp_client)

    @property
    def circuit_types(self):
        return CircuitTypesAPI(self._sp_client)

    @property
    def circuits(self):
        return CircuitsAPI(self._sp_client)

    @property
    def providers(self):
        return ProvidersAPI(self._sp_client)
