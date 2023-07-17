import yaml
import json
import requests
from typing import Dict
from lmctl.client.exceptions import TNCOClientError

def clean_address(address: str) -> str:
    if address is not None:
        while address.endswith('/'):
            address = address[:-1]
    return address

def clean_path(path: str) -> str:
    if path is not None:
        while path.startswith('/'):
            path = path[1]
    return path

def choose_first_not_none(*args):
    for arg in args:
        if arg is not None:
            return arg

def append_endpoint(address: str, endpoint: str):
    while address.endswith('/'):
        address = address[:-1]
    
    if endpoint.startswith('/'):
        return address + endpoint
    else:
        return address + '/' + endpoint

def convert_dict_to_yaml(data_dict: Dict):
    return yaml.safe_dump(data_dict)

def convert_dict_to_json(data_dict: Dict):
    return json.dumps(data_dict)

def read_response_body_as_plaintext(response: requests.Response) -> Dict:
    try:
        return response.text
    except ValueError as e:
        raise TNCOClientError(f'Failed to parse response as plain text: {str(e)}') from e

def read_response_body_as_yaml(response: requests.Response) -> Dict:
    try:
        return yaml.safe_load(response.text)
    except yaml.YAMLError as e:
        raise TNCOClientError(f'Failed to parse response as YAML: {str(e)}') from e

def read_response_body_as_json(response: requests.Response, error_class = TNCOClientError) -> Dict:
    try:
        return response.json()
    except ValueError as e:
        raise error_class(f'Failed to parse response as JSON: {str(e)}') from e

def read_response_location_header(response: requests.Response, error_class = TNCOClientError) -> str:
    location_header = response.headers.get('Location', response.headers.get('location', None))
    if location_header is None:
        raise error_class(f'Failed to find location header in response')
    location_parts = location_header.split('/')
    id_value = location_parts[len(location_parts)-1]
    if (id_value is None or len(id_value.strip())) == 0 and location_header.endswith('/'):
        id_value = location_parts[len(location_parts)-2]
    return id_value

def build_relative_endpoint_from_data(data_dict: Dict, id_attr: str, base_endpoint: str) -> str:
    id_value = data_dict.get(id_attr, None)
    if id_value is None:
        raise TNCOClientError(f'Cannot build API endpoint path for object missing "{id_attr}" attribute value')
    return build_relative_endpoint(base_endpoint=base_endpoint, id_value=id_value)

def build_relative_endpoint(base_endpoint: str, id_value: str) -> str:
    return f'{base_endpoint}/{id_value}'