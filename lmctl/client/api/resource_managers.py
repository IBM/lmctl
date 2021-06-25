from typing import Dict, List
from .tnco_api_base import TNCOAPI
from lmctl.client.utils import read_response_body_as_json

class ResourceManagersAPI(TNCOAPI):
    endpoint = 'api/resource-managers'
    id_attr = 'name'

    def all(self) -> List:
        return self._all()

    def get(self, id: str) -> Dict:
        return self._get(id_value=id)

    def create(self, resource_manager: Dict):
        return self._create(obj=resource_manager, response_handler=read_response_body_as_json)

    def update(self, resource_manager: Dict):
        return self._update(obj=resource_manager, response_handler=read_response_body_as_json)

    def delete(self, id: str):
        self._delete(id_value=id)
