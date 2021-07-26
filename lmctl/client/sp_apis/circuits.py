from .sp_api_base import SitePlannerAPIGroup, SitePlannerAPI

class CircuitTerminationsAPI(SitePlannerAPI):
    _endpoint_chain = 'circuits.circuit_terminations'
    _relation_fields = ['circuit', 'site', 'cable']

class CircuitTypesAPI(SitePlannerAPI):
    _endpoint_chain = 'circuits.circuit_types'

class CircuitsAPI(SitePlannerAPI):
    _endpoint_chain = 'circuits.circuits'
    _relation_fields = ['provider', 'type']

class ProvidersAPI(SitePlannerAPI):
    _endpoint_chain = 'circuits.providers'

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
