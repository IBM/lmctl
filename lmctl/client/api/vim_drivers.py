from typing import Dict
from .tnco_api_base import TNCOAPI
class VIMDriversAPI(TNCOAPI):
    endpoint = 'api/resource-manager/vim-drivers'

    def get(self, driver_id: str) -> Dict:
        return self._get(id_value=driver_id)

    def create(self, driver: Dict):
        return self._create(obj=driver)

    def update(self, driver: Dict):
        self._update(obj=driver)

    def delete(self, driver_id: str):
        self._delete(id_value=driver_id)

    def get_by_type(self, driver_type: str) -> Dict:
        return self._get_json(self.endpoint, query_params={'type': driver_type})
