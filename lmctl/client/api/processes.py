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

    def query(self, object_group_id: str = None, **query_params) -> List:
        return self._get_json(self.endpoint, query_params=query_params, object_group_id=object_group_id)
