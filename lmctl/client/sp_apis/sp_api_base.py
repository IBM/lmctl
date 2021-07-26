import copy
import pynetbox
from pynetbox.core.query import Request
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

    def all(self, limit: int = 0, **filters) -> List:
        if len(filters) == 0:
            result_set = self._pynb_endpoint.all(limit=limit)
        else:
            result_set = self._pynb_endpoint.filter(limit=limit, **filters)
        return [self._record_to_dict(r) for r in result_set]

    def get(self, id: str) -> Dict:
        obj = self._pynb_endpoint.get(id)
        if obj is None:
            # 404
            raise SitePlannerClientError(f'Could not find object with {self._pk_field}: {id}')
        return self._record_to_dict(obj)

    def create(self, obj: Dict) -> Dict:
        record = self._pynb_endpoint.create(obj)
        return self._record_to_dict(record)

    def update(self, obj: Dict):
        pk = obj.get(self._pk_field, None)
        if pk is None:
            raise SitePlannerClientError(f'Cannot update object missing "{self._pk_field}" attribute value')
        update_data = self._sanitize_update(obj)
        self._put_update(pk, update_data)

    def _put_update(self, pk: Union[str, int], obj: Dict):
        req = Request(
            base=self._pynb_endpoint.url + '/' + str(pk),
            token=self._pynb_endpoint.token,
            session_key=self._pynb_endpoint.session_key,
            http_session=self._pynb_endpoint.api.http_session,
        ).put(obj)

    def delete(self, id: str):
        existing_obj = self._pynb_endpoint.get(id)
        if existing_obj is None:
            # 404
            raise SitePlannerClientError(f'Could not find object with {self._pk_field}: {id}')
        existing_obj.delete()

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


