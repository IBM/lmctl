from typing import Dict
from .descriptors import DescriptorsAPI, obj_yaml_request_builder, yaml_response_handler, accept_yaml_or_json_header_request_builder
from .resource_api_base import ResourceAPIBase, ListAPIMeta, ReadAPIMeta, CreateAPIMeta, UpdateAPIMeta, DeleteAPIMeta

class DescriptorTemplatesAPI(DescriptorsAPI):
    endpoint = 'api/catalog/descriptorTemplates'

    def __init__(self, base_client: 'LmClient'):
        if base_client.kami_address is not None:
            self.override_address = base_client.kami_address
        else:
            self.override_address = None
        super().__init__(base_client)

    def render(self, template_name: str, render_request: Dict) -> Dict:
        endpoint = self._render_endpoint(template_name)
        request = obj_yaml_request_builder(render_request)
        request['headers']['Accept'] = 'application/yaml'
        request['method'] = 'POST'
        request['endpoint'] = endpoint
        if self.override_address is not None:
            request['override_address'] = self.override_address
        response = self.base_client.make_request(**request)
        return yaml_response_handler(response)

    def render_raw(self, template_name: str, render_request: Dict) -> str:
        endpoint = self._render_raw_endpoint(template_name)
        request = obj_yaml_request_builder(render_request)
        request['headers']['Accept'] = 'text/plain'
        request['method'] = 'POST'
        request['endpoint'] = endpoint
        if self.override_address is not None:
            request['override_address'] = self.override_address
        response = self.base_client.make_request(**request)
        return response.text

    def _render_endpoint(self, template_name: str) -> str:
        return f'{self.endpoint}/{template_name}/render'

    def _render_raw_endpoint(self, template_name: str) -> str:
        return f'{self.endpoint}/{template_name}/render-raw'

