from typing import List, Dict
from .tnco_api_base import TNCOAPI
from lmctl.client.exceptions import TNCOClientError

class ObjectGroupsAPI(TNCOAPI):
    endpoint = 'api/v1/object-groups'

    def get(self, id: str) -> Dict:
        return self._get(id_value=id)
    
    def get_by_name(self, name: str) -> Dict:
        object_groups = self.all()
        for og in object_groups:
            if og.get('name', None) == name:
                return og
        raise TNCOClientError(f'No Object Group found with name matching "{name}"')

    def query(self, **query_params) -> List:
        return self._get_json(self.endpoint, query_params=query_params)

    def all(self) -> List:
        return self._all()
    
    def get_default(self) -> Dict:
        return self._get_json(self.endpoint + '/default')
