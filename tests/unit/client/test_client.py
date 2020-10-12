import unittest
import requests
from unittest.mock import patch, MagicMock
from lmctl.client import LmClient, LmClientError, LmClientHttpError

class TestLmClient(unittest.TestCase):

    def _get_requests_session(self, mock_requests):
        return mock_requests.return_value

    def _build_mocked_auth_type(self):
        mock_auth = MagicMock()
        mock_auth.handle.return_value = {'expiresIn': 100000, 'accessToken': '123'}
        return mock_auth

    @patch('lmctl.client.client.requests.Session')
    def test_make_request(self, requests_session_builder):
        client = LmClient('test.example.com')
        response = client.make_request('GET', 'api/test')
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with('GET', 'test.example.com/api/test', headers={})
        self.assertEqual(response, mock_session.request.return_value)

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_for_json(self, requests_session_builder):
        client = LmClient('test.example.com')
        response = client.make_request_for_json('GET', 'api/test')
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with('GET', 'test.example.com/api/test', headers={})
        self.assertEqual(response, mock_session.request.return_value.json.return_value)

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_for_json_fails_when_cannot_parse(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.return_value.json.side_effect = ValueError('Mock error')
        client = LmClient('test.example.com')
        with self.assertRaises(LmClientError) as context:
            client.make_request_for_json('GET', 'api/test')
        self.assertEqual(str(context.exception), 'LmClientError: Failed to parse response to JSON: Mock error')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_with_body(self, requests_session_builder):
        client = LmClient('test.example.com')
        client.make_request('POST', 'api/test', body={'id': 'test'})
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with('POST', 'test.example.com/api/test', headers={}, body={'id': 'test'})

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_with_headers(self, requests_session_builder):
        client = LmClient('test.example.com')
        client.make_request('GET', 'api/test', headers={'Accept': 'plain/text'})
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with('GET', 'test.example.com/api/test', headers={'Accept': 'plain/text'})

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_with_auth(self, requests_session_builder):
        mock_auth = self._build_mocked_auth_type()
        client = LmClient('test.example.com', auth=mock_auth)
        client.make_request('GET', 'api/test')
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with('GET', 'test.example.com/api/test', headers={'Authorization': 'Bearer 123'})

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_with_auth_but_include_auth_false(self, requests_session_builder):
        mock_auth = self._build_mocked_auth_type()
        client = LmClient('test.example.com', auth=mock_auth)
        client.make_request('GET', 'api/test', include_auth=False)
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with('GET', 'test.example.com/api/test', headers={})

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_error(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.side_effect = requests.RequestException('Mock error')
        client = LmClient('test.example.com')
        with self.assertRaises(LmClientError) as context:
            client.make_request('GET', 'api/test')
        self.assertEqual(str(context.exception), 'LmClientError: Mock error')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=MagicMock(status_code=400))
        client = LmClient('test.example.com')
        with self.assertRaises(LmClientError) as context:
            client.make_request('GET', 'api/test')
        self.assertEqual(str(context.exception), 'LmClientHttpError: GET request to test.example.com/api/test failed: status=400, message=Mock http error')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_unparsable_json_body(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/json'})
        mock_response.json.side_effect = ValueError('Cannot parse')
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = LmClient('test.example.com')
        with self.assertRaises(LmClientError) as context:
            client.make_request('GET', 'api/test')
        self.assertEqual(str(context.exception), 'LmClientHttpError: GET request to test.example.com/api/test failed: status=400, message=Mock http error')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_json_body_read_localized_message(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/json'})
        mock_response.json.return_value = {'localizedMessage': 'This is the localized message', 'message': 'This is the message'}
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = LmClient('test.example.com')
        with self.assertRaises(LmClientError) as context:
            client.make_request('GET', 'api/test')
        self.assertEqual(str(context.exception), 'LmClientHttpError: GET request to test.example.com/api/test failed: status=400, message=This is the localized message')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_json_body_read_message(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/json'})
        mock_response.json.return_value = {'message': 'This is the message'}
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = LmClient('test.example.com')
        with self.assertRaises(LmClientError) as context:
            client.make_request('GET', 'api/test')
        self.assertEqual(str(context.exception), 'LmClientHttpError: GET request to test.example.com/api/test failed: status=400, message=This is the message')
    
    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_unparsable_yaml_body(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/yaml'}, text='-: notyaml: {"}')
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = LmClient('test.example.com')
        with self.assertRaises(LmClientError) as context:
            client.make_request('GET', 'api/test')
        self.assertEqual(str(context.exception), 'LmClientHttpError: GET request to test.example.com/api/test failed: status=400, message=Mock http error')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_yaml_body_read_localized_message(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/yaml'}, text='localizedMessage: "This is the localized message"\nmessage: "This is the message"')
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = LmClient('test.example.com')
        with self.assertRaises(LmClientError) as context:
            client.make_request('GET', 'api/test')
        self.assertEqual(str(context.exception), 'LmClientHttpError: GET request to test.example.com/api/test failed: status=400, message=This is the localized message')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_yaml_body_read_localized_message(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/yaml'}, text='message: "This is the message"')
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = LmClient('test.example.com')
        with self.assertRaises(LmClientError) as context:
            client.make_request('GET', 'api/test')
        self.assertEqual(str(context.exception), 'LmClientHttpError: GET request to test.example.com/api/test failed: status=400, message=This is the message')
