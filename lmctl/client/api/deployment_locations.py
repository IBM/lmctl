from typing import List, Dict
from .tnco_api_base import TNCOAPI

class DeploymentLocationAPI(TNCOAPI):
    endpoint = 'api/deploymentLocations'

    def all(self, object_group_id: str = None) -> List:
        return self._all(object_group_id=object_group_id)

    def get(self, id: str) -> Dict:
        return self._get(id_value=id)

    def create(self, location: Dict, object_group_id: str = None):
        return self._create(obj=location, object_group_id=object_group_id)

    def update(self, location: Dict):
        self._update(obj=location)

    def delete(self, id: str):
        self._delete(id_value=id)

    def all_with_name(self, name: str, object_group_id: str = None) -> List:
        return self._get_json(self.endpoint, query_params={'name': name}, object_group_id=object_group_id)