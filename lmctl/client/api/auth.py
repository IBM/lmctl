import base64
import logging
from requests.auth import HTTPBasicAuth
from typing import Dict
from .tnco_api_base import TNCOAPI
from lmctl.client.client_request import TNCOClientRequest
from lmctl.client.exceptions import TNCOClientError, TNCOClientHttpError

logger = logging.getLogger(__name__)

class AuthenticationAPI(TNCOAPI):
    oauth_endpoint = 'oauth/token'
    legacy_login_endpoint = 'ui/api/login'
    older_legacy_login_endpoint = 'api/login'

    def _build_client_basic_auth(self, client_id: str, client_secret: str) -> HTTPBasicAuth:
        return HTTPBasicAuth(client_id, client_secret)

    def request_client_access(self, client_id: str, client_secret: str) -> Dict:
        auth = self._build_client_basic_auth(client_id, client_secret)
        body = {
            'grant_type': 'client_credentials'
        }
        request = TNCOClientRequest(method='POST', endpoint=self.oauth_endpoint)\
                        .disable_auth_token()\
                        .add_form_data(body)\
                        .add_auth_handler(auth)
        auth_response = self.base_client.make_request_for_json(request)
        return auth_response

    def request_user_access(self, client_id: str, client_secret: str, username: str, password: str) -> Dict:
        auth = self._build_client_basic_auth(client_id, client_secret)
        body = {
            'username': username,
            'password': password,
            'grant_type': 'password'
        }
        request = TNCOClientRequest(method='POST', endpoint=self.oauth_endpoint)\
                        .disable_auth_token()\
                        .add_form_data(body)\
                        .add_auth_handler(auth)
        auth_response = self.base_client.make_request_for_json(request)
        return auth_response

    def legacy_login(self, username: str, password: str, legacy_auth_address: str = None) -> Dict:
        body = {
            'username': username,
            'password': password
        }
        try:
            request = TNCOClientRequest(method='POST', endpoint=self.legacy_login_endpoint)\
                        .disable_auth_token()\
                        .add_json_body(body)
            request.override_address = legacy_auth_address
            auth_response = self.base_client.make_request_for_json(request)
        except TNCOClientHttpError as e:
            if e.status_code == 404:
                logger.info(f'Failed to access login API at {self.legacy_login_endpoint}, responded with {e.status_code} status code...may be an older CP4NA orchestration environment, trying {self.older_legacy_login_endpoint}')
                request = TNCOClientRequest(method='POST', endpoint=self.older_legacy_login_endpoint)\
                        .disable_auth_token()\
                        .add_json_body(body)
                request.override_address = legacy_auth_address
                auth_response = self.base_client.make_request_for_json(request)
            else:
                raise
        return auth_response

    def request_zen_api_key_access(self, username: str, api_key: str, zen_auth_address: str = None) -> Dict:
        body = {
            'username': username,
            'api_key': api_key
        }
        request = TNCOClientRequest(method='POST', endpoint=None)\
                        .disable_auth_token()\
                        .add_json_body(body)
        request.override_address = zen_auth_address
        auth_response = self.base_client.make_request_for_json(request)
        return auth_response
