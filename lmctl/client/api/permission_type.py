from typing import List, Dict
from .tnco_api_base import TNCOAPI

class PermissionTypesAPI(TNCOAPI):
    endpoint = 'api/v1/object-groups/permission-types'

    def get(self) -> Dict:
        return self._get()

    def query(self, **query_params) -> List:
        return self._get_json(self.endpoint, query_params=query_params)
