import urllib
from typing import List, Dict
from .resource_api_base import ResourceAPIBase, json_response_handler

class AssembliesAPI(ResourceAPIBase):
    endpoint = 'api/topology/assemblies'

    # These operations must be performed via Intents
    enable_create_api = False
    enable_delete_api = False
    enable_update_api = False
    # Cannot be named "all" - replaced with "top_N"
    enable_list_api = False

    # "N" is determined by a config property on the target application
    def get_topN(self) -> List:
        response = self.base_client.make_request(method='GET', endpoint=self.endpoint)
        return json_response_handler(response)
    
    def all_with_name(self, name: str) -> List:
        params = {'name': name}
        endpoint = f'{self.endpoint}?{urllib.parse.urlencode(params)}'
        response = self.base_client.make_request(method='GET', endpoint=endpoint)
        return json_response_handler(response)

    def all_with_name_containing(self, search_string: str) -> List:
        params = {'nameContains': search_string}
        endpoint = f'{self.endpoint}?{urllib.parse.urlencode(params)}'
        response = self.base_client.make_request(method='GET', endpoint=endpoint)
        return json_response_handler(response)