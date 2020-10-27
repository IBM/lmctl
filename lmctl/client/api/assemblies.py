import urllib
from typing import List, Dict, Union
from lmctl.client.exceptions import LmClientError
from .resource_api_base import ResourceAPIBase, json_response_handler, obj_json_request_builder, location_id_response_handler
from lmctl.client.models import (CreateAssemblyIntent, UpgradeAssemblyIntent, ChangeAssemblyStateIntent, 
                                    DeleteAssemblyIntent, ScaleAssemblyIntent, HealAssemblyIntent,
                                    AdoptAssemblyIntent, Intent)

class AssembliesAPI(ResourceAPIBase):
    endpoint = 'api/topology/assemblies'

    # These operations must be performed via Intents so disable the bootstrap methods from ResourceAPIBase
    enable_create_api = False
    enable_delete_api = False
    enable_update_api = False
    # Cannot be named "all" - replaced with "get_topN"
    enable_list_api = False

    # "N" is determined by a config property on the target application
    def get_topN(self) -> List:
        response = self.base_client.make_request(method='GET', endpoint=self.endpoint)
        return json_response_handler(response)

    def get_by_name(self, name: str) -> Dict:
        result = self.all_with_name(name)
        if len(result) == 0:
            raise LmClientError('No Assembly found with name matching "{name}"')
        else:
            return result[0]

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

    def intent(self, intent_name: str, intent_obj: Union[Dict, 
                                                        AdoptAssemblyIntent,
                                                        CreateAssemblyIntent, 
                                                        ChangeAssemblyStateIntent, 
                                                        DeleteAssemblyIntent, 
                                                        HealAssemblyIntent, 
                                                        ScaleAssemblyIntent,
                                                        UpgradeAssemblyIntent]) -> str:
        return self._intent_request_impl(intent_name, intent_obj)

    def intent_create(self, intent_obj: Union[Dict, CreateAssemblyIntent]) -> str:
        return self._intent_request_impl('createAssembly', intent_obj)

    def intent_upgrade(self, intent_obj: Union[Dict, UpgradeAssemblyIntent]) -> str:
        return self._intent_request_impl('upgradeAssembly', intent_obj)

    def intent_delete(self, intent_obj: Union[Dict, DeleteAssemblyIntent]) -> str:
        return self._intent_request_impl('deleteAssembly', intent_obj)

    def intent_change_state(self, intent_obj: Union[Dict, ChangeAssemblyStateIntent]) -> str:
        return self._intent_request_impl('changeAssemblyState', intent_obj)

    def intent_scale_out(self, intent_obj: Union[Dict, ScaleAssemblyIntent]) -> str:
        return self._intent_request_impl('scaleOutAssembly', intent_obj)

    def intent_scale_in(self, intent_obj: Union[Dict, ScaleAssemblyIntent]) -> str:
        return self._intent_request_impl('scaleInAssembly', intent_obj)

    def intent_heal(self, intent_obj: Union[Dict, HealAssemblyIntent]) -> str:
        return self._intent_request_impl('healAssembly', intent_obj)

    def intent_adopt(self, intent_obj: Union[Dict, AdoptAssemblyIntent]) -> str:
        return self._intent_request_impl('adoptAssembly', intent_obj)   

    def _intent_endpoint(self, intent_name: str) -> str:
        return f'api/intent/{intent_name}'

    def _intent_request_impl(self, intent_name: str, intent_obj: Union[Dict, 
                                                                        AdoptAssemblyIntent,
                                                                        CreateAssemblyIntent, 
                                                                        ChangeAssemblyStateIntent, 
                                                                        DeleteAssemblyIntent, 
                                                                        HealAssemblyIntent, 
                                                                        ScaleAssemblyIntent,
                                                                        UpgradeAssemblyIntent]) -> str:
        endpoint = self._intent_endpoint(intent_name)
        if isinstance(intent_obj, Intent):
            intent_obj_data = intent_obj.to_dict()
        else:
            intent_obj_data = intent_obj
        request = obj_json_request_builder(intent_obj_data)
        request['endpoint'] = endpoint
        request['method'] = 'POST'
        response = self.base_client.make_request(**request)
        return location_id_response_handler(response)
