from typing import Dict, List
from .tnco_api_base import TNCOAPI
class SharedInfrastructureKeysAPI(TNCOAPI):
    endpoint = 'api/resource-manager/infrastructure-keys/shared'
    id_attr = 'name'

    def all(self, include_private_key: bool = None, object_group_id: str = None) -> List:
        query_params = None
        if include_private_key is not None:
            query_params={'includePrivateKey': include_private_key}
        return self._all(query_params=query_params, object_group_id=object_group_id)

    def get(self, id: str, include_private_key: bool = None) -> Dict:
        query_params = None
        if include_private_key is not None:
            query_params={'includePrivateKey': include_private_key}
        return self._get(id_value=id, query_params=query_params)

    def create(self, inf_key: Dict, object_group_id: str = None):
        return self._create(obj=inf_key, object_group_id=object_group_id)

    def update(self, inf_key: Dict):
        self._update(obj=inf_key)

    def delete(self, id: str):
        self._delete(id_value=id)

