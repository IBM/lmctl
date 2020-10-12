from typing import List, Dict
from .resource_api_base import ResourceAPIBase, json_response_handler

class DeploymentLocationAPI(ResourceAPIBase):
    endpoint = 'api/deploymentLocations'

    def _by_name_endpoint(self, location_name: str) -> str:
        return f'{self.endpoint}?name={location_name}'

    def all_with_name(self, deployment_location_name: str) -> List:
        endpoint = self._by_name_endpoint(deployment_location_name)
        response = self.base_client.make_request(method='GET', endpoint=endpoint)
        return json_response_handler(response)

    