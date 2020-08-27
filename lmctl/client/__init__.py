from .client import LmClient
from .exceptions import LmClientError, LmClientHttpError
from .client_factory import LmClientFactory

factory = LmClientFactory()

def build(address: str, auth: AuthType=None) -> LmClient:
    return factory.build()