from typing import Dict
from .exceptions import LmClientError, LmClientHttpError
from .apis import AuthenticationAPI, DeploymentLocationAPI
from .auth_type import AuthType
from .auth_tracker import AuthTracker
import requests
import logging

logger = logging.getLogger(__name__)

class LmClient:

    POST = 'post'
    GET = 'get'
    PUT = 'put'
    DELETE = 'delete'

    def __init__(self, address: str, auth: AuthType=None):
        self.address = address
        self.auth = auth
        self.auth_tracker = AuthTracker() if self.auth is not None else None
        self._session = None

    def close(self):
        if self._session is not None:
            self._session.close()
    
    def _session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def _add_auth_headers(self, headers: Dict=None) -> Dict:
        if headers is None:
            headers = {}
        if self.auth_tracker is not None:
            if self.auth_tracker.has_access_expired:
                auth_response = self.auth.handle(self)
                self.auth_tracker.accept_auth_response(auth_response)
            headers['Authorization'] = f'Bearer {self.auth_tracker.current_access_token}'
        return headers
    
    def make_request(self, method: str, url: str, include_auth: bool=True, **kwargs) -> requests.Response:
        logger.debug(f'LM request: Method={method}, URL={url}, kwargs={kwargs}')
        if include_auth:
            headers = self._add_auth_headers(headers=kwargs.pop('headers', None))
        try:
            response = self._session().request(method, url, headers=headers, **kwargs)
        except requests.RequestException as e:
            raise LmClientError(str(e)) from e
        logger.debug(f'LM request has returned: Method={method}, URL={url}, Response={response}')
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise LmClientHttpError(f'{method} request to {url} failed', e) from e
        return response

    def make_request_for_json(self, method: str, url: str, no_auth: bool=False, **kwargs) -> Dict:
        response = self.make_request(method, url, **kwargs)
        try:
            return response.json()
        except ValueError as e:
            raise LmClientError(f'Failed to parse response to JSON: {str(e)}') from e

    @property
    def auth(self) -> AuthenticationAPI:
        return AuthenticationAPI(self)

    @property
    def deployment_locations(self) -> DeploymentLocationAPI:
        return DeploymentLocationAPI(self)