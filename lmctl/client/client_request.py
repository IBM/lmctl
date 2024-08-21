from pydantic.dataclasses import dataclass
from typing import Any, Dict, Optional
from dataclasses import field
from requests.auth import AuthBase

import copy

class ValidationConfig:
    arbitrary_types_allowed = True

@dataclass(config=ValidationConfig)
class TNCOClientRequest:
    method: str
    endpoint: Optional[str] = None
    headers: Dict[str, Any] = field(default_factory=dict)
    query_params: Dict[str, Any] = field(default_factory=dict)
    body: Any = None
    files: Dict[str, Any] = field(default_factory=dict)
    override_address: Optional[str] = None
    inject_current_auth: bool = True
    additional_auth_handler: AuthBase = None
    object_group_id_param: Optional[str] = None
    object_group_id_body: Optional[str] = None

    def __post_init__(self):
        if self.object_group_id_body is not None:
            self.add_object_group_id_body(self.object_group_id_body)
        
        if not (self.endpoint or self.override_address):
            raise ValueError("At least one of endpoint or override_address must be set")

    def add_headers(self, headers: Dict[str, Any]) -> 'TNCOClientRequest':
        self.headers.update(headers)
        return self
    
    def add_query_params(self, query_params: Dict[str, Any]) -> 'TNCOClientRequest':
        self.query_params.update(query_params)
        return self
    
    def add_object_group_id_param(self, object_group_id: str) -> 'TNCOClientRequest':
        self.object_group_id_param = object_group_id
        return self
    
    def add_object_group_id_body(self, object_group_id: str) -> 'TNCOClientRequest':
        if self.body is None:
            raise ValueError('Cannot add object_group_id to body as body has not been set')
        self.object_group_id_body = object_group_id
        if isinstance(self.body, dict):
            self.body['objectGroupId'] = object_group_id
        else:
            body_type = type(self.body)
            raise ValueError(f'Cannot add object_group_id to body as body is not a dictionary. Existing body is of type {body_type}')
        return self

    def _set_body(self, body: Any) -> 'TNCOClientRequest':
        if self.body is not None:
            raise ValueError('Body already configured on request')
        self.body = body

    def add_json_body(self, data_dict: Dict) -> 'TNCOClientRequest':
        self._set_body(copy.deepcopy(data_dict))
        self.add_headers({'Content-Type': 'application/json'})
        return self

    def add_yaml_body(self, data_dict: Dict) -> 'TNCOClientRequest':
        self._set_body(copy.deepcopy(data_dict))
        self.add_headers({'Content-Type': 'application/yaml'})
        return self

    def add_form_data(self, form_dict: Dict[str, Any]) -> 'TNCOClientRequest':
        self._set_body(copy.deepcopy(form_dict))
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
    def build_request_for_json(endpoint: str, method: str = 'GET', query_params: Dict[str, Any] = None, object_group_id: str = None):
        if query_params is None:
            query_params = dict()
        return TNCOClientRequest(
            endpoint=endpoint,
            method=method,
            headers={
                'Accept': 'application/json'
            },
            query_params=query_params,
            object_group_id_param=object_group_id
        )