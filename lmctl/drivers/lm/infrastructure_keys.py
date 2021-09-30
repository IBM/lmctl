import logging
import requests
from .base import LmDriver, NotFoundException

logger = logging.getLogger(__name__)


class LmInfrastructureKeysDriver(LmDriver):
    """
    Client for CP4NA orchestration Infrastructure Key APIs
    """

    def __init__(self, lm_base, lm_security_ctrl=None):
        super().__init__(lm_base, lm_security_ctrl)

    def __infrastructure_keys_api(self):
        return '{0}/api/resource-manager/infrastructure-keys/shared'.format(self.lm_base)

    def __infrastructure_key_by_name_api(self, keyname):
        return '{0}/api/resource-manager/infrastructure-keys/shared/{1}'.format(self.lm_base, keyname)

    def get_infrastructure_keys(self):
        url = self.__infrastructure_keys_api()
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            infrastructure_keys = response.json()
            return infrastructure_keys
        else:
            self._raise_unexpected_status_exception(response)

    def get_infrastructure_key_by_name(self, keyname):
        url = self.__infrastructure_key_by_name_api(keyname)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            infrastructure_key = response.json()
            return infrastructure_key
        elif response.status_code == 404:
            return None         
        else:
            self._raise_unexpected_status_exception(response)

    def add_infrastructure_key(self, infrastructure_key):
        url = self.__infrastructure_keys_api()
        headers = self._configure_access_headers()
        response = requests.post(url, headers=headers, json=infrastructure_key, verify=False)
        if response.status_code == 201:
            location_header = response.headers['location']
            location_parts = location_header.split('/')
            ik_id = location_parts[len(location_parts)-1]
            infrastructure_key['id'] = ik_id
            return infrastructure_key
        else:
            self._raise_unexpected_status_exception(response)

    def delete_infrastructure_key(self, infrastructure_key_name):
        url = self.__infrastructure_key_by_name_api(infrastructure_key_name)
        headers = self._configure_access_headers()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            raise NotFoundException('No infrastructure key with name {0}'.format(infrastructure_key_name))
        else:
            self._raise_unexpected_status_exception(response)
