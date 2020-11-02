import unittest
import base64
from unittest.mock import MagicMock, call
from lmctl.client.api import AuthenticationAPI
from lmctl.client.exceptions import TNCOClientHttpError
from requests.auth import HTTPBasicAuth

class TestAuthenticationAPI(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()
        self.authentication = AuthenticationAPI(self.mock_client)

    def test_request_client_access(self):
        self.mock_client.make_request_for_json.return_value = {'access_token': '123', 'expires_in': 60}
        response = self.authentication.request_client_access('LmClient', 'secret')
        self.assertEqual(response, {'access_token': '123', 'expires_in': 60})
        client_encoded = base64.b64encode('LmClient:secret'.encode('utf-8'))
        auth = HTTPBasicAuth('LmClient', 'secret')
        self.mock_client.make_request_for_json.assert_called_with(method='POST', 
                                                                    endpoint='oauth/token',
                                                                    auth=auth, 
                                                                    include_auth=False, 
                                                                    data={'grant_type': 'client_credentials'})

    def test_request_user_access(self):
        self.mock_client.make_request_for_json.return_value = {'access_token': '123', 'expires_in': 60}
        response = self.authentication.request_user_access('LmClient', 'secret', 'joe', 'secretpass')
        self.assertEqual(response, {'access_token': '123', 'expires_in': 60})
        client_encoded = base64.b64encode('LmClient:secret'.encode('utf-8'))
        auth = HTTPBasicAuth('LmClient', 'secret')
        self.mock_client.make_request_for_json.assert_called_with(method='POST', 
                                                                    endpoint='oauth/token',
                                                                    auth=auth, 
                                                                    include_auth=False, 
                                                                    data={
                                                                        'grant_type': 'password',
                                                                        'username': 'joe', 
                                                                        'password': 'secretpass'
                                                                    })

    def test_legacy_login(self):
        self.mock_client.make_request_for_json.return_value = {'accessToken': '123', 'expiresIn': 60}
        response = self.authentication.legacy_login('joe', 'secretpass')
        self.assertEqual(response, {'accessToken': '123', 'expiresIn': 60})
        self.mock_client.make_request_for_json.assert_called_with(method='POST', 
                                                                    endpoint='ui/api/login',
                                                                    include_auth=False, 
                                                                    override_address=None,
                                                                    json={
                                                                        'username': 'joe', 
                                                                        'password': 'secretpass'
                                                                    })

    def test_legacy_login_older_environments(self):
        def request_mock(endpoint, *args, **kwargs):
            if endpoint == 'ui/api/login':
                raise TNCOClientHttpError('Mock error', cause=MagicMock(response=MagicMock(status_code=404, headers={}, body=b'')))
            else:
                return {'accessToken': '123', 'expiresIn': 60}
        self.mock_client.make_request_for_json.side_effect = request_mock
        response = self.authentication.legacy_login('joe', 'secretpass')
        self.assertEqual(response, {'accessToken': '123', 'expiresIn': 60})
        self.mock_client.make_request_for_json.assert_has_calls([
            call(method='POST', 
                endpoint='ui/api/login',
                include_auth=False, 
                override_address=None,
                json={
                    'username': 'joe', 
                    'password': 'secretpass'
                }
            ),
            call(method='POST', 
                endpoint='api/login',
                include_auth=False, 
                override_address=None,
                json={
                    'username': 'joe', 
                    'password': 'secretpass'
                }
            )
        ])