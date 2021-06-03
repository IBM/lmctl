import unittest
from unittest.mock import MagicMock
from lmctl.client.token_auth import JwtTokenAuth

class TestJwtTokenAuth(unittest.TestCase):

    def test_handle(self):
        auth = JwtTokenAuth(token='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c')
        client = MagicMock()
        response = auth.handle(client)
        self.assertEqual(response, {'token': auth.token})
