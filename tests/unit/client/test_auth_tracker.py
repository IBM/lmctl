import unittest
import time
import jwt
from datetime import datetime, timedelta
from lmctl.client.auth_tracker import AuthTracker

class TestAuthTracker(unittest.TestCase):

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

    def test_accept_auth_response_with_access_token(self):
        tracker = AuthTracker()
        auth_response = {'accessToken': self._build_a_token()}
        tracker.accept_auth_response(auth_response)
        self.assertEqual(tracker.current_access_token, auth_response['accessToken'])
        self.assertIsNotNone(tracker.time_of_auth)

    def test_accept_auth_response_with_token(self):
        tracker = AuthTracker()
        auth_response = {'token': self._build_a_token()}
        tracker.accept_auth_response(auth_response)
        self.assertEqual(tracker.current_access_token, auth_response['token'])
        self.assertIsNotNone(tracker.time_of_auth)

    def test_has_access_expired_is_true_when_no_token(self):
        tracker = AuthTracker()
        self.assertTrue(tracker.has_access_expired)

    def test_has_access_expired_is_true_when_time_passed(self):
        tracker = AuthTracker()
        auth_response = {'token': self._build_a_token(expires_in=0.1)}
        tracker.accept_auth_response(auth_response)
        time.sleep(0.2)
        self.assertTrue(tracker.has_access_expired)

    def test_has_access_expired_false_when_time_not_passed(self):
        tracker = AuthTracker()
        # Expires in 10 minutes
        auth_response = {'token': self._build_a_token(expires_in=600)}
        tracker.accept_auth_response(auth_response)
        self.assertFalse(tracker.has_access_expired)