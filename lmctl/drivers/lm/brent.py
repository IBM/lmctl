import logging
import requests
from .base import LmDriver

logger = logging.getLogger(__name__)

class LmBrentDriver(LmDriver):
    """
    Client for LM Brent APIs
    """

    def __init__(self, lm_base, lm_security_ctrl=None):
        super().__init__(lm_base, lm_security_ctrl)

    def __vim_drivers_api(self):
        return '{0}/api/resource-manager/vim-drivers'.format(self.lm_base)

    def __lifecycle_drivers_api(self):
        return '{0}/api/resource-manager/lifecycle-drivers'.format(self.lm_base)

    def __vim_drivers_by_type_api(self, type):
        return '{0}/api/resource-manager/vim-drivers?infrastructureType={1}'.format(self.lm_base, type)

    def __lifecycle_drivers_by_type_api(self, type):
        return '{0}/api/resource-manager/lifecycle-drivers?type={1}'.format(self.lm_base, type)

    def __vim_driver_by_id_api(self, id):
        return '{0}/api/resource-manager/vim-drivers/{1}'.format(self.lm_base, id)

    def __lifecycle_driver_by_id_api(self, id):
        return '{0}/api/resource-manager/lifecycle-drivers/{1}'.format(self.lm_base, id)

    def add_vim_driver(self, vim_driver):
        url = self.__vim_drivers_api()
        headers = self._configure_access_headers()
        response = requests.post(url, headers=headers, json=vim_driver, verify=False)
        if response.status_code == 201:
            return 'Success: created VIM driver \'{0}\''.format(vim_driver)
        elif response.status_code == 409:
            return 'Failed: VIM driver \'{0}\' already exists'.format(vim_driver)
        else:
            self._raise_unexpected_status_exception(response)

    def add_lifecycle_driver(self, lifecycle_driver):
        url = self.__lifecycle_drivers_api()
        headers = self._configure_access_headers()
        response = requests.post(url, headers=headers, json=lifecycle_driver, verify=False)
        if response.status_code == 201:
            return 'Success: created Lifecycle driver \'{0}\''.format(lifecycle_driver)
        elif response.status_code == 409:
            return 'Failed: Lifecycle driver \'{0}\' already exists'.format(lifecycle_driver)
        else:
            self._raise_unexpected_status_exception(response)

    def remove_vim_driver(self, id):
        url = self.__vim_driver_by_id_api(id)
        headers = self._configure_access_headers()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 204:
            return True
        else:
            self._raise_unexpected_status_exception(response)

    def remove_lifecycle_driver(self, id):
        url = self.__lifecycle_driver_by_id_api(id)
        headers = self._configure_access_headers()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 204:
            return True
        else:
            self._raise_unexpected_status_exception(response)

    def get_vim_drivers_by_type(self, type):
        url = self.__vim_drivers_by_type_api(type)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return [response.json()]
        elif response.status_code == 404:
            return []
        else:
            self._raise_unexpected_status_exception(response)

    def get_lifecycle_drivers_by_type(self, type):
        url = self.__lifecycle_drivers_by_type_api(type)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return [response.json()]
        elif response.status_code == 404:
            return []
        else:
            self._raise_unexpected_status_exception(response)