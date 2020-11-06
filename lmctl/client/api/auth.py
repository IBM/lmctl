import base64
import logging
from requests.auth import HTTPBasicAuth
from typing import Dict
from .api_base import APIBase
from lmctl.client.exceptions import TNCOClientError, TNCOClientHttpError

logger = logging.getLogger(__name__)

class AuthenticationAPI(APIBase):
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
        auth_response = self.base_client.make_request_for_json(method='POST', endpoint=self.oauth_endpoint, auth=auth, include_auth=False, data=body)
        return auth_response

    def request_user_access(self, client_id: str, client_secret: str, username: str, password: str) -> Dict:
        auth = self._build_client_basic_auth(client_id, client_secret)
        body = {
            'username': username,
            'password': password,
            'grant_type': 'password'
        }
        auth_response = self.base_client.make_request_for_json(method='POST', endpoint=self.oauth_endpoint, auth=auth, include_auth=False, data=body)
        return auth_response

    def legacy_login(self, username: str, password: str, legacy_auth_address: str = None) -> Dict:
        body = {
            'username': username,
            'password': password
        }
        try:
            auth_response = self.base_client.make_request_for_json(method='POST', 
                                                                    endpoint=self.legacy_login_endpoint, 
                                                                    include_auth=False, 
                                                                    override_address=legacy_auth_address, 
                                                                    json=body)
        except TNCOClientHttpError as e:
            if e.status_code == 404:
                logger.info(f'Failed to access login API at {self.legacy_login_endpoint}, responded with {e.status_code} status code...may be an older LM environment, trying {self.older_legacy_login_endpoint}')
                auth_response = self.base_client.make_request_for_json(method='POST', 
                                                                        endpoint=self.older_legacy_login_endpoint, 
                                                                        include_auth=False, 
                                                                        override_address=legacy_auth_address, 
                                                                        json=body)
            else:
                raise
        return auth_response
