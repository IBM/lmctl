import unittest
from lmctl.client import TNCOClientRequest

class TestTNCOClientRequest(unittest.TestCase):

    def test_init_minimum(self):
        request = TNCOClientRequest(endpoint='api/test', method='POST')
        self.assertEqual(request, TNCOClientRequest(
            endpoint='api/test',
            method='POST'
        ))

    def test_request_for_json(self):
        request = TNCOClientRequest.build_request_for_json(endpoint='api/test')
        self.assertEqual(request, TNCOClientRequest(
            endpoint='api/test',
            method='GET',
            headers={'Accept': 'application/json'}
        ))

        request = TNCOClientRequest.build_request_for_json(endpoint='api/test', method='POST')
        self.assertEqual(request, TNCOClientRequest(
            endpoint='api/test',
            method='POST',
            headers={'Accept': 'application/json'}
        ))

        request = TNCOClientRequest.build_request_for_json(endpoint='api/test', query_params={'Testing': True})
        self.assertEqual(request, TNCOClientRequest(
            endpoint='api/test',
            method='GET',
            headers={'Accept': 'application/json'},
            query_params={'Testing': True}
        ))

        request = TNCOClientRequest.build_request_for_json(endpoint='api/test', query_params={'Testing': True}, object_group_id='123')
        self.assertEqual(request, TNCOClientRequest(
            endpoint='api/test',
            method='GET',
            headers={'Accept': 'application/json'},
            query_params={'Testing': True},
            object_group_id_param='123'
        ))
    
    def test_missing_endpoint_and_override_address(self):
        with self.assertRaises(ValueError) as context:
            TNCOClientRequest(method='GET')
        self.assertEqual(str(context.exception).split('[type=value_error')[0].strip(), '1 validation error for TNCOClientRequest\n  Value error, At least one of endpoint or override_address must be set')

        request = TNCOClientRequest(method='GET', endpoint='api/test', override_address=None )
        self.assertEqual(request, TNCOClientRequest(
            method='GET',
            endpoint='api/test'
        ))

        request = TNCOClientRequest(method='GET', override_address='https://zen:80', endpoint=None)
        self.assertEqual(request, TNCOClientRequest(
            method='GET',
            override_address='https://zen:80'
        ))