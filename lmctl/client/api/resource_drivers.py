from typing import Dict
from .resource_api_base import ResourceAPIBase, json_response_handler

class ResourceDriversAPI(ResourceAPIBase):
    endpoint = 'api/resource-manager/resource-drivers'

    enable_list_api = False
    enable_update_api = False

    def _by_type_endpoint(self, driver_type: str) -> str:
        return f'{self.endpoint}?type={driver_type}'

    def get_by_type(self, driver_type: str) -> Dict:
        endpoint = self._by_type_endpoint(driver_type)
        response = self.base_client.make_request(method='GET', endpoint=endpoint)
        return json_response_handler(response)
