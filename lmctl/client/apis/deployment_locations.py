from typing import List

class DeploymentLocationAPI:

    def __init__(self, base_client: 'LmClient'):
        self.base_client = base_client
        self.endpoint = f'{self.base_client.address}/api/deploymentLocations'

    def _by_name_endpoint(self, location_name: str) -> str:
        return f'{self.endpoint}?name={location_name}'

    def _by_id_endpoint(self, location_id: str) -> str:
        return f'{self.endpoint}/{location_id}'

    def all(self) -> List:
        url = self._endpoint()
        location_list = self.base_client.make_request_for_json('GET', self.endpoint)
        return location_list

    def all_by_name(self, deployment_location_name: str) -> List:
        url = self.__location_by_name_api(deployment_location_name)
        location_list = self.base_client.make_request_for_json('GET', self.endpoint)
        return location_list