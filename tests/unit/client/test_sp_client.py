import unittest
from lmctl.client import SitePlannerClient

class TestSitePlannerClient(unittest.TestCase):

    def test_address_with_trailing_slash_is_trimmed(self):
        client = SitePlannerClient('https://test.example.com/')
        self.assertEqual(client.address, 'https://test.example.com')