import json
import requests
from .base import LmDriver, NotFoundException


class LmOnboardRmDriver(LmDriver):
    """
    Client for CP4NA orchestration Resource Manager Onboarding APIs
    """

    def __init__(self, lm_base, lm_security_ctrl=None):
        super().__init__(lm_base, lm_security_ctrl)

    def update_rm(self, rm_data):
        rm_name = rm_data['name']
        url = '{0}/api/resource-managers/{1}'.format(self.lm_base, rm_name)
        headers = self._configure_access_headers()
        response = requests.put(url, json=rm_data, headers=headers, verify=False)
        if response.status_code == 404:
            raise NotFoundException('No resource manager with name {0}'.format(rm_name))
        elif response.status_code == 200:
            return True
        else:
            self._raise_unexpected_status_exception(response)

    def get_rm_by_name(self, rm_name):
        url = '{0}/api/resource-managers/{1}'.format(self.lm_base, rm_name)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 404:
            raise NotFoundException('No resource manager with name {0}'.format(rm_name))
        elif response.status_code == 200:
            return response.json()
        else:
            self._raise_unexpected_status_exception(response)
