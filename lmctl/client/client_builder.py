from .client_credentials_auth import ClientCredentialsAuth
from .pass_auth import UserPassAuth, LegacyUserPassAuth
from .zen_auth import ZenAPIKeyAuth
from .token_auth import JwtTokenAuth
from .client import TNCOClient
from .auth_type import AuthType

class TNCOClientBuilder:

    def __init__(self):
        self._address = None
        self._kami_address = None
        self._auth = None
    
    @property
    def address(self):
        return self._address

    def address(self, address: str) -> 'TNCOClientBuilder':
        self._address = address
        return self
    
    @property
    def kami_address(self):
        return self._kami_address

    def kami_address(self, kami_address: str) -> 'TNCOClientBuilder':
        self._kami_address = kami_address
        return self
    
    @property
    def auth(self):
        return self._auth

    def auth(self, auth: AuthType) -> 'TNCOClientBuilder':
        self._auth = auth
        return self
        
    def zen_api_key_auth(self, username: str, api_key: str, zen_auth_address: str = None) -> 'TNCOClientBuilder':
        self._auth = ZenAPIKeyAuth(username=username, api_key=api_key, zen_auth_address=zen_auth_address)
        return self

    def token_auth(self, token: str) -> 'TNCOClientBuilder':
        self._auth = JwtTokenAuth(token=token)
        return self

    def client_credentials_auth(self, client_id: str, client_secret: str) -> 'TNCOClientBuilder':
        self._auth = ClientCredentialsAuth(client_id=client_id, client_secret=client_secret)
        return self
    
    def user_pass_auth(self, username: str, password: str, client_id: str, client_secret: str) -> 'TNCOClientBuilder':
        self._auth = UserPassAuth(username=username, password=password, client_id=client_id, client_secret=client_secret)
        return self
    
    def legacy_user_pass_auth(self, username: str, password: str, legacy_auth_address: str = None) -> 'TNCOClientBuilder':
        self._auth = LegacyUserPassAuth(username=username, password=password, legacy_auth_address=legacy_auth_address)
        return self
    
    def build(self):
        return TNCOClient(self._address, auth_type=self._auth, kami_address=self._kami_address)
