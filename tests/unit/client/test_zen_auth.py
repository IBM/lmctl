import unittest
from unittest.mock import MagicMock
from lmctl.client.zen_auth import ZenAPIKeyAuth

class TestZenAPIKeyAuth(unittest.TestCase):

    def test_handle(self):
        auth = ZenAPIKeyAuth('User', 'secret', 'http://zen:80/auth')
        client = MagicMock()
        auth.handle(client)
        client.auth.request_zen_api_key_access.assert_called_once_with(username='User', api_key='secret', zen_auth_address='http://zen:80/auth')
