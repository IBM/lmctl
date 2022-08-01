import unittest
import time
from lmctl.client.auth_tracker import AuthTracker
from .token_helper import build_a_token

class TestAuthTracker(unittest.TestCase):

    def test_accept_auth_response_with_access_token(self):
        tracker = AuthTracker()
        auth_response = {'accessToken': build_a_token()}
        tracker.accept_auth_response(auth_response)
        self.assertEqual(tracker.current_access_token, auth_response['accessToken'])
        self.assertIsNotNone(tracker.time_of_auth)

    def test_accept_auth_response_with_token(self):
        tracker = AuthTracker()
        auth_response = {'token': build_a_token()}
        tracker.accept_auth_response(auth_response)
        self.assertEqual(tracker.current_access_token, auth_response['token'])
        self.assertIsNotNone(tracker.time_of_auth)

    def test_has_access_expired_is_true_when_no_token(self):
        tracker = AuthTracker()
        self.assertTrue(tracker.has_access_expired)

    def test_has_access_expired_is_true_when_time_passed(self):
        tracker = AuthTracker()
        auth_response = {'token': build_a_token(expires_in=0.1)}
        tracker.accept_auth_response(auth_response)
        time.sleep(0.2)
        self.assertTrue(tracker.has_access_expired)

    def test_has_access_expired_false_when_time_not_passed(self):
        tracker = AuthTracker()
        # Expires in 10 minutes
        auth_response = {'token': build_a_token(expires_in=600)}
        tracker.accept_auth_response(auth_response)
        self.assertFalse(tracker.has_access_expired)