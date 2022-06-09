import unittest
from unittest.mock import patch
from requests import Session, Response

from lmctl.client import SitePlannerClient, TNCOClient
from lmctl.client.sp_client import SitePlannerSessionProxy

from .token_helper import FakeTNCOAuth

class TestSitePlannerClient(unittest.TestCase):

    def test_address_with_trailing_slash_is_trimmed(self):
        client = SitePlannerClient('https://sp.example.com/')
        self.assertEqual(client.address, 'https://sp.example.com')

    def test_pynetbox_session_not_proxied_when_api_token_is_used(self):
        client = SitePlannerClient('https://sp.example.com', api_token='abcdef', parent_client=TNCOClient('https://tnco.example.com'))
        self.assertIsInstance(client.pynb_api.http_session, Session)

    def test_pynetbox_session_proxied_when_api_token_not_used(self):
        client = SitePlannerClient('https://sp.example.com', parent_client=TNCOClient('https://tnco.example.com'))
        self.assertIsInstance(client.pynb_api.http_session, SitePlannerSessionProxy)
    
    def _get_http_request_from_send(self, mock_http):
        last_call = mock_http.return_value.send.call_args_list[0]
        args = last_call[0]
        # Get the "request" arg, first in the signature
        return args[0]

    def _mock_delete_call(self, client, mock_http):
        mock_response = Response()
        mock_response.status_code = 204
        mock_http.return_value.send.return_value = mock_response
        # Make the call
        client.dcim.sites.delete(['1'])

        return self._get_http_request_from_send(mock_http)

    @patch('requests.sessions.HTTPAdapter')
    def test_request_uses_api_token(self, mock_http):

        client = SitePlannerClient('https://sp.example.com', api_token='abcdef')
        
        # Make a call
        captured_request = self._mock_delete_call(client, mock_http)

        self.assertIn('Authorization', captured_request.headers)
        self.assertEqual(captured_request.headers['Authorization'], 'Token abcdef')

    @patch('requests.sessions.HTTPAdapter')
    def test_request_does_not_use_api_token_when_auth_disabled(self, mock_http):

        client = SitePlannerClient('https://sp.example.com', use_auth=False, api_token='abcdef')
        
        # Make a call
        captured_request = self._mock_delete_call(client, mock_http)

        self.assertNotIn('Authorization', captured_request.headers)
        
    @patch('requests.sessions.HTTPAdapter')
    def test_request_uses_tnco_auth(self, mock_http):

        auth_type = FakeTNCOAuth()
        client = SitePlannerClient('https://sp.example.com', parent_client=TNCOClient('https://tnco.example.com', auth_type=auth_type))
        
        # Make a call
        captured_request = self._mock_delete_call(client, mock_http)

        self.assertIn('Authorization', captured_request.headers)
        self.assertEqual(captured_request.headers['Authorization'], f'Bearer {auth_type.token}')

    @patch('requests.sessions.HTTPAdapter')
    def test_request_does_not_use_tnco_auth_when_auth_disabled(self, mock_http):

        auth_type = FakeTNCOAuth()
        client = SitePlannerClient('https://sp.example.com', use_auth=False, parent_client=TNCOClient('https://tnco.example.com', auth_type=auth_type))
        
        # Make a call
        captured_request = self._mock_delete_call(client, mock_http)

        self.assertNotIn('Authorization', captured_request.headers)
        
    @patch('requests.sessions.HTTPAdapter')
    def test_inject_sp_path_adds_to_url(self, mock_http):

        client = SitePlannerClient('https://sp.example.com', api_token='abcdef', inject_sp_path=True)
        
        # Make a call
        captured_request = self._mock_delete_call(client, mock_http)

        self.assertEqual(captured_request.url, 'https://sp.example.com/api/site-planner/dcim/sites/')

    @patch('requests.sessions.HTTPAdapter')
    def test_inject_sp_path_disabled_does_not_add_to_url(self, mock_http):

        client = SitePlannerClient('https://sp.example.com', api_token='abcdef')
        
        # Make a call
        captured_request = self._mock_delete_call(client, mock_http)

        self.assertEqual(captured_request.url, 'https://sp.example.com/api/dcim/sites/')
