import unittest
import base64
import json
from unittest.mock import MagicMock, call
from lmctl.client.api import AuthenticationAPI
from lmctl.client.exceptions import TNCOClientHttpError
from requests.auth import HTTPBasicAuth
from lmctl.client.client_request import TNCOClientRequest

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
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
            method='POST',
            endpoint='oauth/token',
            additional_auth_handler=auth, 
            inject_current_auth=False, 
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            body={'grant_type': 'client_credentials'}
        ))

    def test_request_user_access(self):
        self.mock_client.make_request_for_json.return_value = {'access_token': '123', 'expires_in': 60}
        response = self.authentication.request_user_access('LmClient', 'secret', 'joe', 'secretpass')
        self.assertEqual(response, {'access_token': '123', 'expires_in': 60})
        client_encoded = base64.b64encode('LmClient:secret'.encode('utf-8'))
        auth = HTTPBasicAuth('LmClient', 'secret')
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
            method='POST',
            endpoint='oauth/token',
            additional_auth_handler=auth, 
            inject_current_auth=False, 
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            body={'username': 'joe', 'password': 'secretpass', 'grant_type': 'password'}
        ))

    def test_legacy_login(self):
        self.mock_client.make_request_for_json.return_value = {'accessToken': '123', 'expiresIn': 60}
        response = self.authentication.legacy_login('joe', 'secretpass')
        self.assertEqual(response, {'accessToken': '123', 'expiresIn': 60})
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
            method='POST',
            endpoint='ui/api/login',
            override_address=None,
            inject_current_auth=False, 
            headers={'Content-Type': 'application/json'}, 
            body={'username': 'joe', 'password': 'secretpass'}
        ))

    def test_legacy_login_with_auth_address(self):
        self.mock_client.make_request_for_json.return_value = {'accessToken': '123', 'expiresIn': 60}
        response = self.authentication.legacy_login('joe', 'secretpass', legacy_auth_address='https://auth.example.com')
        self.assertEqual(response, {'accessToken': '123', 'expiresIn': 60})
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
            method='POST',
            endpoint='ui/api/login',
            override_address='https://auth.example.com',
            inject_current_auth=False, 
            headers={'Content-Type': 'application/json'}, 
            body={'username': 'joe', 'password': 'secretpass'}
        ))

    def test_legacy_login_older_environments(self):
        def request_mock(request):
            if request.endpoint == 'ui/api/login':
                raise TNCOClientHttpError('Mock error', cause=MagicMock(response=MagicMock(status_code=404, headers={}, body=b'')))
            else:
                return {'accessToken': '123', 'expiresIn': 60}
        self.mock_client.make_request_for_json.side_effect = request_mock
        response = self.authentication.legacy_login('joe', 'secretpass')
        self.assertEqual(response, {'accessToken': '123', 'expiresIn': 60})
        self.mock_client.make_request_for_json.assert_has_calls([
            call(
                TNCOClientRequest(
                    method='POST',
                    endpoint='ui/api/login',
                    override_address=None,
                    inject_current_auth=False, 
                    headers={'Content-Type': 'application/json'}, 
                    body={'username': 'joe', 'password': 'secretpass'}
                )
            ),
            call(
                TNCOClientRequest(
                    method='POST',
                    endpoint='api/login',
                    override_address=None,
                    inject_current_auth=False,
                    headers={'Content-Type': 'application/json'}, 
                    body={'username': 'joe', 'password': 'secretpass'}
                )
            )
        ])
    
    def test_request_zen_api_key_access(self):        
        self.mock_client.make_request_for_json.return_value = {'token': '123'}
        response = self.authentication.request_zen_api_key_access('joe', 'secretkey')
        self.assertEqual(response, {'token': '123'})
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
                                                                    method='POST', 
                                                                    endpoint='icp4d-api/v1/authorize',
                                                                    inject_current_auth=False, 
                                                                    override_address=None,
                                                                    headers={'Content-Type': 'application/json'},
                                                                    body={
                                                                            'username': 'joe', 
                                                                            'api_key': 'secretkey'
                                                                        }
                                                                    ))

    def test_request_zen_api_key_access_with_override_address(self):        
        self.mock_client.make_request_for_json.return_value = {'token': '123'}
        response = self.authentication.request_zen_api_key_access('joe', 'secretkey', zen_auth_address='https://auth.example.com')
        self.assertEqual(response, {'token': '123'})
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
                                                                    method='POST', 
                                                                    endpoint='icp4d-api/v1/authorize',
                                                                    inject_current_auth=False, 
                                                                    override_address='https://auth.example.com',
                                                                    headers={'Content-Type': 'application/json'},
                                                                    body={
                                                                            'username': 'joe', 
                                                                            'api_key': 'secretkey'
                                                                        }
                                                                    ))
        
    def test_request_zen_api_key_access_with_override_address_containing_default_endpoint(self):        
        self.mock_client.make_request_for_json.return_value = {'token': '123'}
        response = self.authentication.request_zen_api_key_access('joe', 'secretkey', zen_auth_address='https://auth.example.com/icp4d-api/v1/authorize')
        self.assertEqual(response, {'token': '123'})
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
                                                                    method='POST', 
                                                                    endpoint='icp4d-api/v1/authorize',
                                                                    inject_current_auth=False, 
                                                                    override_address='https://auth.example.com/',
                                                                    headers={'Content-Type': 'application/json'},
                                                                    body={
                                                                            'username': 'joe', 
                                                                            'api_key': 'secretkey'
                                                                        }
                                                                    ))
        
    def test_request_zen_api_key_access_with_override_address_containing_default_endpoint_with_trailing_slash(self):        
        self.mock_client.make_request_for_json.return_value = {'token': '123'}
        response = self.authentication.request_zen_api_key_access('joe', 'secretkey', zen_auth_address='https://auth.example.com/icp4d-api/v1/authorize/')
        self.assertEqual(response, {'token': '123'})
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
                                                                    method='POST', 
                                                                    endpoint='icp4d-api/v1/authorize',
                                                                    inject_current_auth=False, 
                                                                    override_address='https://auth.example.com/',
                                                                    headers={'Content-Type': 'application/json'},
                                                                    body={
                                                                            'username': 'joe', 
                                                                            'api_key': 'secretkey'
                                                                        }
                                                                    ))
        
    def test_request_zen_api_key_access_with_override_endpoint(self):        
        self.mock_client.make_request_for_json.return_value = {'token': '123'}
        response = self.authentication.request_zen_api_key_access('joe', 'secretkey', override_auth_endpoint='v2/auth')
        self.assertEqual(response, {'token': '123'})
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
                                                                    method='POST', 
                                                                    endpoint='v2/auth',
                                                                    inject_current_auth=False, 
                                                                    override_address=None,
                                                                    headers={'Content-Type': 'application/json'},
                                                                    body={
                                                                            'username': 'joe', 
                                                                            'api_key': 'secretkey'
                                                                        }
                                                                    ))
        
    def test_request_zen_api_key_access_with_override_address_and_override_endpoint(self):        
        self.mock_client.make_request_for_json.return_value = {'token': '123'}
        response = self.authentication.request_zen_api_key_access('joe', 'secretkey', zen_auth_address='https://auth.example.com', override_auth_endpoint='v2/auth')
        self.assertEqual(response, {'token': '123'})
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
                                                                    method='POST', 
                                                                    endpoint='v2/auth',
                                                                    inject_current_auth=False, 
                                                                    override_address='https://auth.example.com',
                                                                    headers={'Content-Type': 'application/json'},
                                                                    body={
                                                                            'username': 'joe', 
                                                                            'api_key': 'secretkey'
                                                                        }
                                                                    ))
        
    def test_request_zen_api_key_access_with_override_address_containg_default_endpoint_and_override_endpoint(self):      
        self.mock_client.make_request_for_json.return_value = {'token': '123'}
        response = self.authentication.request_zen_api_key_access('joe', 'secretkey', zen_auth_address='https://auth.example.com/icp4d-api/v1/authorize', override_auth_endpoint='v2/auth')
        self.assertEqual(response, {'token': '123'})
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
                                                                    method='POST', 
                                                                    endpoint='v2/auth',
                                                                    inject_current_auth=False, 
                                                                    override_address='https://auth.example.com/',
                                                                    headers={'Content-Type': 'application/json'},
                                                                    body={
                                                                            'username': 'joe', 
                                                                            'api_key': 'secretkey'
                                                                        }
                                                                    ))
        
    def test_request_zen_api_key_access_with_override_address_and_override_endpoint_same_as_default_endpoint(self):      
        self.mock_client.make_request_for_json.return_value = {'token': '123'}
        response = self.authentication.request_zen_api_key_access('joe', 'secretkey', zen_auth_address='https://auth.example.com/', override_auth_endpoint='icp4d-api/v1/authorize')
        self.assertEqual(response, {'token': '123'})
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
                                                                    method='POST', 
                                                                    endpoint='icp4d-api/v1/authorize',
                                                                    inject_current_auth=False, 
                                                                    override_address='https://auth.example.com/',
                                                                    headers={'Content-Type': 'application/json'},
                                                                    body={
                                                                            'username': 'joe', 
                                                                            'api_key': 'secretkey'
                                                                        }
                                                                    ))
        
    def test_request_zen_api_key_access_with_override_address_and_override_endpoint_containing_default_endpoint(self):      
        self.mock_client.make_request_for_json.return_value = {'token': '123'}
        response = self.authentication.request_zen_api_key_access('joe', 'secretkey', zen_auth_address='https://auth.example.com/', override_auth_endpoint='icp4d-api/v1/authorize/ext/auth')
        self.assertEqual(response, {'token': '123'})
        self.mock_client.make_request_for_json.assert_called_with(TNCOClientRequest(
                                                                    method='POST', 
                                                                    endpoint='icp4d-api/v1/authorize/ext/auth',
                                                                    inject_current_auth=False, 
                                                                    override_address='https://auth.example.com/',
                                                                    headers={'Content-Type': 'application/json'},
                                                                    body={
                                                                            'username': 'joe', 
                                                                            'api_key': 'secretkey'
                                                                        }
                                                                    ))