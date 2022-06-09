import pynetbox
from typing import Optional
from pydantic.dataclasses import dataclass
from requests import Session, Request, PreparedRequest

@dataclass
class SitePlannerOverrides:
    address: Optional[str] = None
    api_token: Optional[str] = None
    use_auth: Optional[bool] = True

class SitePlannerClient:

    _patched = False
    
    def __init__(self, address: str, api_token: str = None, parent_client: 'TNCOClient' = None, use_auth: bool = True, inject_sp_path: bool = False):
        self.address = self._parse_address(address)
        self.api_token = api_token
        self.parent_client = parent_client
        self.use_auth = use_auth
        self.inject_sp_path = inject_sp_path
        self.pynb_api = self._construct_pynetbox()

        # Proxy Apps exposed by pynetbox
        self.dcim = self.pynb_api.dcim
        self.ipam = self.pynb_api.ipam
        self.circuits = self.pynb_api.circuits
        self.secrets = self.pynb_api.secrets
        self.tenancy = self.pynb_api.tenancy
        self.extras = self.pynb_api.extras
        self.virtualization = self.pynb_api.virtualization
        self.users = self.pynb_api.users
        self.wireless = self.pynb_api.wireless
        self.plugins = self.pynb_api.plugins

        self.openapi = self.pynb_api.openapi
        self.status = self.pynb_api.status
        self.create_token = self.pynb_api.create_token

    @property
    def version(self):
        return self.version

    def _construct_pynetbox(self):
        pynb_api = pynetbox.api(self.address, token=self.api_token if self.use_auth else None)
        pynb_api.http_session = SitePlannerSessionProxy(self.parent_client, inject_sp_path=self.inject_sp_path)

        if self.use_auth and self.api_token is None:
            # Could be using Zen/Oauth 
            if self.parent_client is not None:
                # Using Zen/Oauth from CP4NA (TNCO)
                # Intercept calls made by pynetbox to add auth headers
                pynb_api.http_session.inject_auth_headers = True

        pynb_api.http_session.verify = False
        return pynb_api

    def _parse_address(self, address: str) -> str:
        if address is not None:
            while address.endswith('/'):
                address = address[:-1]
        return address

class SitePlannerSessionProxy(Session):
    
    def __init__(self, tnco_client: 'TNCOClient', *args, inject_auth_headers: bool = False, inject_sp_path: bool = False,**kwargs):
        super().__init__(*args, **kwargs)
        self.tnco_client = tnco_client
        self.inject_auth_headers = inject_auth_headers
        self.inject_sp_path = inject_sp_path

    def prepare_request(self, request: Request) -> PreparedRequest:
        # Intercept the request to add auth headers
        if self.inject_auth_headers:
            self.tnco_client.supplement_headers(request.headers)
        if self.inject_sp_path:
            request.url = request.url.replace('/api/', '/api/site-planner/')
        return super().prepare_request(request)