import json
import requests

class AnsibleRmDriver:
    """
    Handles communication with a target Ansible RM
    """
    def __init__(self, ansible_rm_base):
        self.ansible_rm_base=ansible_rm_base

    def onboardType(self, resource_name, resource_version, resource_csar):
        """Push a Resource to the target Ansible RM"""
        url = '{0}/api/v1.0/resource-manager/types'.format(self.ansible_rm_base)
        files = {'upfile': open(resource_csar,'rb')}
        data = {
            'resource_name': resource_name,
            'resource_version': resource_version 
        }
        response = requests.post(url, files=files, data=data, verify=False)
        if response.status_code == 200:
            return True
        else:
            AnsibleRmDriverExceptionBuilder.error(response)

class AnsibleRmDriverException(Exception):
    pass

class AnsibleRmDriverExceptionBuilder:

    def __init__(self):
        pass

    @staticmethod
    def error(response):
        raise AnsibleRmDriverException('Request returned unexpected status code: {0}'.format(response.status_code))

