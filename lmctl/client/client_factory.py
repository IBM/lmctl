from .auth_type import AuthType
from .client import LmClient

class LmClientFactory:

    def build(self, address: str, auth: AuthType=None) -> LmClient:
        return LmClient(address, auth=auth)