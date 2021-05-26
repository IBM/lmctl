from typing import List, Dict
from .tnco_api_base import TNCOAPI

class BehaviourAssemblyConfigurationsAPI(TNCOAPI):
    endpoint = 'api/behaviour/assemblyConfigurations'

    def get(self, id: str) -> Dict:
        return self._get(id_value=id)

    def create(self, assembly_configuration: Dict):
        return self._create(obj=assembly_configuration)

    def update(self, assembly_configuration: Dict):
        self._update(obj=assembly_configuration)

    def delete(self, id: str):
        self._delete(id_value=id)

    def all_in_project(self, project_id: str) -> List:
        return self._get_json(self.endpoint, query_params={'projectId': project_id})
