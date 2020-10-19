from typing import Union
from pathlib import Path
from .api_base import APIBase
from .resource_api_base import location_id_response_handler

class ResourcePackagesAPI(APIBase):
    endpoint = 'api/resource-manager/resource-packages'

    enable_list_api = False
    enable_read_api = False

    def create(self, resource_pkg_path: Union[str,Path]) -> str:
        with open(resource_pkg_path, 'rb') as resource_pkg:
            files = {'file': resource_pkg}
            response = self.base_client.make_request(method='POST', endpoint=self.endpoint, files=files)
            return location_id_response_handler(response)
    
    def update(self, resource_name: str, resource_pkg_path: Union[str,Path]):
        with open(resource_pkg_path, 'rb') as resource_pkg:
            files = {'file': resource_pkg}
            endpoint = f'{self.endpoint}/{resource_name}'
            self.base_client.make_request(method='PUT', endpoint=endpoint, files=files)

    def delete(self, resource_name: str):
        endpoint = f'{self.endpoint}/{resource_name}'
        self.base_client.make_request(method='DELETE', endpoint=endpoint)