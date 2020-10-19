import unittest
from unittest.mock import MagicMock
from lmctl.client.client_credentials_auth import ClientCredentialsAuth

class TestClientCredentialsAuth(unittest.TestCase):

    def test_handle(self):
        auth = ClientCredentialsAuth('MyClient', 'secret')
        client = MagicMock()
        auth.handle(client)
        client.auth.request_client_access.assert_called_once_with('MyClient', 'secret')
