from typing import Dict
from .tnco_api_base import TNCOAPI
from lmctl.client.exceptions import TNCOClientHttpError

class BrentDeploymentLocationAPI(TNCOAPI):
    endpoint = 'api/resource-manager/topology/deployment-locations'

    def get(self, id: str) -> Dict:
        try:
            return self._get(id_value=id)
        except TNCOClientHttpError as e:
            if e.status_code == 404:
                return None
            elif e.status_code == 403:
                return None
            raise e

