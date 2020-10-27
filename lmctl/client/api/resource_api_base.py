import requests 
import urllib
from typing import Dict, List, Any, Callable, Union
from lmctl.client.exceptions import LmClientError
from .api_base import APIBase

def json_response_handler(response, *args, **kwargs):
    try:
        return response.json()
    except ValueError as e:
        raise LmClientError(f'Failed to parse response as JSON: {str(e)}') from e

def location_id_suplemented_response_handler(response: requests.Response, obj: Dict, id_attr: str, *args, **kwargs) -> Dict:
    location_header = response.headers.get('Location', response.headers.get('location', None))
    if location_header is None:
        raise LmClientError(f'Failed to find location header in response')
    location_parts = location_header.split('/')
    id_value = location_parts[len(location_parts)-1]
    obj[id_attr] = id_value
    return obj

def location_id_response_handler(response: requests.Response, *args, **kwargs) -> str:
    location_header = response.headers.get('Location', response.headers.get('location', None))
    if location_header is None:
        raise LmClientError(f'Failed to find location header in response')
    location_parts = location_header.split('/')
    id_value = location_parts[len(location_parts)-1]
    return id_value

def id_path_builder(endpoint: str, id_value: str, *args, extra_request_params: Dict = None, **kwargs):
    built_endpoint = f'{endpoint}/{id_value}'
    if extra_request_params is not None and len(extra_request_params) > 0:
        built_endpoint = f'{built_endpoint}?{urllib.parse.urlencode(extra_request_params)}'
    return built_endpoint

def query_param_builder(endpoint: str, *args, extra_request_params: Dict = None, **kwargs):
    built_endpoint = endpoint
    if extra_request_params is not None and len(extra_request_params) > 0:
        built_endpoint = f'{built_endpoint}?{urllib.parse.urlencode(extra_request_params)}'
    return built_endpoint

def obj_json_request_builder(obj: Dict, *args, **kwargs) -> Dict:
    return {
        'json': obj
    }

def noop_builder(*args, **kwargs) -> Dict:
    return {}

class APIArg:
    def __init__(self, param_name: str = None, validator: Callable = None):
        self.param_name = param_name
        self.validator = validator

class ListAPIMeta:
    def __init__(self, method: str = 'GET', 
                        request_builder: Callable = noop_builder, 
                        endpoint_builder: Callable = query_param_builder, 
                        response_handler: Callable = json_response_handler,
                        extra_request_params: Dict = None):
        self.method = method
        self.request_builder = request_builder
        self.endpoint_builder = endpoint_builder
        self.response_handler = response_handler
        self.extra_request_params = extra_request_params

class ReadAPIMeta:
    def __init__(self, method: str = 'GET', 
                        request_builder: Callable = noop_builder, 
                        endpoint_builder: Callable = id_path_builder, 
                        response_handler: Callable = json_response_handler,
                        extra_request_params: Dict = None):
        self.method = method
        self.request_builder = request_builder
        self.endpoint_builder = endpoint_builder
        self.response_handler = response_handler
        self.extra_request_params = extra_request_params

class CreateAPIMeta:
    def __init__(self, method: str = 'POST', request_builder: Callable = obj_json_request_builder, endpoint_builder: Callable = None, response_handler: Callable = location_id_suplemented_response_handler):
        self.method = method
        self.request_builder = request_builder
        self.endpoint_builder = endpoint_builder
        self.response_handler = response_handler

class UpdateAPIMeta:
    def __init__(self, method: str = 'PUT', request_builder: Callable = obj_json_request_builder, endpoint_builder: Callable = id_path_builder, response_handler: Callable = None):
        self.method = method
        self.request_builder = request_builder
        self.endpoint_builder = endpoint_builder
        self.response_handler = response_handler

class DeleteAPIMeta:
    def __init__(self, method: str = 'DELETE', request_builder: Callable = noop_builder, endpoint_builder: Callable = id_path_builder, response_handler: Callable = None):
        self.method = method
        self.request_builder = request_builder
        self.endpoint_builder = endpoint_builder
        self.response_handler = response_handler

