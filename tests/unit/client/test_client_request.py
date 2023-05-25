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
            object_group_id='123'
        ))