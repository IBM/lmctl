from .resource_api_base import ResourceAPIBase, ReadAPIMeta, APIArg, json_response_handler
from typing import List

class ProcessesAPI(ResourceAPIBase):
    endpoint = 'api/processes'

    enable_create_api = False
    enable_update_api = False
    enable_delete_api = False
    enable_list_api = False

    read_meta = ReadAPIMeta(extra_request_params={
        'shallow': APIArg()
    })

    def query(self, **query_params) -> List:
        response = self.base_client.make_request(method='GET', endpoint=self.endpoint, params=query_params)
        return json_response_handler(response)
