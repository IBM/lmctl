from typing import Dict
from .auth_type import AuthType

class OktaClientCredentialsAuth(AuthType):

    def __init__(self, client_id: str, client_secret: str, scope: str = None, auth_server_id: str = None, okta_server: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.auth_server_id = auth_server_id
        self.okta_server = okta_server

    def handle(self, client: 'TNCOClient') -> Dict:
        return client.auth.request_okta_client_access(self.client_id, self.client_secret, self.scope, self.auth_server_id, self.okta_server)


class OktaUserPassAuth(AuthType):

    def __init__(self, username: str, password: str, client_id: str, client_secret: str, scope: str = None, auth_server_id: str = None, okta_server: str = None):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.auth_server_id = auth_server_id
        self.okta_server = okta_server

    def handle(self, client: 'TNCOClient') -> Dict:
        return client.auth.request_okta_user_access(client_id=self.client_id,
                                                client_secret=self.client_secret,
                                                username=self.username,
                                                password=self.password, scope=self.scope,
                                                auth_server_id= self.auth_server_id,
                                                okta_server=self.okta_server)