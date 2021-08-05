import json
from pynetbox.core.query import RequestError, ContentError
from lmctl.client.exceptions import SitePlannerClientError

def make_call(self, pynb_endpoint, verb='get', params=None, data=None):
    if verb in ('post', 'put'):
        headers = {'Content-Type': 'application/json;'}
    else:
        headers = {'accept': 'application/json;'}
    if pynb_endpoint.token:
        headers['authorization'] = 'Token {}'.format(pynb_endpoint.token)
    if pynb_endpoint.session_key:
        headers['X-Session-Key'] = pynb_endpoint.session_key
    params = params or {}
    resp = getattr(pynb_endpoint.http_session, verb)(url_override or pynb_endpoint.url, headers=headers, params=params, json=data)
    return resp

def check_response(self, resp):
    if not resp.ok:
        raise SitePlannerClientError.with_pynb_error(RequestError(resp))

def check_response_and_get_json(self, resp): 
    try:
        return resp.json()
    except json.JSONDecodeError:
        raise SitePlannerClientError.with_pynb_error(ContentError(resp))