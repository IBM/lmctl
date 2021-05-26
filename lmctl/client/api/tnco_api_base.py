from typing import Dict, Callable, List
from lmctl.client.client_request import TNCOClientRequest
from lmctl.client.exceptions import TNCOClientError
from lmctl.client.utils import (build_relative_endpoint, convert_dict_to_json, build_relative_endpoint_from_data, 
                        read_response_location_header, read_response_body_as_json, read_response_body_as_yaml, 
                        read_response_body_as_plaintext)
import yaml
import json
import requests


def default_create_response_handler_placeholder(response):
    pass

class TNCOAPI:
    id_attr = 'id'

    def __init__(self, base_client: 'TNCOClient'):
        self.base_client = base_client

    def _get_json(self, endpoint: str, query_params: Dict[str,str] = None):
        request = TNCOClientRequest.build_request_for_json(endpoint=endpoint)
        if query_params is not None:
            request.query_params.update(query_params)
        return self._exec_request_and_parse_json(request)

    def _exec_request(self, request: TNCOClientRequest, response_handler: Callable = None):
        response = self.base_client.make_request(request)
        if response_handler is not None:
            return response_handler(response=response)

    def _exec_request_and_parse_json(self, request: TNCOClientRequest) -> Dict:
        return self._exec_request(request, response_handler=read_response_body_as_json)

    def _exec_request_and_parse_yaml(self, request: TNCOClientRequest) -> Dict:
        return self._exec_request(request, response_handler=read_response_body_as_yaml)

    def _exec_request_and_parse_plaintext(self, request: TNCOClientRequest) -> str:
        return self._exec_request(request, response_handler=read_response_body_as_plaintext)

    def _exec_request_and_get_location_header(self, request: TNCOClientRequest) -> str:
        return self._exec_request(request, response_handler=read_response_location_header)

    def _all(self, query_params: Dict[str,str] = None, endpoint: str = None) -> List:
        if endpoint is None:
            endpoint = self.endpoint
        return self._get_json(
            endpoint=endpoint,
            query_params=query_params
        )

    def _get(self, id_value: str, query_params: Dict[str,str] = None, endpoint: str = None) -> Dict:
        if endpoint is None:
            endpoint = self.endpoint
        return self._get_json(
            endpoint=build_relative_endpoint(base_endpoint=endpoint, id_value=id_value),
            query_params=query_params
        )

    def _create(self, obj: Dict, endpoint: str = None, response_handler: Callable = default_create_response_handler_placeholder):
        if endpoint is None:
            endpoint = self.endpoint
        request = TNCOClientRequest(method='POST', endpoint=endpoint).add_json_body(obj)
        if response_handler == default_create_response_handler_placeholder:
            id_value = self._exec_request(request, response_handler=read_response_location_header)
            obj[self.id_attr] = id_value
            return obj
        else:
            return self._exec_request(request, response_handler=response_handler)

    def _update(self, obj: Dict, id_attr: str  = None, endpoint: str = None, response_handler: Callable = None):
        if id_attr is None:
            id_attr = self.id_attr
        if endpoint is None:
            endpoint = self.endpoint
        request = TNCOClientRequest(
                        method='PUT',
                        endpoint=build_relative_endpoint_from_data(data_dict=obj, id_attr=id_attr, base_endpoint=endpoint)
                    ).add_json_body(obj)
        return self._exec_request(request, response_handler=response_handler)

    def _delete(self, id_value: str, endpoint: str = None):
        if endpoint is None:
            endpoint = self.endpoint
        request = TNCOClientRequest(
            method='DELETE',
            endpoint=build_relative_endpoint(base_endpoint=endpoint, id_value=id_value)
        )
        self._exec_request(request)