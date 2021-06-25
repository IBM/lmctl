from typing import Union
from pathlib import Path
from lmctl.client.client_request import TNCOClientRequest
from .tnco_api_base import TNCOAPI
from lmctl.client.utils import build_relative_endpoint

class ResourcePackagesAPI(TNCOAPI):
    endpoint = 'api/resource-manager/resource-packages'

    def create(self, resource_pkg_path: Union[str,Path]) -> str:
        with open(resource_pkg_path, 'rb') as resource_pkg:
            files = {'file': resource_pkg}
            request = TNCOClientRequest(method='POST', endpoint=self.endpoint).add_files(files)
            return self._exec_request_and_get_location_header(request)

    def update(self, resource_name: str, resource_pkg_path: Union[str,Path]):
        with open(resource_pkg_path, 'rb') as resource_pkg:
            files = {'file': resource_pkg}
            request = TNCOClientRequest(method='PUT', 
                                        endpoint=build_relative_endpoint(base_endpoint=self.endpoint, id_value=resource_name)
                                    ).add_files(files)
            self._exec_request(request)

    def delete(self, resource_name: str):
        self._delete(id_value=resource_name)
