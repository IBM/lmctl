import requests
from .base import LmDriver, NotFoundException

class LmResourcePkgDriver(LmDriver):
    """
    Client for CP4NA orchestration Resource Pkg APIs
    """

    def __init__(self, lm_base, lm_security_ctrl=None):
        super().__init__(lm_base, lm_security_ctrl)

    def __packages_api(self):
        return '{0}/api/resource-manager/resource-packages'.format(self.lm_base)

    def __package_api(self, resource_type_name):
        return '{0}/{1}'.format(self.__packages_api(), resource_type_name)

    def onboard_package(self, resource_pkg_path):
        url = self.__packages_api()
        headers = self._configure_access_headers()
        with open(resource_pkg_path, 'rb') as resource_pkg:
            files = {'file': resource_pkg}
            response = requests.post(url, headers=headers, files=files, verify=False)
            if response.status_code == 201:
                return True
            else:
                self._raise_unexpected_status_exception(response)

    def delete_package(self, resource_type_name):
        url = self.__package_api(resource_type_name)
        headers = self._configure_access_headers()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 404:
            raise NotFoundException('Package does not exist: {0}'.format(resource_type_name))
        elif response.status_code == 204:
            return True
        else:
            self._raise_unexpected_status_exception(response)

