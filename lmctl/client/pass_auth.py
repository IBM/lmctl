from typing import Dict
from .auth_type import AuthType

class UserPassAuth(AuthType):

    def __init__(self, username: str, password: str, client_id: str, client_secret: str):
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret

    def handle(self, client: 'TNCOClient') -> Dict:
        return client.auth.request_user_access(client_id=self.client_id, 
                                                client_secret=self.client_secret, 
                                                username=self.username, 
                                                password=self.password)

class LegacyUserPassAuth(AuthType):

    def __init__(self, username: str, password: str, legacy_auth_address: str = None):
        self.username = username
        self.password = password
        self.legacy_auth_address = legacy_auth_address

    def handle(self, client: 'TNCOClient') -> Dict:
        return client.auth.legacy_login(username=self.username, password=self.password, legacy_auth_address=self.legacy_auth_address)
