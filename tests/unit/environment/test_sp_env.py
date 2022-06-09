import unittest
from pydantic import ValidationError
from lmctl.environment import SitePlannerEnvironmentOverrides

class TestSitePlannerEnvironmentOverrides(unittest.TestCase):
    maxDiff = None

    def test_init_with_address(self):
        config = SitePlannerEnvironmentOverrides(address='testing')
        self.assertEqual(config.address, 'testing')
        self.assertIsNone(config.api_token)
        self.assertIsNone(config.secure)

    def test_init_without_address(self):
        config = SitePlannerEnvironmentOverrides()
        self.assertIsNone(config.address)
        self.assertIsNone(config.api_token)
        self.assertIsNone(config.secure)

    def test_api_token(self):
        config = SitePlannerEnvironmentOverrides(address='testing', api_token='123')
        self.assertEqual(config.address, 'testing')
        self.assertEqual(config.api_token, '123')

    def test_secure(self):
        config = SitePlannerEnvironmentOverrides(secure=False)
        self.assertFalse(config.secure)
