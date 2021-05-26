from typing import Dict
from lmctl.client.client_request import TNCOClientRequest
from .descriptors import DescriptorsAPI

class DescriptorTemplatesAPI(DescriptorsAPI):
    endpoint = 'api/catalog/descriptorTemplates'

    def __init__(self, base_client: 'TNCOClient'):
        if base_client.kami_address is not None:
            self.override_address = base_client.kami_address
        else:
            self.override_address = None
        super().__init__(base_client)

    def render(self, template_name: str, render_request: Dict) -> Dict:
        if render_request is None:
            render_request = {}
        endpoint = self._render_endpoint(template_name)
        request = TNCOClientRequest(method='POST', endpoint=endpoint)\
                        .add_yaml_body(render_request)\
                        .add_headers({'Accept': 'application/yaml'})
        if self.override_address is not None:
            request.override_address = self.override_address
        return self._exec_request_and_parse_yaml(request)

    def render_raw(self, template_name: str, render_request: Dict) -> str:
        if render_request is None:
            render_request = {}
        endpoint = self._render_raw_endpoint(template_name)
        request = TNCOClientRequest(method='POST', endpoint=endpoint)\
                        .add_yaml_body(render_request)\
                        .add_headers({'Accept': 'text/plain'})
        if self.override_address is not None:
            request.override_address = self.override_address
        return self._exec_request_and_parse_plaintext(request)

    def _render_endpoint(self, template_name: str) -> str:
        return f'{self.endpoint}/{template_name}/render'

    def _render_raw_endpoint(self, template_name: str) -> str:
        return f'{self.endpoint}/{template_name}/render-raw'

