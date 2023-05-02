from typing import List, Dict
from .tnco_api_base import TNCOAPI
from lmctl.client.client_request import TNCOClientRequest

class ObjectGroupsAPI(TNCOAPI):
    endpoint = 'api/v1/object-groups'

    def get(self, id: str) -> Dict:
        return self._get(id_value=id)

    def query(self, **query_params) -> List:
        return self._get_json(self.endpoint, query_params=query_params)

    def all(self) -> List:
        return self._all()
