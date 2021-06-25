import urllib
from typing import List, Dict, Union
from lmctl.client.exceptions import TNCOClientError
from lmctl.client.models import (CreateAssemblyIntent, UpgradeAssemblyIntent, ChangeAssemblyStateIntent, 
                                    DeleteAssemblyIntent, ScaleAssemblyIntent, HealAssemblyIntent,
                                    AdoptAssemblyIntent, CreateOrUpgradeAssemblyIntent, Intent)

from lmctl.client.client_request import TNCOClientRequest
from .tnco_api_base import TNCOAPI
from lmctl.client.utils import build_relative_endpoint, read_response_location_header

class AssembliesAPI(TNCOAPI):
    topology_endpoint = 'api/topology/assemblies'

    def get(self, id: str) -> Dict:
        return self._get_json(
            endpoint=build_relative_endpoint(base_endpoint=self.topology_endpoint, id_value=id)
        )

    def get_topN(self) -> List:
        return self._get_json(self.topology_endpoint)

    def get_by_name(self, name: str) -> Dict:
        result = self.all_with_name(name)
        if len(result) == 0:
            raise TNCOClientError(f'No Assembly found with name matching "{name}"')
        else:
            return result[0]

    def all_with_name(self, name: str) -> List:
        return self._get_json(self.topology_endpoint, query_params={'name': name})

    def all_with_name_containing(self, search_string: str) -> List:
        return self._get_json(self.topology_endpoint, query_params={'nameContains': search_string})

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

    def intent_create_or_upgrade(self, intent_obj: Union[Dict, CreateOrUpgradeAssemblyIntent]) -> str:
        return self._intent_request_impl('createOrUpgradeAssembly', intent_obj)

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

    def intent_endpoint(self, intent_name: str) -> str:
        return f'api/intent/{intent_name}'

    def _intent_request_impl(self, intent_name: str, intent_obj: Union[Dict, 
                                                                        AdoptAssemblyIntent,
                                                                        CreateAssemblyIntent, 
                                                                        ChangeAssemblyStateIntent, 
                                                                        DeleteAssemblyIntent, 
                                                                        HealAssemblyIntent, 
                                                                        ScaleAssemblyIntent,
                                                                        UpgradeAssemblyIntent]) -> str:
        endpoint = self.intent_endpoint(intent_name)
        if isinstance(intent_obj, Intent):
            intent_obj_data = intent_obj.to_dict()
        else:
            intent_obj_data = intent_obj
        request = TNCOClientRequest(method='POST', endpoint=endpoint).add_json_body(intent_obj_data)
        return self._exec_request_and_get_location_header(request)