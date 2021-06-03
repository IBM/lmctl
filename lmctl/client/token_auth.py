from typing import Dict
from .auth_type import AuthType

class JwtTokenAuth(AuthType):

    def __init__(self, token: str = None):
        self.token = token

    def handle(self, client: 'TNCOClient') -> Dict:
        return {'token': self.token}
