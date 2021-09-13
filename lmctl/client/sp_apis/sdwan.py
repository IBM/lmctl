import logging
from typing import Dict
from .sp_api_base import SitePlannerAPIGroup, SitePlannerCrudAPI
from lmctl.client.utils import read_response_location_header
from lmctl.client.exceptions import SitePlannerClientError

logger = logging.getLogger(__name__)

class TemplateTypesAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'plugins.sdwan.templatetypes'

    def get_by_name(self, name: str) -> Dict:
        override_url = self._pynb_endpoint.url + f'/?name={name}'
        resp = self._make_direct_http_call(
            verb='get',
            override_url=override_url,
        ).json()
        count = resp.get('count', 0)
        if count == 0:
            return None
        if count > 1:
            raise SitePlannerClientError(f'Too many matches on name: {name}')
        results = resp.get('results', None)
        if results is None:
            return None
        obj = results[0]
        return self._record_to_dict(obj)

    def get_by_cloud_account_type(self, cloud_account_type_id: str) -> Dict:
        override_url = self._pynb_endpoint.url + f'/?cloud_account_type={cloud_account_type_id}'
        resp = self._make_direct_http_call(
            verb='get',
            override_url=override_url,
        ).json()
        results = resp.get('results', None)
        if results is None:
            return []
        return [self._record_to_dict(obj) for obj in results]


class SDWANGroup(SitePlannerAPIGroup):

    @property
    def template_types(self):
        return TemplateTypesAPI(self._sp_client)    
