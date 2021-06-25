import json
import requests
import logging
from .base import LmDriver, NotFoundException

logger = logging.getLogger(__name__)


class LmDescriptorTemplatesDriver(LmDriver):
    """
    Client for CP4NA orchestration Descriptor Template APIs
    """

    TEMPLATES_API = 'api/catalog/descriptorTemplates'

    def __init__(self, lm_base):
        super().__init__(lm_base)

    def delete_descriptor_template(self, descriptor_name):
        url = '{0}/{1}/{2}'.format(self.lm_base, self.TEMPLATES_API, descriptor_name)
        headers = self._configure_access_headers()
        response = requests.delete(url, headers=headers, verify=False)
        if response.status_code == 404:
            raise NotFoundException('No descriptor template with name {0}'.format(descriptor_name))
        elif response.status_code == 204:
            return True
        else:
            self._raise_unexpected_status_exception(response)

    def get_descriptor_template(self, descriptor_name):
        url = '{0}/{1}/{2}'.format(self.lm_base, self.TEMPLATES_API, descriptor_name)
        headers = {
            'Accept': 'application/yaml'
        }
        headers = self._configure_access_headers(headers)
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 404:
            raise NotFoundException('No descriptor template with name {0}'.format(descriptor_name))
        elif response.status_code == 200:
            return response.text
        else:
            self._raise_unexpected_status_exception(response)

    def create_descriptor_template(self, descriptor_content):
        url = '{0}/{1}'.format(self.lm_base, self.TEMPLATES_API)
        headers = {
            'Content-Type': 'application/yaml'
        }
        headers = self._configure_access_headers(headers)
        response = requests.post(url, headers=headers, data=descriptor_content, verify=False)
        if response.status_code == 201:
            return True
        else:
            self._raise_unexpected_status_exception(response)

    def update_descriptor_template(self, descriptor_name, descriptor_content):
        url = '{0}/{1}/{2}'.format(self.lm_base, self.TEMPLATES_API, descriptor_name)
        headers = {
            'Content-Type': 'application/yaml'
        }
        headers = self._configure_access_headers(headers)
        response = requests.put(url, headers=headers, data=descriptor_content, verify=False)
        if response.status_code == 200:
            return True
        else:
            self._raise_unexpected_status_exception(response)

