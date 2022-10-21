from typing import Dict
from .auth_type import AuthType

class ClientCredentialsAuth(AuthType):

    def __init__(self, client_id: str, client_secret: str, scope: str = None, okta_authserver: str = None, okta_server: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.okta_authserver = okta_authserver
        self.okta_server = okta_server

    def handle(self, client: 'TNCOClient') -> Dict:
        return client.auth.request_client_access(self.client_id, self.client_secret, self.scope, self.okta_authserver, self.okta_server)

    