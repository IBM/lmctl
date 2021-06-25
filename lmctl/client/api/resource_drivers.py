from typing import Dict
from .tnco_api_base import TNCOAPI

class ResourceDriversAPI(TNCOAPI):
    endpoint = 'api/resource-manager/resource-drivers'

    def get(self, id: str) -> Dict:
        return self._get(id_value=id)

    def create(self, driver: Dict):
        return self._create(obj=driver)

    def delete(self, id: str):
        self._delete(id_value=id)

    def get_by_type(self, driver_type: str) -> Dict:
        return self._get_json(self.endpoint, query_params={'type': driver_type})
