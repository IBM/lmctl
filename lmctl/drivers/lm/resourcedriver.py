import logging
import requests
from .base import LmDriver, NotFoundException

logger = logging.getLogger(__name__)

class LmResourceDriverMgmtDriver(LmDriver):
    """
    Client for managing Resource drivers
    """

    def __init__(self, lm_base, lm_security_ctrl=None):
        super().__init__(lm_base, lm_security_ctrl)

    def __resource_drivers_api(self):
        return '{0}/api/resource-manager/resource-drivers'.format(self.lm_base)

    def __resource_drivers_by_type_api(self, driver_type):
        return '{0}/api/resource-manager/resource-drivers?type={1}'.format(self.lm_base, driver_type)

    def __resource_driver_by_id_api(self, driver_id):
        return '{0}/api/resource-manager/resource-drivers/{1}'.format(self.lm_base, driver_id)

    def add_resource_driver(self, resource_driver):
        url = self.__resource_drivers_api()
        headers = self._configure_access_headers()
        response = requests.post(url, headers=headers, json=resource_driver, verify=False)
        if response.status_code == 201:
            location_header = response.headers['location']
            location_parts = location_header.split('/')
            driver_id = location_parts[len(location_parts)-1]
            resource_driver['id'] = driver_id
            return resource_driver
        else:
            self._raise_unexpected_status_exception(response)

    def delete_resource_driver(self, driver_id):
        url = self.__resource_driver_by_id_api(driver_id)
        headers = self._configure_access_headers()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            raise NotFoundException('No resource driver with id {0}'.format(driver_id))
        else:
            self._raise_unexpected_status_exception(response)

    def get_resource_driver(self, driver_id):
        url = self.__resource_driver_by_id_api(driver_id)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise NotFoundException('No resource driver with id {0}'.format(driver_id))
        else:
            self._raise_unexpected_status_exception(response)

    def get_resource_driver_by_type(self, driver_type):
        url = self.__resource_drivers_by_type_api(driver_type)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise NotFoundException('No resource driver with type {0}'.format(driver_type))
        else:
            self._raise_unexpected_status_exception(response)