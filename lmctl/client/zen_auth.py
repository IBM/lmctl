from typing import Dict
from .auth_type import AuthType

class ZenAPIKeyAuth(AuthType):

    def __init__(self, username: str, api_key: str, zen_auth_address: str = None):
        self.username = username
        self.api_key = api_key
        self.zen_auth_address = zen_auth_address

    def handle(self, client: 'TNCOClient') -> Dict:
        return client.auth.request_zen_api_key_access(username=self.username, api_key=self.api_key, zen_auth_address=self.zen_auth_address)
