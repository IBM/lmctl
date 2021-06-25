from pydantic.dataclasses import dataclass
from typing import Any, Dict
from dataclasses import field
from requests.auth import AuthBase
from .utils import convert_dict_to_yaml, convert_dict_to_json

class ValidationConfig:
    arbitrary_types_allowed = True

@dataclass(config=ValidationConfig)
class TNCOClientRequest:
    method: str
    endpoint: str = None
    headers: Dict[str, Any] = field(default_factory=dict)
    query_params: Dict[str, Any] = field(default_factory=dict)
    body: Any = None
    files: Dict[str, Any] = field(default_factory=dict)
    override_address: str = None
    inject_current_auth: bool = True
    additional_auth_handler: AuthBase = None

    def add_headers(self, headers: Dict[str, Any]) -> 'TNCOClientRequest':
        self.headers.update(headers)
        return self
    
    def add_query_params(self, query_params: Dict[str, Any]) -> 'TNCOClientRequest':
        self.query_params.update(query_params)
        return self

    def _set_body(self, body: Any) -> 'TNCOClientRequest':
        if self.body is not None:
            raise ValueError('Body already configured on request')
        self.body = body
    
    def add_json_body(self, data_dict: Dict) -> 'TNCOClientRequest':
        json_data = convert_dict_to_json(data_dict)
        self._set_body(json_data)
        self.add_headers({'Content-Type': 'application/json'})
        return self

    def add_yaml_body(self, data_dict: Dict) -> 'TNCOClientRequest':
        yaml_data = convert_dict_to_yaml(data_dict)
        self._set_body(yaml_data)
        self.add_headers({'Content-Type': 'application/yaml'})
        return self

    def add_form_data(self, form_dict: Dict[str, Any]) -> 'TNCOClientRequest':
        self._set_body(form_dict)
        self.add_headers({'Content-Type': 'application/x-www-form-urlencoded'})
        return self

    def add_files(self, files: Dict[str, Any]) -> 'TNCOClientRequest':
        self.files.update(files)
        return self
    
    def disable_auth_token(self) -> 'TNCOClientRequest':
        self.inject_current_auth = False
        return self

    def add_auth_handler(self, additional_auth_handler: AuthBase) -> 'TNCOClientRequest':
        self.additional_auth_handler = additional_auth_handler
        return self

    @staticmethod
    def build_request_for_json(endpoint: str, method: str = 'GET', query_params: Dict[str, Any] = None):
        if query_params is None:
            query_params = dict()
        return TNCOClientRequest(
            endpoint=endpoint,
            method=method,
            headers={
                'Accept': 'application/json'
            },
            query_params=query_params
        )