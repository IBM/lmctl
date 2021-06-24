import unittest
import requests
import json
import jwt
from unittest.mock import patch, MagicMock, Mock
from lmctl.client import TNCOClient, TNCOClientError, TNCOClientHttpError, TNCOErrorCapture, TNCOClientRequest
from datetime import datetime, timedelta

class TestTNCOClient(unittest.TestCase):

    def _get_requests_session(self, mock_requests):
        return mock_requests.return_value
    
    def _build_a_token(self, expires_in=30):
        token_content = {
            'sub': '1234567890',
            'name': 'John Doe',
            'admin': True,
            'jti': 'c257f98d-f4dd-4fa9-afb4-6329924316f2',
            'iat': int(datetime.now().strftime('%s')),
            'exp': int((datetime.now() + timedelta(seconds=expires_in)).strftime('%s'))
        }
        return jwt.encode(token_content, 'secret', algorithm='HS256')

    def _build_mocked_auth_type(self):
        mock_auth = MagicMock()
        self.token = self._build_a_token()
        mock_auth.handle.return_value = {'token': self.token}
        return mock_auth

    def test_address_with_trailing_slash_is_trimmed(self):
        client = TNCOClient('https://test.example.com/')
        self.assertEqual(client.address, 'https://test.example.com')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request(self, requests_session_builder):
        client = TNCOClient('https://test.example.com', use_sessions=True)
        response = client.make_request(TNCOClientRequest(method='GET', endpoint='api/test'))
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with(method='GET', url='https://test.example.com/api/test', headers={}, verify=False)
        self.assertEqual(response, mock_session.request.return_value)

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_for_json(self, requests_session_builder):
        client = TNCOClient('https://test.example.com', use_sessions=True)
        response = client.make_request_for_json(TNCOClientRequest(method='GET', endpoint='api/test'))
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with(method='GET', url='https://test.example.com/api/test', headers={}, verify=False)
        self.assertEqual(response, mock_session.request.return_value.json.return_value)

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_for_json_fails_when_cannot_parse(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.return_value.json.side_effect = ValueError('Mock error')
        client = TNCOClient('https://test.example.com', use_sessions=True)
        with self.assertRaises(TNCOClientError) as context:
            client.make_request_for_json(TNCOClientRequest(method='GET', endpoint='api/test'))
        self.assertEqual(str(context.exception), 'Failed to parse response to JSON: Mock error')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_with_body(self, requests_session_builder):
        client = TNCOClient('https://test.example.com', use_sessions=True)
        client.make_request(TNCOClientRequest(method='POST', endpoint='api/test', body=json.dumps({'id': 'test'})))
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with(method='POST', url='https://test.example.com/api/test', data=json.dumps({'id': 'test'}), headers={}, verify=False)

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_with_headers(self, requests_session_builder):
        client = TNCOClient('https://test.example.com', use_sessions=True)
        client.make_request(TNCOClientRequest(method='GET', endpoint='api/test', headers={'Accept': 'plain/text'}))
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with(method='GET', url='https://test.example.com/api/test', headers={'Accept': 'plain/text'}, verify=False)
    
    @patch('lmctl.client.client.requests.Session')
    def test_make_request_with_auth(self, requests_session_builder):
        mock_auth = self._build_mocked_auth_type()
        client = TNCOClient('https://test.example.com', auth_type=mock_auth, use_sessions=True)
        client.make_request(TNCOClientRequest(method='GET', endpoint='api/test'))
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with(method='GET', url='https://test.example.com/api/test', headers={'Authorization': f'Bearer {self.token}'}, verify=False)

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_with_auth_but_inject_current_auth_false(self, requests_session_builder):
        mock_auth = self._build_mocked_auth_type()
        client = TNCOClient('https://test.example.com', auth_type=mock_auth, use_sessions=True)
        client.make_request(TNCOClientRequest(method='GET', endpoint='api/test', inject_current_auth=False))
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.assert_called_with(method='GET', url='https://test.example.com/api/test', headers={}, verify=False)

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_with_trace_ctx(self, requests_session_builder):
        from lmctl.utils.trace_ctx import trace_ctx
        with trace_ctx.scope(transaction_id='123456789'):
            client = TNCOClient('https://test.example.com', use_sessions=True)
            client.make_request(TNCOClientRequest(method='GET', endpoint='api/test'))
            mock_session = self._get_requests_session(requests_session_builder)
            mock_session.request.assert_called_with(method='GET', url='https://test.example.com/api/test', headers={'X-Tracectx-TransactionId': '123456789'}, verify=False)

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_combines_trace_ctx_and_auth_and_user_supplied_headers(self, requests_session_builder):
        mock_auth = self._build_mocked_auth_type()
        from lmctl.utils.trace_ctx import trace_ctx
        with trace_ctx.scope(transaction_id='123456789'):
            client = TNCOClient('https://test.example.com', auth_type=mock_auth, use_sessions=True)
            client.make_request(TNCOClientRequest(method='GET', endpoint='api/test', headers={'Accept': 'plain/text'}))
            mock_session = self._get_requests_session(requests_session_builder)
            mock_session.request.assert_called_with(method='GET', url='https://test.example.com/api/test', headers={'Accept': 'plain/text', 'Authorization': f'Bearer {self.token}', 'X-Tracectx-TransactionId': '123456789'}, verify=False)

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_error(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.side_effect = requests.RequestException('Mock error')
        client = TNCOClient('https://test.example.com', use_sessions=True)
        with self.assertRaises(TNCOClientError) as context:
            client.make_request(TNCOClientRequest(method='GET', endpoint='api/test'))
        self.assertEqual(str(context.exception), 'Mock error')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=MagicMock(status_code=400))
        client = TNCOClient('https://test.example.com', use_sessions=True)
        with self.assertRaises(TNCOClientError) as context:
            client.make_request(TNCOClientRequest(method='GET', endpoint='api/test'))
        self.assertEqual(str(context.exception), 'GET request to https://test.example.com/api/test failed: status=400, message=Mock http error')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_unparsable_json_body(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/json'})
        mock_response.json.side_effect = ValueError('Cannot parse')
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = TNCOClient('https://test.example.com', use_sessions=True)
        with self.assertRaises(TNCOClientError) as context:
            client.make_request(TNCOClientRequest(method='GET', endpoint='api/test'))
        self.assertEqual(str(context.exception), 'GET request to https://test.example.com/api/test failed: status=400, message=Mock http error')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_json_body_read_localized_message(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/json'})
        mock_response.json.return_value = {'localizedMessage': 'This is the localized message', 'message': 'This is the message'}
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = TNCOClient('https://test.example.com', use_sessions=True)
        with self.assertRaises(TNCOClientError) as context:
            client.make_request(TNCOClientRequest(method='GET', endpoint='api/test'))
        self.assertEqual(str(context.exception), 'GET request to https://test.example.com/api/test failed: status=400, message=This is the localized message')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_json_body_read_message(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/json'})
        mock_response.json.return_value = {'message': 'This is the message'}
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = TNCOClient('https://test.example.com', use_sessions=True)
        with self.assertRaises(TNCOClientError) as context:
            client.make_request(TNCOClientRequest(method='GET', endpoint='api/test'))
        self.assertEqual(str(context.exception), 'GET request to https://test.example.com/api/test failed: status=400, message=This is the message')
    
    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_unparsable_yaml_body(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/yaml'}, text='-: notyaml: {"}')
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = TNCOClient('https://test.example.com', use_sessions=True)
        with self.assertRaises(TNCOClientError) as context:
            client.make_request(TNCOClientRequest(method='GET', endpoint='api/test'))
        self.assertEqual(str(context.exception), 'GET request to https://test.example.com/api/test failed: status=400, message=Mock http error')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_yaml_body_read_localized_message(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/yaml'}, text='localizedMessage: "This is the localized message"\nmessage: "This is the message"')
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = TNCOClient('https://test.example.com', use_sessions=True)
        with self.assertRaises(TNCOClientError) as context:
            client.make_request(TNCOClientRequest(method='GET', endpoint='api/test'))
        self.assertEqual(str(context.exception), 'GET request to https://test.example.com/api/test failed: status=400, message=This is the localized message')

    @patch('lmctl.client.client.requests.Session')
    def test_make_request_raises_http_error_with_yaml_body_read_localized_message(self, requests_session_builder):
        mock_session = self._get_requests_session(requests_session_builder)
        mock_response = MagicMock(status_code=400, headers={'Content-Type': 'application/yaml'}, text='message: "This is the message"')
        mock_session.request.return_value.raise_for_status.side_effect = requests.HTTPError('Mock http error', response=mock_response)
        client = TNCOClient('https://test.example.com', use_sessions=True)
        with self.assertRaises(TNCOClientError) as context:
            client.make_request(TNCOClientRequest(method='GET', endpoint='api/test'))
        self.assertEqual(str(context.exception), 'GET request to https://test.example.com/api/test failed: status=400, message=This is the message')

    
    @patch('lmctl.client.client.SharedInfrastructureKeysAPI')
    @patch('lmctl.client.client.BehaviourProjectsAPI')
    @patch('lmctl.client.client.DescriptorsAPI')
    @patch('lmctl.client.client.DeploymentLocationAPI')
    def test_ping(self, mock_dl_api, mock_descriptors_api, mock_projects_api, mock_keys_api):
        mock_dl_api.return_value.all.return_value = []
        mock_descriptors_api.return_value.all.return_value = []
        mock_projects_api.return_value.all.return_value = []
        mock_keys_api.return_value.all.return_value = []
        client = TNCOClient('https://test.example.com', use_sessions=True)
        result = client.ping()
        self.assertTrue(result.passed)
        self.assertTrue(len(result.tests) == 4, msg='Unexpected number of results')
        self.assertEqual(result.tests[0].name, 'Descriptors')
        self.assertTrue(result.tests[0].passed)
        self.assertIsNone(result.tests[0].error)
        self.assertEqual(result.tests[1].name, 'Topology')
        self.assertTrue(result.tests[1].passed)
        self.assertIsNone(result.tests[1].error)
        self.assertEqual(result.tests[2].name, 'Behaviour')
        self.assertTrue(result.tests[2].passed)
        self.assertIsNone(result.tests[2].error)
        self.assertEqual(result.tests[3].name, 'Resource Manager')
        self.assertTrue(result.tests[3].passed)
        self.assertIsNone(result.tests[3].error)
    
    @patch('lmctl.client.client.DescriptorTemplatesAPI')
    @patch('lmctl.client.client.SharedInfrastructureKeysAPI')
    @patch('lmctl.client.client.BehaviourProjectsAPI')
    @patch('lmctl.client.client.DescriptorsAPI')
    @patch('lmctl.client.client.DeploymentLocationAPI')
    def test_ping_include_template_engine(self, mock_dl_api, mock_descriptors_api, mock_projects_api, mock_keys_api, mock_templates_api):
        mock_dl_api.return_value.all.return_value = []
        mock_descriptors_api.return_value.all.return_value = []
        mock_projects_api.return_value.all.return_value = []
        mock_keys_api.return_value.all.return_value = []
        mock_templates_api.all.return_value = []
        client = TNCOClient('https://test.example.com', use_sessions=True)
        result = client.ping(include_template_engine=True)
        self.assertTrue(result.passed)
        self.assertEqual(len(result.tests), 5, msg='Unexpected number of results')
        self.assertEqual(result.tests[0].name, 'Descriptors')
        self.assertTrue(result.tests[0].passed)
        self.assertIsNone(result.tests[0].error)
        self.assertEqual(result.tests[1].name, 'Topology')
        self.assertTrue(result.tests[1].passed)
        self.assertIsNone(result.tests[1].error)
        self.assertEqual(result.tests[2].name, 'Behaviour')
        self.assertTrue(result.tests[2].passed)
        self.assertIsNone(result.tests[2].error)
        self.assertEqual(result.tests[3].name, 'Resource Manager')
        self.assertTrue(result.tests[3].passed)
        self.assertIsNone(result.tests[3].error)
        self.assertEqual(result.tests[4].name, 'Template Engine')
        self.assertTrue(result.tests[4].passed)
        self.assertIsNone(result.tests[4].error)
    
    @patch('lmctl.client.client.SharedInfrastructureKeysAPI')
    @patch('lmctl.client.client.BehaviourProjectsAPI')
    @patch('lmctl.client.client.DescriptorsAPI')
    @patch('lmctl.client.client.DeploymentLocationAPI')
    def test_ping_captures_errors(self, mock_dl_api, mock_descriptors_api, mock_projects_api, mock_keys_api):
        mock_dl_api.return_value.all.return_value = []
        mock_descriptors_api.return_value.all.return_value = []
        mock_error = TNCOClientError('Mock error')
        mock_projects_api.return_value.all.side_effect = mock_error
        mock_keys_api.return_value.all.return_value = []
        client = TNCOClient('https://test.example.com', use_sessions=True)
        result = client.ping()
        self.assertFalse(result.passed)
        self.assertTrue(len(result.tests) == 4, msg='Unexpected number of results')
        self.assertEqual(result.tests[0].name, 'Descriptors')
        self.assertTrue(result.tests[0].passed)
        self.assertIsNone(result.tests[0].error)
        self.assertEqual(result.tests[1].name, 'Topology')
        self.assertTrue(result.tests[1].passed)
        self.assertIsNone(result.tests[1].error)
        self.assertEqual(result.tests[2].name, 'Behaviour')
        self.assertFalse(result.tests[2].passed)
        self.assertEqual(result.tests[2].error, mock_error)
        self.assertEqual(result.tests[3].name, 'Resource Manager')
        self.assertTrue(result.tests[3].passed)
        self.assertIsNone(result.tests[3].error)
        