

class DeploymentLocationApi:

    def __init__(self, base_client: 'LmClient'):
        self.base_client = base_client
        self.endpoint = f'{self.base_client.address}/api/deploymentLocations'

    def _by_name_endpoint(self, location_name: str) -> str:
        return f'{self.endpoint}?name={location_name}'

    def _by_id_endpoint(self, location_id: str) -> str:
        return f'{self.endpoint}/{location_id}'

    def all(self):
        url = self._endpoint()
        headers = self._configure_access_headers()
        response = self.base_client.make_request('GET', self.endpoint)
        return response.json()

    def get_locations_by_name(self, deployment_location_name):
        url = self.__location_by_name_api(deployment_location_name)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            locations = response.json()
            return locations
        else:
            self._raise_unexpected_status_exception(response)
