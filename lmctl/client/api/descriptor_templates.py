from typing import Dict
from .descriptors import DescriptorsAPI, obj_yaml_request_builder, yaml_response_handler

class DescriptorTemplatesAPI(DescriptorsAPI):
    endpoint = 'api/catalog/descriptorTemplates'

    def render(self, template_name: str, render_request: Dict) -> Dict:
        endpoint = self._render_endpoint(template_name)
        request = obj_yaml_request_builder(render_request)
        request['method'] = 'POST'
        request['endpoint'] = endpoint
        response = self.base_client.make_request(**request)
        return yaml_response_handler(response)

    def render_raw(self, template_name: str, render_request: Dict) -> str:
        endpoint = self._render_raw_endpoint(template_name)
        request = obj_yaml_request_builder(render_request)
        request['method'] = 'POST'
        request['endpoint'] = endpoint
        response = self.base_client.make_request(**request)
        return response.text

    def _render_endpoint(self, template_name: str) -> str:
        return f'{self.endpoint}/{template_name}/render'

    def _render_raw_endpoint(self, template_name: str) -> str:
        return f'{self.endpoint}/{template_name}/render-raw'

