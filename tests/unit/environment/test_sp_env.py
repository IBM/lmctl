import unittest
from pydantic import ValidationError
from lmctl.environment import SitePlannerEnvironment, SitePlannerClient

class TestSitePlannerEnvironment(unittest.TestCase):
    maxDiff = None

    def test_minimum_init(self):
        config = SitePlannerEnvironment(address='testing')
        self.assertEqual(config.address, 'testing')
        self.assertIsNone(config.api_token)

    def test_init_fails_when_address_is_none(self):
        with self.assertRaises(TypeError) as context:
            config = SitePlannerEnvironment()
        self.assertEqual(str(context.exception), '__init__() missing 1 required positional argument: \'address\'')
        with self.assertRaises(ValidationError) as context:
            config = SitePlannerEnvironment(address=' ')
        self.assertEqual(str(context.exception), '1 validation error for SitePlannerEnvironment\naddress\n  ensure this value has at least 1 characters (type=value_error.any_str.min_length; limit_value=1)')

    def test_api_token(self):
        config = SitePlannerEnvironment(address='testing', api_token='123')
        self.assertEqual(config.address, 'testing')
        self.assertEqual(config.api_token, '123')
    
    def test_build_client(self):
        config = SitePlannerEnvironment(address='testing', api_token='123')
        client = config.build_client()
        self.assertIsInstance(client, SitePlannerClient)
        self.assertEqual(client.address, 'testing')
        self.assertEqual(client.api_token, '123')

    def test_build_client_without_token(self):
        config = SitePlannerEnvironment(address='testing')
        client = config.build_client()
        self.assertIsInstance(client, SitePlannerClient)
        self.assertEqual(client.address, 'testing')
        self.assertIsNone(client.api_token)

    
