import logging
import requests
from .base import LmDriver, NotFoundException

logger = logging.getLogger(__name__)

class LmVimDriverMgmtDriver(LmDriver):
    """
    Client for managing VIM Drivers
    """

    def __init__(self, lm_base, lm_security_ctrl=None):
        super().__init__(lm_base, lm_security_ctrl)

    def __vim_drivers_api(self):
        return '{0}/api/resource-manager/vim-drivers'.format(self.lm_base)

    def __vim_drivers_by_type_api(self, inf_type):
        return '{0}/api/resource-manager/vim-drivers?infrastructureType={1}'.format(self.lm_base, inf_type)

    def __vim_driver_by_id_api(self, driver_id):
        return '{0}/api/resource-manager/vim-drivers/{1}'.format(self.lm_base, driver_id)

    def add_vim_driver(self, vim_driver):
        url = self.__vim_drivers_api()
        headers = self._configure_access_headers()
        response = requests.post(url, headers=headers, json=vim_driver, verify=False)
        if response.status_code == 201:
            location_header = response.headers['location']
            location_parts = location_header.split('/')
            driver_id = location_parts[len(location_parts)-1]
            vim_driver['id'] = driver_id
            return vim_driver
        else:
            self._raise_unexpected_status_exception(response)

    def delete_vim_driver(self, driver_id):
        url = self.__vim_driver_by_id_api(driver_id)
        headers = self._configure_access_headers()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            raise NotFoundException('No VIM driver with id {0}'.format(driver_id))
        else:
            self._raise_unexpected_status_exception(response)

    def get_vim_driver(self, driver_id):
        url = self.__vim_driver_by_id_api(driver_id)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise NotFoundException('No VIM driver with id {0}'.format(driver_id))
        else:
            self._raise_unexpected_status_exception(response)

    def get_vim_driver_by_type(self, inf_type):
        url = self.__vim_drivers_by_type_api(inf_type)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise NotFoundException('No VIM driver with infrastructure type {0}'.format(inf_type))
        else:
            self._raise_unexpected_status_exception(response)