import yaml
from typing import List, Dict
from lmctl.client.client_request import TNCOClientRequest
from .tnco_api_base import TNCOAPI
from lmctl.client.utils import build_relative_endpoint_from_data, build_relative_endpoint


class DescriptorsAPI(TNCOAPI):
    endpoint = 'api/catalog/descriptors'
    id_attr = 'name'

    def create(self, descriptor: Dict, object_group_id: str = None):
        request = TNCOClientRequest(method='POST', endpoint=self.endpoint).add_yaml_body(descriptor)
        if object_group_id is not None:
            request.add_object_group_id_param(object_group_id)
        request.override_address = getattr(self, 'override_address') if hasattr(self, 'override_address') else None
        self._exec_request(request)

    def update(self, descriptor: Dict):
        request = TNCOClientRequest(method='PUT', 
                                    endpoint=build_relative_endpoint_from_data(data_dict=descriptor, id_attr='name', base_endpoint=self.endpoint)
                                ).add_yaml_body(descriptor)
        request.override_address = getattr(self, 'override_address') if hasattr(self, 'override_address') else None
        self._exec_request(request)

    def delete(self, name: str):
        request = TNCOClientRequest(method='DELETE', endpoint=build_relative_endpoint(id_value=name, base_endpoint=self.endpoint))
        request.override_address = getattr(self, 'override_address') if hasattr(self, 'override_address') else None
        self._exec_request(request)

    def get(self, name: str, effective: bool = None) -> Dict:
        query_params = {}
        if effective is not None:
            query_params['effective'] = effective
        request = TNCOClientRequest(
                        method='GET',
                        endpoint=build_relative_endpoint(base_endpoint=self.endpoint, id_value=name)
                    ).add_headers({'Accept': 'application/yaml,application/json'})\
                    .add_query_params(query_params)
        request.override_address = getattr(self, 'override_address') if hasattr(self, 'override_address') else None
        return self._exec_request_and_parse_yaml(request)

    def all(self, object_group_id: str = None) -> List:
        request = TNCOClientRequest(
                        method='GET',
                        endpoint=self.endpoint,
                    ).add_headers({'Accept': 'application/yaml,application/json'})
        if object_group_id is not None:
            request.add_object_group_id_param(object_group_id)
        request.override_address = getattr(self, 'override_address') if hasattr(self, 'override_address') else None
        return self._exec_request_and_parse_yaml(request)

