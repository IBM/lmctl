from .api import *
from typing import Dict
from .exceptions import LmClientError, LmClientHttpError
from .auth_type import AuthType
from .auth_tracker import AuthTracker
from urllib.parse import urlparse
import requests
import logging

logger = logging.getLogger(__name__)

class LmClient:

    POST = 'post'
    GET = 'get'
    PUT = 'put'
    DELETE = 'delete'

    def __init__(self, address: str, auth_type: AuthType = None, kami_address: str = None):
        self.address = address
        self.auth_type = auth_type
        self.kami_address = kami_address
        self.auth_tracker = AuthTracker() if self.auth_type is not None else None
        self._session = None

    def close(self):
        if self._session is not None:
            self._session.close()
    
    def _curr_session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
        return self._session

    def _add_auth_headers(self, headers: Dict=None) -> Dict:
        if headers is None:
            headers = {}
        if self.auth_tracker is not None:
            if self.auth_tracker.has_access_expired:
                auth_response = self.auth_type.handle(self)
                self.auth_tracker.accept_auth_response(auth_response)
            headers['Authorization'] = f'Bearer {self.auth_tracker.current_access_token}'
        return headers
    
    def make_request(self, method: str, endpoint: str, include_auth: bool = True, override_address: str = None, **kwargs) -> requests.Response:
        address = override_address or self.address
        url = f'{address}/{endpoint}'
        logger.debug(f'LM request: Method={method}, URL={url}, kwargs={kwargs}')
        headers = kwargs.pop('headers', {})
        if include_auth:
            headers = self._add_auth_headers(headers=headers)
        try:
            response = self._curr_session().request(method, url, headers=headers, verify=False, **kwargs)
        except requests.RequestException as e:
            raise LmClientError(str(e)) from e
        logger.debug(f'LM request has returned: Method={method}, URL={url}, Response={response}')
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise LmClientHttpError(f'{method} request to {url} failed', e) from e
        return response

    def make_request_for_json(self, method: str, endpoint: str, include_auth: bool = True, override_address: str = None, **kwargs) -> Dict:
        response = self.make_request(method, endpoint, include_auth=include_auth, override_address=override_address, **kwargs)
        try:
            return response.json()
        except ValueError as e:
            raise LmClientError(f'Failed to parse response to JSON: {str(e)}') from e

    @property
    def auth(self) -> AuthenticationAPI:
        return AuthenticationAPI(self)

    @property
    def assemblies(self) -> AssembliesAPI:
        return AssembliesAPI(self)

    @property
    def behaviour_assembly_confs(self) -> BehaviourAssemblyConfigurationsAPI:
        return BehaviourAssemblyConfigurationsAPI(self)

    @property
    def behaviour_projects(self) -> BehaviourProjectsAPI:
        return BehaviourProjectsAPI(self)

    @property
    def behaviour_scenarios(self) -> BehaviourScenariosAPI:
        return BehaviourScenariosAPI(self)

    @property
    def behaviour_scenario_execs(self) -> BehaviourScenarioExecutionsAPI:
        return BehaviourScenarioExecutionsAPI(self)

    @property
    def deployment_locations(self) -> DeploymentLocationAPI:
        return DeploymentLocationAPI(self)

    @property
    def descriptors(self) -> DescriptorsAPI:
        return DescriptorsAPI(self)

    @property
    def descriptor_templates(self) -> DescriptorTemplatesAPI:
        return DescriptorTemplatesAPI(self)
    
    @property
    def lifecycle_drivers(self) -> LifecycleDriversAPI:
        return LifecycleDriversAPI(self)

    @property
    def processes(self) -> ProcessesAPI:
        return ProcessesAPI(self)
    
    @property
    def resource_drivers(self) -> ResourceDriversAPI:
        return ResourceDriversAPI(self)
    
    @property
    def resource_packages(self) -> ResourcePackagesAPI:
        return ResourcePackagesAPI(self)
    
    @property
    def resource_managers(self) -> ResourceManagersAPI:
        return ResourceManagersAPI(self)
    
    @property
    def shared_inf_keys(self) -> SharedInfrastructureKeysAPI:
        return SharedInfrastructureKeysAPI(self)
    
    @property
    def vim_drivers(self) -> VIMDriversAPI:
        return VIMDriversAPI(self)
    