class ResourceAPIBase(APIBase):

    def __init__(self, base_client: 'LmClient'):
        super().__init__(base_client)
        if not hasattr(self, 'endpoint'):
            raise ValueError(f'Subclass of ResourceAPIBase must set "endpoint" class attribute: Subclass={self.__class__.__name__}')
        if not hasattr(self, 'id_attr'):
            self.id_attr = 'id'
        self._populate_functions()

    def _populate_functions(self):
        if getattr(self, 'enable_list_api', True) is True:
            self.all = self._list_api_impl
            if getattr(self, 'list_meta', None) is None:
                self.list_meta = ListAPIMeta()
        if getattr(self, 'enable_read_api', True) is True:
            self.get = self._read_api_impl
            if getattr(self, 'read_meta', None) is None:
                self.read_meta = ReadAPIMeta()
        if getattr(self, 'enable_create_api', True) is True:
            self.create = self._create_api_impl
            if getattr(self, 'create_meta', None) is None:
                self.create_meta = CreateAPIMeta()
        if getattr(self, 'enable_update_api', True) is True:
            self.update = self._update_api_impl
            if getattr(self, 'update_meta', None) is None:
                self.update_meta = UpdateAPIMeta()
        if getattr(self, 'enable_delete_api', True) is True:
            self.delete = self._delete_api_impl
            if getattr(self, 'delete_meta', None) is None:
                self.delete_meta = DeleteAPIMeta()

    def _get_endpoint(self, endpoint: str, meta: Union[ListAPIMeta, ReadAPIMeta, CreateAPIMeta, UpdateAPIMeta, DeleteAPIMeta], *args, **kwargs) -> str:
        if meta.endpoint_builder is not None:
            return meta.endpoint_builder(endpoint, *args, **kwargs)
        return endpoint

    def _build_request_kwargs(self, method: str, endpoint: str, request_builder: Dict = None):
        request_kwargs = {}
        if request_builder is not None:
            request_kwargs.update(request_builder)
        request_kwargs['method'] = method
        request_kwargs['endpoint'] = endpoint
        if hasattr(self, 'override_address') and getattr(self, 'override_address') is not None:
            request_kwargs['override_address'] = self.override_address
        return request_kwargs

    def _list_api_impl(self, **kwargs) -> List:
        extra_request_params = self._parse_extra_args(self.list_meta, **kwargs)
        endpoint = self._get_endpoint(self.endpoint, self.list_meta, extra_request_params=extra_request_params)
        request_builder = self.list_meta.request_builder(id_attr=self.id_attr)
        request = self._build_request_kwargs(self.list_meta.method, endpoint, request_builder)
        response = self.base_client.make_request(**request)
        return self.list_meta.response_handler(response=response, id_attr=self.id_attr)

    def _read_api_impl(self, id_value, **kwargs):
        extra_request_params = self._parse_extra_args(self.read_meta, **kwargs)
        endpoint = self._get_endpoint(self.endpoint, self.read_meta, id_value=id_value, id_attr=self.id_attr, extra_request_params=extra_request_params)
        request_builder = self.read_meta.request_builder(id_value=id_value, id_attr=self.id_attr)
        request = self._build_request_kwargs(self.read_meta.method, endpoint, request_builder)
        response = self.base_client.make_request(**request)
        return self.read_meta.response_handler(response=response, id_value=id_value, id_attr=self.id_attr)

    def _create_api_impl(self, obj: Dict):
        endpoint = self._get_endpoint(self.endpoint, self.create_meta, obj=obj, id_attr=self.id_attr)
        request_builder = self.create_meta.request_builder(obj=obj, id_attr=self.id_attr)
        request = self._build_request_kwargs(self.create_meta.method, endpoint, request_builder)
        response = self.base_client.make_request(**request)
        if self.create_meta.response_handler is not None:
            return self.create_meta.response_handler(response=response, obj=obj, id_attr=self.id_attr)

    def _update_api_impl(self, obj: Dict):
        id_value = obj.get(self.id_attr, None)
        if id_value is None:
            raise LmClientError(f'Cannot update object missing "{self.id_attr}" attribute value')
        endpoint = self._get_endpoint(self.endpoint, self.update_meta, obj=obj, id_value=id_value, id_attr=self.id_attr)
        request_builder = self.update_meta.request_builder(obj=obj, id_value=id_value, id_attr=self.id_attr)
        request = self._build_request_kwargs(self.update_meta.method, endpoint, request_builder)
        response = self.base_client.make_request(**request)
        if self.update_meta.response_handler is not None:
            return self.update_meta.response_handler(response=response, obj=obj, id_value=id_value, id_attr=self.id_attr)

    def _delete_api_impl(self, id_value: str):
        endpoint = self._get_endpoint(self.endpoint, self.delete_meta, id_value=id_value, id_attr=self.id_attr)
        request_builder = self.delete_meta.request_builder(id_value=id_value, id_attr=self.id_attr)
        request = self._build_request_kwargs(self.delete_meta.method, endpoint, request_builder)
        response = self.base_client.make_request(**request)
        if self.delete_meta.response_handler is not None:
            return self.delete_meta.response_handler(response=response, id_value=id_value, id_attr=self.id_attr)

    def _build_endpoint_to_instance(self, id_value: str) -> str:
        return f'{self.endpoint}/{id_value}'

    def _parse_extra_args(self, meta: Union[ListAPIMeta, ReadAPIMeta, CreateAPIMeta, UpdateAPIMeta, DeleteAPIMeta], **kwargs):
        extra_request_params = {}
        if hasattr(meta, 'extra_request_params'):
            extra_request_param_defs = meta.extra_request_params
            for k,v in kwargs.items():
                if k not in extra_request_param_defs:
                    raise ValueError(f'Unknown keyword arg passed to request: {k}')
                if extra_request_param_defs[k].validator is not None:
                    extra_request_param_defs[k].validator(v)
                param_name = k
                if extra_request_param_defs[k].param_name is not None:
                    param_name = extra_request_param_defs[k].param_name
                extra_request_params[param_name] = v
        return extra_request_params
                