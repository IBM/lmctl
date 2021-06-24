from .sp_client import SitePlannerClient

class SitePlannerClientBuilder:

    def __init__(self):
        self._address = None
        self._api_token = None

    @property
    def address(self):
        return self._address

    def address(self, address: str) -> 'SitePlannerClientBuilder':
        self._address = address
        return self
    
    @property
    def api_token(self):
        return self._api_token

    def api_token(self, api_token: str) -> 'SitePlannerClientBuilder':
        self._api_token = api_token
        return self
    
    def build(self):
        return SitePlannerClient(self._address, api_token=self._api_token)
