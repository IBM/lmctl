import unittest
import time
from lmctl.client.auth_tracker import AuthTracker

class TestAuthTracker(unittest.TestCase):

    def test_accept_auth_response(self):
        tracker = AuthTracker()
        tracker.accept_auth_response({
            'accessToken': '123',
            'expiresIn': 60,
        })
        self.assertEqual(tracker.current_access_token,'123')
        self.assertIsNotNone(tracker.time_of_auth)

    def test_has_access_expired_when_no_token(self):
        tracker = AuthTracker()
        self.assertTrue(tracker.has_access_expired)

    def test_has_access_expired(self):
        tracker = AuthTracker()
        tracker.accept_auth_response({
            'accessToken': '123',
            'expiresIn': 0.2,
        })
        time.sleep(0.3)
        self.assertTrue(tracker.has_access_expired)

    def test_has_access_expired_false_when_time_not_passed(self):
        tracker = AuthTracker()
        tracker.accept_auth_response({
            'accessToken': '123',
            'expiresIn': 25,
        })
        self.assertFalse(tracker.has_access_expired)