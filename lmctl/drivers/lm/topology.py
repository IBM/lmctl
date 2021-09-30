import json
import requests
from .base import LmDriver, NotFoundException


class LmTopologyDriver(LmDriver):
    """
    Client for CP4NA orchestration Topology APIs
    """

    def __init__(self, lm_base, lm_security_ctrl=None):
        super().__init__(lm_base, lm_security_ctrl)

    def get_assembly_by_name(self, assembly_name):
        url = '{0}/api/topology/assemblies/?name={1}'.format(self.lm_base, assembly_name)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise NotFoundException('No assembly with name {0}'.format(assembly_name))
        else:
            self._raise_unexpected_status_exception(response)

    def delete_assembly(self, assembly_id):
        url = '{0}/api/topology/assemblies/{1}'.format(self.lm_base, assembly_id)
        headers = self._configure_access_headers()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 204:
            return True
        else:
            self._raise_unexpected_status_exception(response)
