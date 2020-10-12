import yaml
from typing import List, Dict
from lmctl.client.exceptions import LmClientError
from .resource_api_base import ResourceAPIBase, ListAPIMeta, ReadAPIMeta, CreateAPIMeta, UpdateAPIMeta

def accept_yaml_or_json_header_request_builder(*args, **kwargs):
    return {
        'headers': {
            'Accept': 'application/yaml,application/json'
        }
    }

def yaml_response_handler(response, *args, **kwargs):
    try:
        return yaml.safe_load(response.text)
    except yaml.YAMLError as e:
        raise LmClientError(f'Failed to parse response as YAML: {str(e)}') from e

def obj_yaml_request_builder(obj: Dict, *args, **kwargs) -> Dict:
    return {
        'data': yaml.safe_dump(obj),
        'headers': {
            'Content-Type': 'application/yaml'
        }
    }

class DescriptorsAPI(ResourceAPIBase):
    endpoint = 'api/catalog/descriptors'
    id_attr = 'name'
    list_meta = ListAPIMeta(request_builder=accept_yaml_or_json_header_request_builder, response_handler=yaml_response_handler)
    read_meta = ReadAPIMeta(request_builder=accept_yaml_or_json_header_request_builder, response_handler=yaml_response_handler)
    create_meta = CreateAPIMeta(request_builder=obj_yaml_request_builder, response_handler=None)
    update_meta = UpdateAPIMeta(request_builder=obj_yaml_request_builder)



    