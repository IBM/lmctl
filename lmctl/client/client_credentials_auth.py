from typing import Dict
from .auth_type import AuthType

class ClientCredentialsAuth(AuthType):

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        
    def handle(self, client: 'TNCOClient') -> Dict:
        return client.auth.request_client_access(self.client_id, self.client_secret)

    