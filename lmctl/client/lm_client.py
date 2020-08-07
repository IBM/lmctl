from .exceptions import LmClientError, LmClientHttpError
from .apis.deployment_locations import DeploymentLocationApi
import requests

class LmClient:

    POST = 'post'
    GET = 'get'
    PUT = 'put'
    DELETE = 'delete'

    def __init__(self, address, auth=None):
        self.address = address
        self.auth = auth
        self._session = None

    def close(self):
        if self._session is not None:
            self._session.close()
    
    def _session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def make_request(self, method: str, url: str, **kwargs):
        try:
            response = self._session().request(method, url, **kwargs)
        except requests.RequestException as e:
            raise LmClient(str(e)) from e
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise LmClientHttpError(f'{method} request to {url} failed', e) from e
        return response

    @property
    def deployment_locations(self) -> DeploymentLocationApi:
        return DeploymentLocationApi(self)