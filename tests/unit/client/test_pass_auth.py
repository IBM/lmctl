import unittest
from unittest.mock import MagicMock
from lmctl.client.pass_auth import UserPassAuth, LegacyUserPassAuth

class TestUserPassAuth(unittest.TestCase):

    def test_handle(self):
        auth = UserPassAuth('jack', 'pass123', 'MyClient', 'secret')
        client = MagicMock()
        auth.handle(client)
        client.auth.request_user_access.assert_called_once_with(client_id='MyClient', client_secret='secret', username='jack', password='pass123')

class TestLegacyUserPassAuth(unittest.TestCase):

    def test_handle(self):
        auth = LegacyUserPassAuth('jack', 'pass123')
        client = MagicMock()
        auth.handle(client)
        client.auth.legacy_login.assert_called_once_with(username='jack', password='pass123', legacy_auth_address=None)
    
    def test_handle_with_legacy_address(self):
        auth = LegacyUserPassAuth('jack', 'pass123', legacy_auth_address='http://ui.lm')
        client = MagicMock()
        auth.handle(client)
        client.auth.legacy_login.assert_called_once_with(username='jack', password='pass123', legacy_auth_address='http://ui.lm')