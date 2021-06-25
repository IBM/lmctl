from typing import List, Dict
from .tnco_api_base import TNCOAPI

class DeploymentLocationAPI(TNCOAPI):
    endpoint = 'api/deploymentLocations'

    def all(self) -> List:
        return self._all()

    def get(self, id: str) -> Dict:
        return self._get(id_value=id)

    def create(self, project: Dict):
        return self._create(obj=project)

    def update(self, project: Dict):
        self._update(obj=project)

    def delete(self, id: str):
        self._delete(id_value=id)

    def all_with_name(self, name: str) -> List:
        return self._get_json(self.endpoint, query_params={'name': name})