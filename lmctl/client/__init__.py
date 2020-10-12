from .client import LmClient
from .exceptions import LmClientError, LmClientHttpError
from .client_factory import LmClientFactory
from .auth_type import AuthType

factory = LmClientFactory()

def build(address: str, auth: AuthType = None) -> LmClient:
    return factory.build()