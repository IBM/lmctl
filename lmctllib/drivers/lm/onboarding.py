import json
import requests
from ..exception import NotFoundException
from .exception import LmDriverExceptionBuilder

class LmOnboardRmDriver:
    """
    Client for LM Resource Manager Onboarding APIs
    """
    def __init__(self, lm_base, lm_security_ctrl=None):
        """
        Constructs a new instance of the driver

        Args:
            lm_base (str): the base URL of the target LM environment e.g. http://app.lm:32080
            lm_security_ctrl (:obj:`LmSecurityCtrl`): security controller to handle authentication with LM (leave empty if the target environment is insecure)
        """
        self.lm_base=lm_base
        self.lm_security_ctrl = lm_security_ctrl

    def __addAccessHeaders(self, headers=None):
        if headers is None:
            headers = {}
        if self.lm_security_ctrl:
            return self.lm_security_ctrl.addAccessHeaders(headers)
        return headers
  
    def updateRm(self, rm_name, rm_url):
        url = '{0}/api/resource-managers/{1}'.format(self.lm_base, rm_name)
        data =  {
            'name': rm_name,
            'url': rm_url
        }
        headers = self.__addAccessHeaders()
        response = requests.put(url, json=data, headers=headers, verify=False)
        if response.status_code == 404:
            raise NotFoundException('No resource manager with name {0}'.format(rm_name))
        elif response.status_code == 200:
            return True
        else:
            LmDriverExceptionBuilder.error(response)
    