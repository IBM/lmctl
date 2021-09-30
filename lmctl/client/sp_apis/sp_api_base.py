import copy
from lmctl.client.client_request import TNCOClientRequest
import pynetbox
import requests
from pynetbox.core.query import Request, RequestError, AllocationError, ContentError
from typing import Dict, List, Union
from lmctl.client.exceptions import SitePlannerClientError

class SitePlannerAPIGroup:

    def __init__(self, sp_client):
        self._sp_client = sp_client

#TODO secrets API


class SitePlannerAPI:
    _pk_field = 'id'
    _endpoint_chain = ''
    _relation_fields = []
    _ignore_fields_on_update = []

    def __init__(self, sp_client):
        self._sp_client = sp_client
        self._pynb_endpoint = self._get_endpoint()

    def _get_endpoint(self):
        chain = self._endpoint_chain.split('.')
        current = self._sp_client.pynb_api
        while len(chain) > 0:
            current = getattr(current, chain.pop(0))
        return current

    def _record_to_dict(self, record):
        return dict(record)

    def _make_direct_http_call(self, verb='get', override_url=None, params=None, data=None):
        if verb in ('post', 'put'):
            headers = {'Content-Type': 'application/json;'}
        else:
            headers = {'accept': 'application/json;'}
        if self._pynb_endpoint.token:
            headers['authorization'] = 'Token {}'.format(self._pynb_endpoint.token)
        if self._pynb_endpoint.session_key:
            headers['X-Session-Key'] = self._pynb_endpoint.session_key
        params = params or {}
        resp = getattr(self._pynb_endpoint.api.http_session, verb)(override_url or self._pynb_endpoint.url, headers=headers, params=params, json=data)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise SitePlannerClientError(f'{resp.request.method} request to {resp.request.url} failed', e) from e
        return resp

    def _make_pynb_call(self, method_name: str, *args, **kwargs):
        try:
            return getattr(self._pynb_endpoint, method_name)(*args, **kwargs)
        except (RequestError, ContentError, AllocationError) as e:
            raise SitePlannerClientError(f'{e.req.request.method} request to {e.req.request.url} failed', e) from e

    def _sanitize_update(self, obj: Dict):
        new_obj = copy.deepcopy(obj)
        for k,v in obj.items():
            if k in self._ignore_fields_on_update:
                del new_obj[k]
            elif k in self._relation_fields and v is not None and isinstance(v, dict):
                # When post/put-ing relatonships we need to send the ID only
                new_obj[k] = v.get('id') if 'id' in v else v
            elif k in self._relation_fields and v is not None and isinstance(v, list):
                # When post/put-ing relatonships we need to send the ID only
                new_obj[k] = [el.get('id') if 'id' in el else el for el in v]
            elif isinstance(v, dict) and 'value' in v.keys() and 'label' in v.keys():
                # When post/put-ing choice fields we need to send the value only
                new_obj[k] = v.get('value')
        return new_obj

    def _get_json(self, endpoint: str, query_params: Dict[str,str] = None):
        request = TNCOClientRequest.build_request_for_json(endpoint=endpoint)
        if query_params is not None:
            request.query_params.update(query_params)
        return self._exec_request_and_parse_json(request)

class SitePlannerCreateMixin:
    def create(self, obj: Dict) -> Dict:
        record = self._make_pynb_call('create', obj)
        return self._record_to_dict(record)

class SitePlannerUpdateMixin:
     
    def update(self, obj: Dict):
        pk = obj.get(self._pk_field, None)
        if pk is None:
            raise SitePlannerClientError(f'Cannot update object missing "{self._pk_field}" attribute value')
        update_data = self._sanitize_update(obj)
        self._put_update(pk, update_data)

    def _put_update(self, pk: Union[str, int], obj: Dict):
        self._make_direct_http_call(
            verb='put', 
            override_url=self._pynb_endpoint.url + '/' + str(pk) + '/',
            data=obj
        )

class SitePlannerGetMixin:
    
    def get(self, id: str) -> Dict:
        obj = self._make_pynb_call('get', id)
        if obj is None:
            # 404
            raise SitePlannerClientError(f'Could not find object with {self._pk_field}: {id}')
        return self._record_to_dict(obj)

class SitePlannerDeleteMixin:
 
    def delete(self, id: str):
        existing_obj = self._make_pynb_call('get', id)
        if existing_obj is None:
            # 404
            raise SitePlannerClientError(f'Could not find object with {self._pk_field}: {id}')
        existing_obj.delete()

class SitePlannerListMixin:

    def all(self, limit: int = 0, **filters) -> List:
        if len(filters) == 0:
            result_set = self._make_pynb_call('all', limit=limit)
        else:
            result_set = self._make_pynb_call('filter', limit=limit, **filters)
        return [self._record_to_dict(r) for r in result_set]

class SitePlannerCrudAPI(SitePlannerAPI, SitePlannerCreateMixin, SitePlannerDeleteMixin, SitePlannerGetMixin, SitePlannerListMixin, SitePlannerUpdateMixin):
    pass
