from .resource_api_base import ResourceAPIBase, ReadAPIMeta, APIArg

class ProcessesAPI(ResourceAPIBase):
    endpoint = 'api/processes'

    enable_create_api = False
    enable_update_api = False
    enable_delete_api = False
    enable_list_api = False

    read_meta = ReadAPIMeta(extra_request_params={
        'shallow': APIArg()
    })