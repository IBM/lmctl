from .api import *
from typing import Dict
from urllib.parse import urlparse, urlencode
from .exceptions import TNCOClientError, TNCOClientHttpError
from .auth_type import AuthType
from .auth_tracker import AuthTracker
from .error_capture import tnco_error_capture
from .client_test_result import TestResult, TestResults
from .client_request import TNCOClientRequest
from lmctl.utils.trace_ctx import trace_ctx
import requests
import logging

logger = logging.getLogger(__name__)

class TNCOClient:
    """
    Base client for TNCO 

    TNCO APIs are grouped by functional attributes.
    """

    POST = 'post'
    GET = 'get'
    PUT = 'put'
    DELETE = 'delete'

    def __init__(self, address: str, auth_type: AuthType = None, kami_address: str = None, use_sessions: bool = False):
        self.address = self._parse_address(address)
        self.auth_type = auth_type
        self.kami_address = kami_address
        self.auth_tracker = AuthTracker() if self.auth_type is not None else None
        self._session = None
        self.use_sessions = use_sessions

    def _parse_address(self, address: str) -> str:
        if address is not None:
            while address.endswith('/'):
                address = address[:-1]
        return address

    def close(self):
        if self._session is not None:
            self._session.close()
    
    def _curr_session(self):
        if self.use_sessions:
            if self._session is None:
                self._session = requests.Session()
            return self._session
        else:
            return requests

    def get_access_token(self) -> str:
        if self.auth_tracker is not None:
            if self.auth_tracker.has_access_expired:
                auth_response = self.auth_type.handle(self)
                self.auth_tracker.accept_auth_response(auth_response)
            return self.auth_tracker.current_access_token
        else:
            return None

    def _add_auth_headers(self, headers: Dict) -> Dict:
        if self.auth_tracker is not None:
            access_token = self.get_access_token()
            headers['Authorization'] = f'Bearer {self.auth_tracker.current_access_token}'
        return headers

    def _supplement_headers(self, headers: Dict, inject_current_auth: bool = True) -> Dict:
        trace_ctx_headers = trace_ctx.to_http_header_dict()
        logger.debug(f'CP4NA orchestration request headers from trace ctx: {trace_ctx_headers}')
        headers.update(trace_ctx_headers)       
        if inject_current_auth:
            self._add_auth_headers(headers=headers)
        return headers

    def make_request(self, request: TNCOClientRequest) -> requests.Response:
        url = request.override_address if request.override_address else self.address
        if request.endpoint is not None:
            url = f'{url}/{request.endpoint}'
            
        request_kwargs = {}
        if request.query_params is not None and len(request.query_params) > 0:
            request_kwargs['params'] = request.query_params

        if request.body is not None:
            request_kwargs['data'] = request.body
        if request.files is not None and len(request.files) > 0:
            request_kwargs['files'] = request.files

        request_kwargs['headers'] = {}
        if request.headers is not None:
            request_kwargs['headers'].update(request.headers)

        # Log before adding sensitive data
        logger.debug(f'CP4NA orchestration request: Method={request.method}, URL={url}, Request Kwargs={request_kwargs}')

        if request.additional_auth_handler is not None:
            request_kwargs['auth'] = request.additional_auth_handler        
        self._supplement_headers(headers=request_kwargs['headers'], inject_current_auth=request.inject_current_auth) 

        try:
            response = self._curr_session().request(method=request.method, url=url, verify=False, **request_kwargs)
        except requests.RequestException as e:
            raise TNCOClientError(str(e)) from e
        logger.debug(f'CP4NA orchestration request has returned: Method={request.method}, URL={url}, Response={response}')
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise TNCOClientHttpError(f'{request.method} request to {url} failed', e) from e
        return response

    def make_request_for_json(self, request: TNCOClientRequest) -> Dict:
        response = self.make_request(request)
        try:
            return response.json()
        except ValueError as e:
            raise TNCOClientError(f'Failed to parse response to JSON: {str(e)}') from e

    def ping(self, include_template_engine: bool = False) -> Dict:
        with tnco_error_capture() as A:
            self.descriptors.all()
        with tnco_error_capture() as B:
            self.deployment_locations.all()
        with tnco_error_capture() as C:
            self.behaviour_projects.all()
        with tnco_error_capture() as D:
            self.shared_inf_keys.all()
        tests = []
        tests.append(TestResult(name='Descriptors', error=A.error))
        tests.append(TestResult(name='Topology', error=B.error))
        tests.append(TestResult(name='Behaviour', error=C.error))
        tests.append(TestResult(name='Resource Manager', error=D.error))
        if include_template_engine:
            with tnco_error_capture() as templates:
                self.descriptor_templates.all()
            tests.append(TestResult(name='Template Engine', error=templates.error))
        return TestResults(tests=tests)

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
    
