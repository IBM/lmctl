import unittest
from unittest.mock import MagicMock
from lmctl.client.zen_auth import ZenAPIKeyAuth
from lmctl.client.api.auth import AuthenticationAPI

class TestZenAPIKeyAuth(unittest.TestCase):

    def test_handle_with_override_address(self):
        auth = ZenAPIKeyAuth('User', 'secret', zen_auth_address='https://auth.example.com')
        client = MagicMock(auth=MagicMock(cp_auth_endpoint=AuthenticationAPI.cp_auth_endpoint))
        auth.handle(client)
        client.auth.request_zen_api_key_access.assert_called_once_with(username='User', api_key='secret', zen_auth_address='https://auth.example.com', override_auth_endpoint=None)

    def test_handle_without_override_address(self):
        auth = ZenAPIKeyAuth('User', 'secret')
        client = MagicMock(auth=MagicMock(cp_auth_endpoint=AuthenticationAPI.cp_auth_endpoint))
        auth.handle(client)
        client.auth.request_zen_api_key_access.assert_called_once_with(username='User', api_key='secret', zen_auth_address=None, override_auth_endpoint=None)

    def test_handle_with_override_address_containing_default_auth_endpoint(self):
        auth = ZenAPIKeyAuth('User', 'secret', zen_auth_address='https://auth.example.com/icp4d-api/v1/authorize')
        client = MagicMock(auth=MagicMock(cp_auth_endpoint=AuthenticationAPI.cp_auth_endpoint))
        auth.handle(client)
        client.auth.request_zen_api_key_access.assert_called_once_with(username='User', api_key='secret', zen_auth_address='https://auth.example.com/icp4d-api/v1/authorize', override_auth_endpoint=None)

    def test_handle_with_override_address_and_override_endpoint(self):
        auth = ZenAPIKeyAuth('User', 'secret', zen_auth_address='https://auth.example.com/proxy-zen-api', override_auth_endpoint='v1/otherAuth')
        client = MagicMock(auth=MagicMock(cp_auth_endpoint=AuthenticationAPI.cp_auth_endpoint))
        auth.handle(client)
        client.auth.request_zen_api_key_access.assert_called_once_with(username='User', api_key='secret', zen_auth_address='https://auth.example.com/proxy-zen-api', override_auth_endpoint='v1/otherAuth')
   
    def test_handle_with_override_endpoint(self):
        auth = ZenAPIKeyAuth('User', 'secret', override_auth_endpoint='v1/otherAuth')
        client = MagicMock(auth=MagicMock(cp_auth_endpoint=AuthenticationAPI.cp_auth_endpoint))
        auth.handle(client)
        client.auth.request_zen_api_key_access.assert_called_once_with(username='User', api_key='secret', zen_auth_address=None, override_auth_endpoint='v1/otherAuth')



    