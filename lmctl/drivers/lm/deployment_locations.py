import logging
import requests
from .base import LmDriver

logger = logging.getLogger(__name__)


class LmDeploymentLocationDriver(LmDriver):
    """
    Client for CP4NA orchestration Deployment Location APIs
    """

    def __init__(self, lm_base, lm_security_ctrl=None):
        super().__init__(lm_base, lm_security_ctrl)

    def __locations_api(self):
        return '{0}/api/deploymentLocations'.format(self.lm_base)

    def __location_by_name_api(self, location_name):
        return '{0}/api/deploymentLocations?name={1}'.format(self.lm_base, location_name)

    def __location_by_id_api(self, location_id):
        return '{0}/api/deploymentLocations/{1}'.format(self.lm_base, location_id)

    def get_locations(self):
        url = self.__locations_api()
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            locations = response.json()
            return locations
        else:
            self._raise_unexpected_status_exception(response)

    def get_locations_by_name(self, deployment_location_name):
        url = self.__location_by_name_api(deployment_location_name)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            locations = response.json()
            return locations
        else:
            self._raise_unexpected_status_exception(response)

    def add_location(self, deployment_location):
        url = self.__locations_api()
        headers = self._configure_access_headers()
        response = requests.post(url, headers=headers, json=deployment_location, verify=False)
        if response.status_code == 201:
            location_header = response.headers['location']
            location_parts = location_header.split('/')
            deployment_location_id = location_parts[len(location_parts)-1]
            deployment_location['id'] = deployment_location_id
            return deployment_location
        else:
            self._raise_unexpected_status_exception(response)

    def delete_location(self, deployment_location_id):
        url = self.__location_by_id_api(deployment_location_id)
        headers = self._configure_access_headers()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            raise NotFoundException('No deployment location with id {0}'.format(deployment_location_id))
        else:
            self._raise_unexpected_status_exception(response)
