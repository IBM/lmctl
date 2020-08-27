import base64
from typing import Dict
from lmctl.client.exceptions import LmClientError, LmClientHttpError

class AuthenticationAPI:

    def __init__(self, base_client: 'LmClient'):
        self.base_client = base_client
        self.login_endpoint = f'{self.base_client.address}/ui/api/login'
        self.old_login_endpoint = f'{self.base_client.address}/api/login'
        self.oauth_endpoint = f'{self.base_client.address}/oauth/token'
    
    def _encoded_client_headers(self, client_id: str, client_secret: str) -> Dict:
        encoded_client = base64.b64encode(f'{client_id}:{client_secret}')
        return f'Basic {encoded_client}'

    def request_client_access(self, client_id: str, client_secret: str) -> Dict:
        headers = {
            'Authorization': self._encoded_client_headers(client_id, client_secret)
        }
        body = {
            'grant_type': 'client_credentials'
        }
        auth_response = self.base_client.make_request_for_json('POST', self.oauth_endpoint, headers=headers, include_auth=False, json=body)
        return auth_response

    def request_user_access(self, client_id: str, client_secret: str, username: str, password: str) -> Dict:
        headers = {
            'Authorization': self._encoded_client_headers(client_id, client_secret)
        }
        body = {
            'username': username,
            'password': password,
            'grant_type': 'password'
        }
        auth_response = self.base_client.make_request_for_json('POST', self.oauth_endpoint, headers=headers, include_auth=False, json=body)
        return auth_response

    def legacy_login(self, username: str, password: str) -> Dict:
        body = {
            'username': username,
            'password': password
        }
        try:
            auth_response = self.base_client.make_request_for_json('POST', self.login_endpoint, headers=headers, include_auth=False, json=body)
        except LmClientHttpError as e:
            if e.status_code == 404:
                logger.info(f'Failed to access login API at {self.login_endpoint}, responded with {e.status_code} status code...may be an older LM environment, trying {self.old_login_endpoint}')
                auth_response = self.base_client.make_request_for_json('POST', self.old_login_endpoint, headers=headers, include_auth=False, json=body)
            else:
                raise
        return auth_response