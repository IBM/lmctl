import logging
import requests
from .base import LmDriver, NotFoundException

logger = logging.getLogger(__name__)

class PackageMgmtDriver(LmDriver):
    """
    Client for managing packages
    """

    def __init__(self, lm_base, lm_security_ctrl=None):
        super().__init__(lm_base, lm_security_ctrl)

    def __packages_api(self):
        return '{0}/api/etsi/vnfpkgm/v2/vnf_packages'.format(self.lm_base)

    def __packages_api_by_id_api(self, package_id):
        return '{0}/api/etsi/vnfpkgm/v2/vnf_packages/{1}'.format(self.lm_base, package_id)

    def __packages_api_package_content(self, package_id):
        return '{0}/api/etsi/vnfpkgm/v2/vnf_packages/{1}/package_content'.format(self.lm_base, package_id)

    def __configure_headers(self, content_type='application/json'):
        headers = self._configure_access_headers()
        headers['Version'] = '2.0.0'
        headers['Content-Type'] = content_type
        return headers


    def create_package(self, package_user_data):
        url = self.__packages_api()
        headers = self.__configure_headers()
        response = requests.post(url, headers=headers, json=package_user_data, verify=False)
        if response.status_code == 201:
            return response.json()
        else:
            self._raise_unexpected_status_exception(response)

    def upload_package_content(self, package_id, resource_pkg_path):
        url = self.__packages_api_content(package_id)
        headers = self.__configure_headers('application/zip')
        with open(resource_pkg_path, 'rb') as resource_pkg:            
            response = requests.put(url, headers=headers, data=resource_pkg, verify=False)
            if response.status_code == 202:
                return True
            else:
                self._raise_unexpected_status_exception(response)        

    def delete_package(self, package_id):
        url = self.__packages_api_by_id_api(package_id)
        headers = self.__configure_headers()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            raise NotFoundException('No package with id {0}'.format(package_id))
        else:
            self._raise_unexpected_status_exception(response)

    def get_package_details(self, package_id):
        url = self.__packages_api_by_id_api(package_id)
        headers = self.__configure_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise NotFoundException('No package with id {0}'.format(package_id))
        else:
            self._raise_unexpected_status_exception(response)

    #def get_package_details(self, package_id):

