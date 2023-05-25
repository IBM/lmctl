from typing import List, Dict
from .tnco_api_base import TNCOAPI

class BehaviourProjectsAPI(TNCOAPI):
    endpoint = 'api/behaviour/projects'

    def all(self, object_group_id: str = None) -> List:
        return self._all(object_group_id=object_group_id)

    def get(self, id: str) -> Dict:
        return self._get(id_value=id)

    def create(self, project: Dict, object_group_id: str = None):
        return self._create(obj=project, object_group_id=object_group_id)

    def update(self, project: Dict):
        self._update(obj=project)

    def delete(self, id: str):
        self._delete(id_value=id)
