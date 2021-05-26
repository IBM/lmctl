from typing import List, Dict
from .tnco_api_base import TNCOAPI
from lmctl.client.client_request import TNCOClientRequest

class ProcessesAPI(TNCOAPI):
    endpoint = 'api/processes'

    def get(self, id: str, shallow: bool = None) -> Dict:
        query_params = {}
        if shallow is not None:
            query_params['shallow'] = shallow
        return self._get(id_value=id, query_params=query_params)

    def query(self, **query_params) -> List:
        return self._get_json(self.endpoint, query_params=query_params)
