import json
import requests
import logging
from ..exception import NotFoundException
from .exception import LmDriverExceptionBuilder

logger = logging.getLogger(__name__)

class LmDescriptorDriver:
    """
    Client for LM Descriptor APIs
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

    def deleteDescriptor(self, descriptor_name):
        url = '{0}/api/catalog/descriptors/{1}'.format(self.lm_base, descriptor_name)
        headers = self.__addAccessHeaders()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 404:
            raise NotFoundException('No descriptor with name {0}'.format(descriptor_name))
        elif response.status_code == 204:
            return True
        else:
            LmDriverExceptionBuilder.error(response)

    def getDescriptor(self, descriptor_name):
        url = '{0}/api/catalog/descriptors/{1}'.format(self.lm_base, descriptor_name)
        headers =  {
            'Accept': 'application/yaml'
        }
        headers = self.__addAccessHeaders(headers)
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 404:
            raise NotFoundException('No descriptor with name {0}'.format(descriptor_name))
        elif response.status_code == 200:
            return response.text
        else:
            LmDriverExceptionBuilder.error(response)

    def createDescriptor(self, descriptor_content):
        url = '{0}/api/catalog/descriptors'.format(self.lm_base)
        headers =  {
            'Content-Type': 'application/yaml'
        }
        headers = self.__addAccessHeaders(headers)
        response = requests.post(url, headers=headers, data=descriptor_content, verify=False)
        if response.status_code == 201:
            return True
        else:
            LmDriverExceptionBuilder.error(response)

    def updateDescriptor(self, descriptor_name, descriptor_content):
        url = '{0}/api/catalog/descriptors/{1}'.format(self.lm_base, descriptor_name)
        headers =  {
            'Content-Type': 'application/yaml'
        }
        headers = self.__addAccessHeaders(headers)
        response = requests.put(url, headers=headers, data=descriptor_content, verify=False)
        if response.status_code == 200:
            return True
        else:
            LmDriverExceptionBuilder.error(response)
    