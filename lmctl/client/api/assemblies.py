import urllib
from typing import List, Dict, Union
from lmctl.client.exceptions import TNCOClientError
from lmctl.client.models import (CreateAssemblyIntent, UpgradeAssemblyIntent, ChangeAssemblyStateIntent, 
                                    DeleteAssemblyIntent, ScaleAssemblyIntent, HealAssemblyIntent,
                                    AdoptAssemblyIntent, CreateOrUpgradeAssemblyIntent,
                                    RollbackAssemblyIntent, CancelAssemblyIntent, RetryAssemblyIntent, Intent)

from lmctl.client.client_request import TNCOClientRequest
from .tnco_api_base import TNCOAPI
from lmctl.client.utils import build_relative_endpoint

INTENTS_WITHOUT_LOCATION_HEADER = ["retry", "rollback", "cancel"]

class AssembliesAPI(TNCOAPI):
    topology_endpoint = 'api/topology/assemblies'

    def get(self, id: str) -> Dict:
        return self._get_json(
            endpoint=build_relative_endpoint(base_endpoint=self.topology_endpoint, id_value=id)
        )

    def get_topN(self, object_group_id: str = None) -> List:
        return self._get_json(self.topology_endpoint, object_group_id=object_group_id)

    def get_by_name(self, name: str) -> Dict:
        result = self.all_with_name(name)
        if len(result) == 0:
            raise TNCOClientError(f'No Assembly found with name matching "{name}"')
        else:
            return result[0]

    def all_with_name(self, name: str, object_group_id: str = None) -> List:
        return self._get_json(self.topology_endpoint, query_params={'name': name}, object_group_id=object_group_id)

    def all_with_name_containing(self, search_string: str, object_group_id: str = None) -> List:
        return self._get_json(self.topology_endpoint, query_params={'nameContains': search_string}, object_group_id=object_group_id)

    def intent(self, intent_name: str, intent_obj: Union[Dict, 
                                                        AdoptAssemblyIntent,
                                                        CreateAssemblyIntent, 
                                                        ChangeAssemblyStateIntent, 
                                                        DeleteAssemblyIntent, 
                                                        HealAssemblyIntent, 
                                                        ScaleAssemblyIntent,
                                                        UpgradeAssemblyIntent,
                                                        RetryAssemblyIntent,
                                                        CancelAssemblyIntent,
                                                        RollbackAssemblyIntent], 
                     object_group_id: str = None) -> str:
        return self._intent_request_impl(intent_name, intent_obj, object_group_id=object_group_id)

    def intent_create(self, intent_obj: Union[Dict, CreateAssemblyIntent], object_group_id: str = None) -> str:
        return self._intent_request_impl('createAssembly', intent_obj, object_group_id=object_group_id)

    def intent_upgrade(self, intent_obj: Union[Dict, UpgradeAssemblyIntent]) -> str:
        return self._intent_request_impl('upgradeAssembly', intent_obj)

    def intent_create_or_upgrade(self, intent_obj: Union[Dict, CreateOrUpgradeAssemblyIntent], object_group_id: str = None) -> str:
        return self._intent_request_impl('createOrUpgradeAssembly', intent_obj, object_group_id=object_group_id)

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

    def intent_retry(self, intent_obj: Union[Dict, RetryAssemblyIntent]) -> str:
        return self._intent_request_impl('retry', intent_obj)

    def intent_rollback(self, intent_obj: Union[Dict, RollbackAssemblyIntent]) -> str:
        return self._intent_request_impl('rollback', intent_obj)

    def intent_cancel(self, intent_obj: Union[Dict, CancelAssemblyIntent]) -> str:
        return self._intent_request_impl('cancel', intent_obj)

    def intent_adopt(self, intent_obj: Union[Dict, AdoptAssemblyIntent], object_group_id: str = None) -> str:
        return self._intent_request_impl('adoptAssembly', intent_obj, object_group_id=object_group_id)   

    def intent_endpoint(self, intent_name: str) -> str:
        return f'api/intent/{intent_name}'

    def _intent_request_impl(self, intent_name: str, intent_obj: Union[Dict, 
                                                                        AdoptAssemblyIntent,
                                                                        CreateAssemblyIntent, 
                                                                        ChangeAssemblyStateIntent, 
                                                                        DeleteAssemblyIntent, 
                                                                        HealAssemblyIntent, 
                                                                        ScaleAssemblyIntent,
                                                                        UpgradeAssemblyIntent],
                                   object_group_id: str = None) -> str:
        endpoint = self.intent_endpoint(intent_name)
        if isinstance(intent_obj, Intent):
            intent_obj_data = intent_obj.to_dict()
        else:
            intent_obj_data = intent_obj
        request = TNCOClientRequest(method='POST', endpoint=endpoint).add_json_body(intent_obj_data)
        if object_group_id is not None:
            request.add_object_group_id_body(object_group_id)
            
        if intent_name in INTENTS_WITHOUT_LOCATION_HEADER:
            return self._exec_request(request)
        return self._exec_request_and_get_location_header(request)