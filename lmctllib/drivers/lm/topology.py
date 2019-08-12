import json
import requests
from ..exception import NotFoundException
from .exception import LmDriverExceptionBuilder

class LmTopologyDriver:
    """
    Client for LM Topology APIs
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
  
    def getAssemblyByName(self, assembly_name):
        url = '{0}/api/topology/assemblies/?name={1}'.format(self.lm_base, assembly_name)
        headers = self.__addAccessHeaders()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            raise NotFoundException('No assembly with name {0}'.format(assembly_name))
        else:
            LmDriverExceptionBuilder.error(response)

    def deleteAssembly(self, assembly_id):
        url = '{0}/api/topology/assemblies/{1}'.format(self.lm_base, assembly_id)
        headers = self.__addAccessHeaders()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 204:
            return True
        else:
            LmDriverExceptionBuilder.error(response)
    