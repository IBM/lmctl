import logging
import requests
from .base import LmDriver, NotFoundException

logger = logging.getLogger(__name__)

class LmLifecycleDriverMgmtDriver(LmDriver):
    """
    Client for managing lifecycle drivers
    """

    def __init__(self, lm_base, lm_security_ctrl=None):
        super().__init__(lm_base, lm_security_ctrl)

    def __lifecycle_drivers_api(self):
        return '{0}/api/resource-manager/lifecycle-drivers'.format(self.lm_base)

    def __lifecycle_drivers_by_type_api(self, lifecycle_type):
        return '{0}/api/resource-manager/lifecycle-drivers?type={1}'.format(self.lm_base, lifecycle_type)

    def __lifecycle_driver_by_id_api(self, driver_id):
        return '{0}/api/resource-manager/lifecycle-drivers/{1}'.format(self.lm_base, driver_id)

    def add_lifecycle_driver(self, lifecycle_driver):
        url = self.__lifecycle_drivers_api()
        headers = self._configure_access_headers()
        response = requests.post(url, headers=headers, json=lifecycle_driver, verify=False)
        if response.status_code == 201:
            location_header = response.headers['location']
            location_parts = location_header.split('/')
            driver_id = location_parts[len(location_parts)-1]
            lifecycle_driver['id'] = driver_id
            return lifecycle_driver
        else:
            self._raise_unexpected_status_exception(response)

    def delete_lifecycle_driver(self, driver_id):
        url = self.__lifecycle_driver_by_id_api(driver_id)
        headers = self._configure_access_headers()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            raise NotFoundException('No lifecycle driver with id {0}'.format(driver_id))
        else:
            self._raise_unexpected_status_exception(response)

    def get_lifecycle_driver(self, driver_id):
        url = self.__lifecycle_driver_by_id_api(driver_id)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise NotFoundException('No lifecycle driver with id {0}'.format(driver_id))
        else:
            self._raise_unexpected_status_exception(response)

    def get_lifecycle_driver_by_type(self, lifecycle_type):
        url = self.__lifecycle_drivers_by_type_api(lifecycle_type)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise NotFoundException('No lifecycle driver with type {0}'.format(lifecycle_type))
        else:
            self._raise_unexpected_status_exception(response)