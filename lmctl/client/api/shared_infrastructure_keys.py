from typing import Dict, List
from .tnco_api_base import TNCOAPI
class SharedInfrastructureKeysAPI(TNCOAPI):
    endpoint = 'api/resource-manager/infrastructure-keys/shared'
    id_attr = 'name'

    def all(self, include_private_key: bool = None) -> List:
        query_params = None
        if include_private_key is not None:
            query_params={'includePrivateKey': include_private_key}
        return self._all(query_params=query_params)

    def get(self, id: str, include_private_key: bool = None) -> Dict:
        query_params = None
        if include_private_key is not None:
            query_params={'includePrivateKey': include_private_key}
        return self._get(id_value=id, query_params=query_params)

    def create(self, resource_manager: Dict):
        return self._create(obj=resource_manager)

    def update(self, resource_manager: Dict):
        self._update(obj=resource_manager)

    def delete(self, id: str):
        self._delete(id_value=id)

