from typing import List, Dict
from .resource_api_base import ResourceAPIBase, ReadAPIMeta, APIArg, ListAPIMeta

class SharedInfrastructureKeysAPI(ResourceAPIBase):
    endpoint = 'api/resource-manager/infrastructure-keys/shared'
    id_attr = 'name'

    read_meta = ReadAPIMeta(extra_request_params={
        'include_private_key': APIArg(param_name='includePrivateKey')
    })

    list_meta = ListAPIMeta(extra_request_params={
        'include_private_key': APIArg(param_name='includePrivateKey')
    })