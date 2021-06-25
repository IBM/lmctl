from typing import List
from typing import List, Dict
from .tnco_api_base import TNCOAPI

class BehaviourScenariosAPI(TNCOAPI):
    endpoint = 'api/behaviour/scenarios'

    def get(self, id: str) -> Dict:
        return self._get(id_value=id)

    def create(self, scenario: Dict):
        return self._create(obj=scenario)

    def update(self, scenario: Dict):
        self._update(obj=scenario)

    def delete(self, id: str):
        self._delete(id_value=id)

    def all_in_project(self, project_id: str) -> List:
        return self._get_json(self.endpoint, query_params={'projectId': project_id})
