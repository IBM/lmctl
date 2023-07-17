import unittest
import unittest.mock as mock
import os
from pydantic import ValidationError
from lmctl.environment import (
    TNCOEnvironment, LmSession, ALLOW_ALL_SCHEMES_ENV_VAR, NO_AUTH_MODE, 
    TOKEN_AUTH_MODE, CP_API_KEY_AUTH_MODE, ZEN_AUTH_MODE,
    OAUTH_MODE, OAUTH_LEGACY_USER_MODE, OAUTH_USER_MODE, OAUTH_CLIENT_MODE,
    OKTA_CLIENT_MODE, OKTA_MODE, OKTA_USER_MODE)
from lmctl.client import TNCOClient, LegacyUserPassAuth, UserPassAuth, ClientCredentialsAuth, JwtTokenAuth, ZenAPIKeyAuth, OktaUserPassAuth, OktaClientCredentialsAuth

class TestTNCOEnvironment(unittest.TestCase):
    maxDiff = None

    ## init behaviour tests ##

    def test_init_secure_prop(self):
        # "secure" to be deprecated. Check "auth_mode" and "secure" play nicely in the interm
        env = TNCOEnvironment(address='testing')
        self.assertFalse(env.secure, False)
        self.assertEqual(env.auth_mode, NO_AUTH_MODE)

        env = TNCOEnvironment(address='testing', secure=True)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OAUTH_MODE)

        env = TNCOEnvironment(address='testing', auth_mode=NO_AUTH_MODE)
        self.assertFalse(env.secure, False)
        self.assertEqual(env.auth_mode, NO_AUTH_MODE)

        # Secure=True overwrites NO_AUTH_MODE
        env = TNCOEnvironment(address='testing', secure=True, auth_mode=NO_AUTH_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OAUTH_MODE)

        # Secure=True makes no change to other auth modes
        env = TNCOEnvironment(address='testing', secure=True, auth_mode=TOKEN_AUTH_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, TOKEN_AUTH_MODE)
        env = TNCOEnvironment(address='testing', secure=True, auth_mode=CP_API_KEY_AUTH_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, CP_API_KEY_AUTH_MODE)
        env = TNCOEnvironment(address='testing', secure=True, auth_mode=ZEN_AUTH_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, ZEN_AUTH_MODE)
        env = TNCOEnvironment(address='testing', secure=True, auth_mode=OAUTH_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OAUTH_MODE)
        env = TNCOEnvironment(address='testing', secure=True, auth_mode=OAUTH_CLIENT_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OAUTH_CLIENT_MODE)
        env = TNCOEnvironment(address='testing', secure=True, auth_mode=OAUTH_USER_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OAUTH_USER_MODE)
        env = TNCOEnvironment(address='testing', secure=True, auth_mode=OAUTH_LEGACY_USER_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OAUTH_LEGACY_USER_MODE)
        env = TNCOEnvironment(address='testing', secure=True, auth_mode=OKTA_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OKTA_MODE)
        env = TNCOEnvironment(address='testing', secure=True, auth_mode=OKTA_CLIENT_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OKTA_CLIENT_MODE)
        env = TNCOEnvironment(address='testing', secure=True, auth_mode=OKTA_USER_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OKTA_USER_MODE)

        # Secure=False keeps NO_AUTH_MODE
        env = TNCOEnvironment(address='testing', secure=False, auth_mode=NO_AUTH_MODE)
        self.assertFalse(env.secure)
        self.assertEqual(env.auth_mode, NO_AUTH_MODE)

        # Secure=False becomes True for other auth modes
        env = TNCOEnvironment(address='testing', secure=False, auth_mode=TOKEN_AUTH_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, TOKEN_AUTH_MODE)
        env = TNCOEnvironment(address='testing', secure=False, auth_mode=CP_API_KEY_AUTH_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, CP_API_KEY_AUTH_MODE)
        env = TNCOEnvironment(address='testing', secure=False, auth_mode=ZEN_AUTH_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, ZEN_AUTH_MODE)
        env = TNCOEnvironment(address='testing', secure=False, auth_mode=OAUTH_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OAUTH_MODE)
        env = TNCOEnvironment(address='testing', secure=False, auth_mode=OAUTH_CLIENT_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OAUTH_CLIENT_MODE)
        env = TNCOEnvironment(address='testing', secure=False, auth_mode=OAUTH_USER_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OAUTH_USER_MODE)
        env = TNCOEnvironment(address='testing', secure=False, auth_mode=OAUTH_LEGACY_USER_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OAUTH_LEGACY_USER_MODE)
        env = TNCOEnvironment(address='testing', secure=False, auth_mode=OKTA_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OKTA_MODE)
        env = TNCOEnvironment(address='testing', secure=False, auth_mode=OKTA_CLIENT_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OKTA_CLIENT_MODE)
        env = TNCOEnvironment(address='testing', secure=False, auth_mode=OKTA_USER_MODE)
        self.assertTrue(env.secure)
        self.assertEqual(env.auth_mode, OKTA_USER_MODE)

    def test_minimum_init(self):
        env = TNCOEnvironment(address='testing')
        self.assertEqual(env.address, 'testing')
        self.assertEqual(env.secure, False)
        # Defaults
        self.assertEqual(env.auth_mode, NO_AUTH_MODE)
        self.assertEqual(env.brent_name, 'brent')
        self.assertEqual(env.protocol, 'https')
        self.assertEqual(env.auth_protocol, 'https')
        self.assertEqual(env.kami_port, '31289')
        self.assertEqual(env.kami_protocol, 'http')

    def test_init_auth_mode_with_none_means_no_auth(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=None)
        self.assertIsNone(env.auth_mode)
        
    def test_init_fails_when_address_and_host_are_none(self):
        with self.assertRaises(ValidationError) as context:
            env = TNCOEnvironment()
            env.validate()
        self.assertEqual(str(context.exception), '1 validation error for TNCOEnvironment\n__root__\n  Invalid CP4NA environment - must specify "address" or "host" property (type=value_error)')

    def test_init_with_secure_and_credentials_not_set(self):
        env = TNCOEnvironment(address='testing.example.com', secure=True)
        # Changed by issue/187 - this is now allowed on construction, only fails when validate is called
        self.assertEqual(env.auth_mode, OAUTH_MODE)
        self.assertIsNone(env.username)
        self.assertIsNone(env.client_id)

    def test_init_with_addresses_as_parts(self):
        env = TNCOEnvironment(host='testing.example.com', port=4567, protocol='https', path='gateway', secure=True, username='user', password='secret', auth_host='auth.example.com', auth_port=81, auth_protocol='https')
        
        self.assertEqual(env.address, 'https://testing.example.com:4567/gateway')
        self.assertEqual(env.auth_address, 'https://auth.example.com:81')
        self.assertEqual(env.get_usable_address(), 'https://testing.example.com:4567/gateway')
        self.assertEqual(env.get_usable_oauth_legacy_user_address(), 'https://auth.example.com:81')

    def test_init_address_from_parts(self):
        env = TNCOEnvironment(host='testing.example.com')
        self.assertEqual(env.address, 'https://testing.example.com')
        env = TNCOEnvironment(host='testing.example.com', port=32455)
        self.assertEqual(env.address, 'https://testing.example.com:32455')
        env = TNCOEnvironment(host='testing.example.com', port=32455, protocol='https')
        self.assertEqual(env.address, 'https://testing.example.com:32455')
        env = TNCOEnvironment(host='testing.example.com', port=None, protocol='https')
        self.assertEqual(env.address, 'https://testing.example.com')
        env = TNCOEnvironment(host='testing.example.com', port=None, protocol='https', path='gateway')
        self.assertEqual(env.address, 'https://testing.example.com/gateway')
        env = TNCOEnvironment(host='testing.example.com', port=32455, protocol='https', path='gateway')
        self.assertEqual(env.address, 'https://testing.example.com:32455/gateway')

    def test_init_auth_address_from_parts(self):
        env = TNCOEnvironment(address='testing.example.com', username='user', auth_mode=OAUTH_LEGACY_USER_MODE,
                              auth_host='auth.example.com')
        self.assertEqual(env.auth_address, 'https://auth.example.com')

        env = TNCOEnvironment(address='testing.example.com', username='user', auth_mode=OAUTH_LEGACY_USER_MODE,
                              auth_host='auth.example.com', auth_port=3423)
        self.assertEqual(env.auth_address, 'https://auth.example.com:3423')

        env = TNCOEnvironment(address='testing.example.com', username='user', auth_mode=OAUTH_LEGACY_USER_MODE,
                              auth_host='auth.example.com', auth_port=3423, auth_protocol='https')
        self.assertEqual(env.auth_address, 'https://auth.example.com:3423')

        env = TNCOEnvironment(address='testing.example.com', username='user', auth_mode=OAUTH_LEGACY_USER_MODE,
                              auth_host='auth.example.com', auth_port=None, auth_protocol='https')
        self.assertEqual(env.auth_address, 'https://auth.example.com')

    def test_init_kami_address_from_parts(self):
        env = TNCOEnvironment(host='test', port=80, protocol='https', secure=True, username='user', auth_host='auth', auth_port=82, auth_protocol='https')
        self.assertEqual(env.kami_address, 'http://test:31289')

    def test_init_kami_address_override_port(self):
        env = TNCOEnvironment(address='https://testing.example.com:80', kami_port=5678)
        self.assertEqual(env.kami_address, 'http://testing.example.com:5678')

    def test_init_kami_address_override_protocol(self):
        env = TNCOEnvironment(address='https://testing.example.com:80', kami_protocol='https')
        self.assertEqual(env.kami_address, 'https://testing.example.com:31289')

    ## http vs https tests ##

    def test_use_of_http_address_fails(self):
        with self.assertRaises(ValueError) as ctx:
            TNCOEnvironment(address='http://cp4na-o-ishtar.example.com').build_client()
        self.assertEqual(str(ctx.exception), 'Use of "http" scheme is not encouraged by lmctl, use "https" instead (http://cp4na-o-ishtar.example.com)')
       
        with self.assertRaises(ValueError) as ctx:
            TNCOEnvironment(host='cp4na-o-ishtar.example.com', protocol='http').build_client()
        self.assertEqual(str(ctx.exception), 'Use of "http" scheme is not encouraged by lmctl, use "https" instead (http://cp4na-o-ishtar.example.com)')
    
    def test_use_of_http_auth_address_fails(self):
        with self.assertRaises(ValueError) as ctx:
            TNCOEnvironment(address='https://cp4na-o-ishtar.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, auth_address='http://cp4na-o-auth.example.com', username='test').build_client()
        self.assertEqual(str(ctx.exception), 'Use of "http" scheme is not encouraged by lmctl, use "https" instead (http://cp4na-o-auth.example.com)')
        
        with self.assertRaises(ValueError) as ctx:
            TNCOEnvironment(host='cp4na-o-ishtar.example.com', port=80, protocol='https', auth_mode=OAUTH_LEGACY_USER_MODE, auth_host='cp4na-o-auth.example.com', auth_protocol='http', username='test').build_client()
        self.assertEqual(str(ctx.exception), 'Use of "http" scheme is not encouraged by lmctl, use "https" instead (http://cp4na-o-auth.example.com)')
    
    def test_use_of_http_cp_front_door_address_fails(self):
        with self.assertRaises(ValueError) as ctx:
            TNCOEnvironment(address='https://cp4na-o-ishtar.example.com', auth_mode=CP_API_KEY_AUTH_MODE, cp_front_door_address='http://cp4na-o-auth.example.com', username='test').build_client()
        self.assertEqual(str(ctx.exception), 'Use of "http" scheme is not encouraged by lmctl, use "https" instead (http://cp4na-o-auth.example.com)')

    def test_use_of_http_address_allowed_when_env_var_set(self):
        previous_env_var_value = os.environ.get(ALLOW_ALL_SCHEMES_ENV_VAR, '')
        os.environ[ALLOW_ALL_SCHEMES_ENV_VAR] = 'true'
        try:
            env = TNCOEnvironment(address='http://cp4na-o-ishtar.example.com')
            self.assertEqual(env.address, 'http://cp4na-o-ishtar.example.com')
            client = env.build_client()
            self.assertEqual(client.address, 'http://cp4na-o-ishtar.example.com')
            
            env = TNCOEnvironment(host='cp4na-o-ishtar.example.com', protocol='http')
            self.assertEqual(env.address, 'http://cp4na-o-ishtar.example.com')
            client = env.build_client()
            self.assertEqual(client.address, 'http://cp4na-o-ishtar.example.com')
        finally:
            os.environ[ALLOW_ALL_SCHEMES_ENV_VAR] = previous_env_var_value

    def test_use_of_http_auth_address_allowed_when_env_var_set(self):
        previous_env_var_value = os.environ.get(ALLOW_ALL_SCHEMES_ENV_VAR, '')
        os.environ[ALLOW_ALL_SCHEMES_ENV_VAR] = 'true'
        try:
            env = TNCOEnvironment(address='https://cp4na-o-ishtar.example.com', auth_address='http://cp4na-o-auth.example.com', 
                                  auth_mode=OAUTH_LEGACY_USER_MODE, username='test')
            self.assertEqual(env.auth_address, 'http://cp4na-o-auth.example.com')
            client = env.build_client()
            self.assertEqual(client.auth_type.legacy_auth_address, 'http://cp4na-o-auth.example.com')
            
            env = TNCOEnvironment(address='https://cp4na-o-ishtar.example.com', auth_host='cp4na-o-auth.example.com', auth_protocol='http',
                                  auth_mode=OAUTH_LEGACY_USER_MODE, username='test')
            self.assertEqual(env.auth_address, 'http://cp4na-o-auth.example.com')
            client = env.build_client()
            self.assertEqual(client.auth_type.legacy_auth_address, 'http://cp4na-o-auth.example.com')
        finally:
            os.environ[ALLOW_ALL_SCHEMES_ENV_VAR] = previous_env_var_value

    def test_use_of_http_cp_front_door_address_allowed_when_env_var_set(self):
        previous_env_var_value = os.environ.get(ALLOW_ALL_SCHEMES_ENV_VAR, '')
        os.environ[ALLOW_ALL_SCHEMES_ENV_VAR] = 'true'
        try:
            env = TNCOEnvironment(address='https://cp4na-o-ishtar.example.com', cp_front_door_address='http://cp4na-o-auth.example.com', 
                                  auth_mode=CP_API_KEY_AUTH_MODE, username='test')
            self.assertEqual(env.cp_front_door_address, 'http://cp4na-o-auth.example.com')
            client = env.build_client()
            self.assertEqual(client.auth_type.zen_auth_address, 'http://cp4na-o-auth.example.com')
        finally:
            os.environ[ALLOW_ALL_SCHEMES_ENV_VAR] = previous_env_var_value

    ## Validate Tests
    def test_validate_oauth_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_MODE, client_id='client', client_secret='secret')
        self.assertEqual(env.auth_mode, OAUTH_MODE)
        self.assertEqual(env.client_id, 'client')
        self.assertEqual(env.client_secret, 'secret')
        env.validate()

    def test_validate_oauth_mode_without_client_id_or_username_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_MODE).validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "username" or "client_id" when using "auth_mode=oauth"')

    def test_validate_oauth_client_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_CLIENT_MODE, client_id='client', client_secret='secret')
        self.assertEqual(env.auth_mode, OAUTH_CLIENT_MODE)
        self.assertEqual(env.client_id, 'client')
        self.assertEqual(env.client_secret, 'secret')
        env.validate()

    def test_validate_oauth_client_mode_without_client_secret(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_CLIENT_MODE, client_id='client')
        self.assertEqual(env.auth_mode, OAUTH_CLIENT_MODE)
        self.assertEqual(env.client_id, 'client')
        self.assertIsNone(env.client_secret)
        env.validate()

    def test_validate_oauth_client_mode_without_client_id_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_CLIENT_MODE).validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "client_id" when using "auth_mode=client-credentials"')

    def test_validate_oauth_user_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_USER_MODE, username='test', password='pass', client_id='client', client_secret='secret')
        self.assertEqual(env.auth_mode, OAUTH_USER_MODE)
        self.assertEqual(env.username, 'test')
        self.assertEqual(env.password, 'pass')
        self.assertEqual(env.client_id, 'client')
        self.assertEqual(env.client_secret, 'secret')
        env.validate()

    def test_validate_oauth_user_mode_without_password(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_USER_MODE, username='test', client_id='client', client_secret='secret')
        self.assertEqual(env.auth_mode, OAUTH_USER_MODE)
        self.assertEqual(env.username, 'test')
        self.assertIsNone(env.password)
        self.assertEqual(env.client_id, 'client')
        self.assertEqual(env.client_secret, 'secret')
        env.validate()

    def test_validate_oauth_user_mode_without_client_secret(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_USER_MODE, username='test', password='pass', client_id='client')
        self.assertEqual(env.auth_mode, OAUTH_USER_MODE)
        self.assertEqual(env.username, 'test')
        self.assertEqual(env.password, 'pass')
        self.assertEqual(env.client_id, 'client')
        self.assertIsNone(env.client_secret)
        env.validate()

    def test_validate_oauth_user_mode_without_client_secret_or_password(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_USER_MODE, username='test', client_id='client')
        self.assertEqual(env.auth_mode, OAUTH_USER_MODE)
        self.assertEqual(env.username, 'test')
        self.assertIsNone(env.password)
        self.assertEqual(env.client_id, 'client')
        self.assertIsNone(env.client_secret)
        env.validate()

    def test_validate_oauth_user_mode_without_username_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_USER_MODE, client_id='client').validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "username" when using "auth_mode=user"')

    def test_validate_oauth_user_mode_without_client_id_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_USER_MODE, username='test').validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "client_id" when using "auth_mode=user"')

    def test_validate_oauth_legacy_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='test', password='secret')
        self.assertEqual(env.auth_mode, OAUTH_LEGACY_USER_MODE)
        self.assertEqual(env.username, 'test')
        self.assertEqual(env.password, 'secret')
        env.validate()

    def test_validate_oauth_legacy_mode_without_password(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='test')
        self.assertEqual(env.auth_mode, OAUTH_LEGACY_USER_MODE)
        self.assertEqual(env.username, 'test')
        self.assertIsNone(env.password)
        env.validate()

    def test_validate_oauth_legacy_mode_without_username_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE).validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "username" when using "auth_mode=user-login"')

    def test_validate_oauth_legacy_without_auth_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='test')
        env.validate()
        self.assertIsNone(env.auth_address)
        self.assertIsNone(env.get_usable_oauth_legacy_user_address())

    def test_validate_zen_auth_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, username='Zenny', api_key='12345', auth_address='zen.example.com/auth')
        self.assertEqual(env.auth_mode, ZEN_AUTH_MODE)
        self.assertEqual(env.username, 'Zenny')
        self.assertEqual(env.api_key, '12345')
        self.assertEqual(env.auth_address, 'zen.example.com/auth')
        env.validate()

    def test_validate_zen_auth_mode_without_api_key(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, username='Zenny', auth_address='zen.example.com/auth')
        self.assertEqual(env.auth_mode, ZEN_AUTH_MODE)
        self.assertEqual(env.username, 'Zenny')
        self.assertIsNone(env.api_key)
        self.assertEqual(env.auth_address, 'zen.example.com/auth')
        env.validate()

    def test_validate_zen_auth_without_username_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE).validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "username" when using "auth_mode=zen"')

    def test_validate_zen_auth_without_auth_address_or_cp_front_door_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, username='test')
        env.validate()
        self.assertIsNone(env.auth_address)
        self.assertIsNone(env.cp_front_door_address)
        self.assertIsNone(env.get_usable_cp_front_door_address())

    def test_validate_zen_auth_with_cp_front_door_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, username='test', cp_front_door_address='auth.example.com')
        env.validate()
        self.assertIsNone(env.auth_address)
        self.assertEqual(env.cp_front_door_address, 'auth.example.com')
        self.assertEqual(env.get_usable_cp_front_door_address(), 'https://auth.example.com')

    def test_validate_zen_auth_with_auth_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, username='test', auth_address='auth.example.com')
        env.validate()
        self.assertIsNone(env.cp_front_door_address)
        self.assertEqual(env.auth_address, 'auth.example.com')
        self.assertIsNone(env.get_usable_cp_front_door_address())

    def test_validate_cp_api_key_auth_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, username='Zenny', api_key='12345', auth_address='zen.example.com/auth')
        self.assertEqual(env.auth_mode, CP_API_KEY_AUTH_MODE)
        self.assertEqual(env.username, 'Zenny')
        self.assertEqual(env.api_key, '12345')
        self.assertEqual(env.auth_address, 'zen.example.com/auth')
        env.validate()

    def test_validate_cp_api_key_auth_mode_without_api_key(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, username='Zenny', auth_address='zen.example.com/auth')
        self.assertEqual(env.auth_mode, CP_API_KEY_AUTH_MODE)
        self.assertEqual(env.username, 'Zenny')
        self.assertIsNone(env.api_key)
        self.assertEqual(env.auth_address, 'zen.example.com/auth')
        env.validate()

    def test_validate_cp_api_key_auth_without_username_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE).validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "username" when using "auth_mode=cp-api-key"')

    def test_validate_cp_api_key_auth_without_auth_address_or_cp_front_door_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, username='test')
        env.validate()
        self.assertIsNone(env.auth_address)
        self.assertIsNone(env.cp_front_door_address)
        self.assertIsNone(env.get_usable_cp_front_door_address())

    def test_validate_cp_api_key_auth_with_cp_front_door_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, username='test', cp_front_door_address='auth.example.com')
        env.validate()
        self.assertIsNone(env.auth_address)
        self.assertEqual(env.cp_front_door_address, 'auth.example.com')
        self.assertEqual(env.get_usable_cp_front_door_address(), 'https://auth.example.com')

    def test_validate_cp_api_key_auth_with_auth_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, username='test', auth_address='auth.example.com')
        env.validate()
        self.assertIsNone(env.cp_front_door_address)
        self.assertEqual(env.auth_address, 'auth.example.com')
        self.assertIsNone(env.get_usable_cp_front_door_address())

    def test_validate_token_auth(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=TOKEN_AUTH_MODE, token='123')
        env.validate()
        self.assertEqual(env.auth_mode, TOKEN_AUTH_MODE)
        self.assertEqual(env.token, '123')

    def test_validate_token_auth_without_token_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=TOKEN_AUTH_MODE).validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "token" when using "auth_mode=token"')
    
    def test_validate_token_auth_without_token_set_allow_no_token(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=TOKEN_AUTH_MODE)
        env.validate(allow_no_token=True)
        self.assertEqual(env.auth_mode, TOKEN_AUTH_MODE)
        self.assertIsNone(env.token)

    def test_validate_okta_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_MODE, client_id='client', client_secret='secret', auth_server_id='server', scope='test')
        self.assertEqual(env.auth_mode, OKTA_MODE)
        self.assertEqual(env.client_id, 'client')
        self.assertEqual(env.client_secret, 'secret')
        self.assertEqual(env.auth_server_id, 'server')
        self.assertEqual(env.scope, 'test')
        env.validate()

    def test_validate_okta_mode_without_client_id_or_username_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_MODE, auth_server_id='server', scope='test').validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "username" and/or "client_id" when using "auth_mode=okta"')

    def test_validate_okta_client_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_CLIENT_MODE, client_id='client', client_secret='secret', auth_server_id='server', scope='test')
        self.assertEqual(env.auth_mode, OKTA_CLIENT_MODE)
        self.assertEqual(env.client_id, 'client')
        self.assertEqual(env.client_secret, 'secret')
        env.validate()

    def test_validate_okta_client_mode_without_client_secret(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_CLIENT_MODE, client_id='client', auth_server_id='server', scope='test')
        self.assertEqual(env.auth_mode, OKTA_CLIENT_MODE)
        self.assertEqual(env.client_id, 'client')
        self.assertIsNone(env.client_secret)
        self.assertEqual(env.auth_server_id, 'server')
        self.assertEqual(env.scope, 'test')
        env.validate()

    def test_validate_okta_client_mode_without_client_id_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_CLIENT_MODE, auth_server_id='server', scope='test').validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "client_id" when using "auth_mode=okta-client"')

    def test_validate_okta_user_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, username='test', password='pass', client_id='client', client_secret='secret', auth_server_id='server', scope='test')
        self.assertEqual(env.auth_mode, OKTA_USER_MODE)
        self.assertEqual(env.username, 'test')
        self.assertEqual(env.password, 'pass')
        self.assertEqual(env.client_id, 'client')
        self.assertEqual(env.client_secret, 'secret')
        self.assertEqual(env.auth_server_id, 'server')
        self.assertEqual(env.scope, 'test')
        env.validate()

    def test_validate_okta_user_mode_without_password(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, username='test', client_id='client', client_secret='secret', auth_server_id='server', scope='test')
        self.assertEqual(env.auth_mode, OKTA_USER_MODE)
        self.assertEqual(env.username, 'test')
        self.assertIsNone(env.password)
        self.assertEqual(env.client_id, 'client')
        self.assertEqual(env.client_secret, 'secret')
        self.assertEqual(env.auth_server_id, 'server')
        self.assertEqual(env.scope, 'test')
        env.validate()

    def test_validate_okta_user_mode_without_client_secret(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, username='test', password='pass', client_id='client', auth_server_id='server', scope='test')
        self.assertEqual(env.auth_mode, OKTA_USER_MODE)
        self.assertEqual(env.username, 'test')
        self.assertEqual(env.password, 'pass')
        self.assertEqual(env.client_id, 'client')
        self.assertIsNone(env.client_secret)
        self.assertEqual(env.auth_server_id, 'server')
        self.assertEqual(env.scope, 'test')
        env.validate()

    def test_validate_okta_user_mode_without_client_secret_or_password(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, username='test', client_id='client', auth_server_id='server', scope='test')
        self.assertEqual(env.auth_mode, OKTA_USER_MODE)
        self.assertEqual(env.username, 'test')
        self.assertIsNone(env.password)
        self.assertEqual(env.client_id, 'client')
        self.assertIsNone(env.client_secret)
        self.assertEqual(env.auth_server_id, 'server')
        self.assertEqual(env.scope, 'test')
        env.validate()

    def test_validate_okta_user_mode_without_username_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, client_id='client', auth_server_id='server', scope='test').validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "username" when using "auth_mode=okta-user"')

    def test_validate_okta_user_mode_without_client_id_fails(self):
        with self.assertRaises(ValueError) as context:
            TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, username='test', auth_server_id='server', scope='test').validate()
        self.assertEqual(str(context.exception), 'Invalid CP4NA environment - must configure "client_id" when using "auth_mode=okta-user"')

    ## build_client tests ##

    def test_build_client_sets_full_address(self):
        env = TNCOEnvironment(address='testing.example.com')
        client = env.build_client()
        self.assertIsInstance(client, TNCOClient)
        self.assertEqual(client.address, 'https://testing.example.com')
        self.assertEqual(client.kami_address, 'http://testing.example.com:31289')

    def test_build_client_with_address_already_containing_protocol(self):
        env = TNCOEnvironment(address='https://testing.example.com')
        client = env.build_client()
        self.assertEqual(client.address, 'https://testing.example.com')

    def test_build_client_with_no_auth(self):
        env = TNCOEnvironment(address='testing.example.com')
        client = env.build_client()
        self.assertIsNone(client.auth_type)

        env = TNCOEnvironment(address='testing.example.com', auth_mode=NO_AUTH_MODE)
        client = env.build_client()
        self.assertIsNone(client.auth_type)

    def test_build_client_with_secure_false_uses_no_auth(self):
        env = TNCOEnvironment(address='testing.example.com', secure=False)
        client = env.build_client()
        self.assertIsNone(client.auth_type)

    def test_build_client_with_oauth_mode_and_username_uses_legacy_auth(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_MODE, username='user', password='secret', auth_address='auth.example.com')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, LegacyUserPassAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.password, 'secret')
        self.assertEqual(client.auth_type.legacy_auth_address, 'https://auth.example.com')

    def test_build_client_with_oauth_mode_with_auth_address_already_containing_protocol(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_MODE, username='user', password='secret', auth_address='https://auth.example.com')
        client = env.build_client()
        self.assertEqual(client.auth_type.legacy_auth_address, 'https://auth.example.com')

    def test_build_client_with_oauth_mode_and_username_without_auth_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_MODE, username='user', password='secret')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, LegacyUserPassAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.password, 'secret')
        self.assertIsNone(client.auth_type.legacy_auth_address)

    def test_build_client_with_oauth_mode_and_username_and_client_id_uses_user_auth(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_MODE, username='user', password='pass', client_id='client', client_secret='secret')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, UserPassAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.password, 'pass')
        self.assertEqual(client.auth_type.client_id, 'client')
        self.assertEqual(client.auth_type.client_secret, 'secret')

    def test_build_client_with_oauth_mode_and_client_id_uses_client_auth(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_MODE, client_id='client', client_secret='secret')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, ClientCredentialsAuth)
        self.assertEqual(client.auth_type.client_id, 'client')
        self.assertEqual(client.auth_type.client_secret, 'secret')

    def test_build_client_with_oauth_mode_without_username_or_client_id_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_MODE, password='pass', client_secret='secret')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "username" or "client_id" when using "auth_mode=oauth"')

    def test_build_client_with_oauth_user_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_USER_MODE, username='user', password='pass', client_id='client', client_secret='secret')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, UserPassAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.password, 'pass')
        self.assertEqual(client.auth_type.client_id, 'client')
        self.assertEqual(client.auth_type.client_secret, 'secret')

    def test_build_client_with_oauth_user_mode_without_username_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_USER_MODE, password='pass', client_id='client', client_secret='secret')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "username" when using "auth_mode=user"')

    def test_build_client_with_oauth_user_mode_without_client_id_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_USER_MODE, username='user', password='pass', client_secret='secret')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "client_id" when using "auth_mode=user"')

    def test_build_client_with_oauth_client_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_CLIENT_MODE, client_id='client', client_secret='secret')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, ClientCredentialsAuth)
        self.assertEqual(client.auth_type.client_id, 'client')
        self.assertEqual(client.auth_type.client_secret, 'secret')

    def test_build_client_with_oauth_client_mode_without_client_id_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_CLIENT_MODE, client_secret='secret')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "client_id" when using "auth_mode=client-credentials"')

    def test_build_client_with_oauth_legacy_user_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='user', password='pass', auth_address='auth.example.com')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, LegacyUserPassAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.password, 'pass')
        self.assertEqual(client.auth_type.legacy_auth_address, 'https://auth.example.com')

    def test_build_client_with_oauth_legacy_user_mode_without_auth_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='user', password='secret')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, LegacyUserPassAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.password, 'secret')
        self.assertIsNone(client.auth_type.legacy_auth_address)

    def test_build_client_with_oauth_legacy_user_mode_without_username_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, password='pass')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "username" when using "auth_mode=user-login"')

    def test_build_client_with_okta_mode_and_username_and_client_id_uses_okta_user_auth(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_MODE,
                                  username='user', password='pass', client_id='client', client_secret='secret', 
                                  auth_server_id='server', scope='scope', auth_address='auth.example.com')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, OktaUserPassAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.password, 'pass')
        self.assertEqual(client.auth_type.client_id, 'client')
        self.assertEqual(client.auth_type.client_secret, 'secret')
        self.assertEqual(client.auth_type.auth_server_id, 'server')
        self.assertEqual(client.auth_type.scope, 'scope')
        self.assertEqual(client.auth_type.okta_server, 'https://auth.example.com')

    def test_build_client_with_okta_mode_and_client_id_uses_okta_client_auth(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_MODE, 
                                 client_id='client', client_secret='secret', 
                                  auth_server_id='server', scope='scope', auth_address='auth.example.com')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, OktaClientCredentialsAuth)
        self.assertEqual(client.auth_type.client_id, 'client')
        self.assertEqual(client.auth_type.client_secret, 'secret')
        self.assertEqual(client.auth_type.auth_server_id, 'server')
        self.assertEqual(client.auth_type.scope, 'scope')
        self.assertEqual(client.auth_type.okta_server, 'https://auth.example.com')

    def test_build_client_with_okta_mode_with_auth_address_already_containing_protocol(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_MODE,
                                  username='user', password='pass', client_id='client', client_secret='secret', 
                                  auth_server_id='server', scope='scope', auth_address='https://auth.example.com')
        client = env.build_client()
        self.assertEqual(client.auth_type.okta_server, 'https://auth.example.com')

    def test_build_client_with_okta_mode_without_auth_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_MODE,
                                  username='user', password='pass', client_id='client', client_secret='secret', 
                                  auth_server_id='server', scope='scope')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, OktaUserPassAuth)
        self.assertIsNone(client.auth_type.okta_server)

    def test_build_client_with_okta_mode_without_username_or_client_id_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_MODE, password='pass', client_secret='secret')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "username" and/or "client_id" when using "auth_mode=okta"')

    def test_build_client_with_okta_mode_without_scope_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_MODE, 
                                 username='user', password='pass', client_id='client', client_secret='secret',
                                 auth_server_id='server', auth_address='auth.example.com')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "scope" when using "auth_mode=okta-user"')

    def test_build_client_with_okta_mode_without_server_id_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_MODE, 
                                 username='user', password='pass', client_id='client', client_secret='secret',
                                 scope='scope', auth_address='auth.example.com')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "auth_server_id" when using "auth_mode=okta-user"')

    def test_build_client_with_okta_user_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, 
                                 username='user', password='pass', client_id='client', client_secret='secret',
                                 auth_server_id='server', scope='scope', auth_address='auth.example.com')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, OktaUserPassAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.password, 'pass')
        self.assertEqual(client.auth_type.client_id, 'client')
        self.assertEqual(client.auth_type.client_secret, 'secret')
        self.assertEqual(client.auth_type.auth_server_id, 'server')
        self.assertEqual(client.auth_type.scope, 'scope')
        self.assertEqual(client.auth_type.okta_server, 'https://auth.example.com')

    def test_build_client_with_okta_user_mode_with_auth_address_already_containing_protocol(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, 
                                 username='user', password='pass', client_id='client', client_secret='secret',
                                 auth_server_id='server', scope='scope', auth_address='https://auth.example.com')
        client = env.build_client()
        self.assertEqual(client.auth_type.okta_server, 'https://auth.example.com')
        
    def test_build_client_with_okta_user_mode_without_username_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, 
                                 password='pass', client_id='client', client_secret='secret',
                                 auth_server_id='server', scope='scope', auth_address='auth.example.com')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "username" when using "auth_mode=okta-user"')

    def test_build_client_with_okta_user_mode_without_client_id_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, 
                                 username='user', password='pass', client_secret='secret',
                                 auth_server_id='server', scope='scope', auth_address='auth.example.com')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "client_id" when using "auth_mode=okta-user"')

    def test_build_client_with_okta_user_mode_without_auth_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE,
                                  username='user', password='pass', client_id='client', client_secret='secret', 
                                  auth_server_id='server', scope='scope')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, OktaUserPassAuth)
        self.assertIsNone(client.auth_type.okta_server)

    def test_build_client_with_okta_user_mode_without_scope_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, 
                                 username='user', password='pass', client_id='client', client_secret='secret',
                                 auth_server_id='server', auth_address='auth.example.com')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "scope" when using "auth_mode=okta-user"')

    def test_build_client_with_okta_user_mode_without_server_id_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, 
                                 username='user', password='pass', client_id='client', client_secret='secret',
                                 scope='scope', auth_address='auth.example.com')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "auth_server_id" when using "auth_mode=okta-user"')

    def test_build_client_with_okta_client_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_CLIENT_MODE, 
                                 client_id='client', client_secret='secret',
                                 auth_server_id='server', scope='scope', auth_address='auth.example.com')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, OktaClientCredentialsAuth)
        self.assertEqual(client.auth_type.client_id, 'client')
        self.assertEqual(client.auth_type.client_secret, 'secret')
        self.assertEqual(client.auth_type.auth_server_id, 'server')
        self.assertEqual(client.auth_type.scope, 'scope')
        self.assertEqual(client.auth_type.okta_server, 'https://auth.example.com')

    def test_build_client_with_okta_client_mode_with_auth_address_already_containing_protocol(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_CLIENT_MODE, 
                                 client_id='client', client_secret='secret',
                                 auth_server_id='server', scope='test', auth_address='https://auth.example.com')
        client = env.build_client()
        self.assertEqual(client.auth_type.okta_server, 'https://auth.example.com')

    def test_build_client_with_okta_client_mode_without_client_id_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_CLIENT_MODE, 
                                 client_secret='secret', auth_server_id='server', auth_address='auth.example.com')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "client_id" when using "auth_mode=okta-client"')

    def test_build_client_with_okta_client_mode_without_scope_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_CLIENT_MODE, 
                                 client_id='client', client_secret='secret',
                                 auth_server_id='server', auth_address='auth.example.com')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "scope" when using "auth_mode=okta-client"')

    def test_build_client_with_okta_client_mode_without_server_id_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_CLIENT_MODE, 
                                 client_id='client', client_secret='secret',
                                 scope='scope', auth_address='auth.example.com')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "auth_server_id" when using "auth_mode=okta-client"')

    def test_build_client_with_zen_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, username='user', api_key='123', cp_front_door_address='auth.example.com')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, ZenAPIKeyAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.api_key, '123')
        self.assertEqual(client.auth_type.zen_auth_address, 'https://auth.example.com')
        self.assertIsNone(client.auth_type.override_auth_endpoint)
    
    def test_build_client_with_zen_mode_with_cp_front_door_address_already_containing_protocol(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, username='user', api_key='123', cp_front_door_address='https://auth.example.com')
        client = env.build_client()
        self.assertEqual(client.auth_type.zen_auth_address, 'https://auth.example.com')

    def test_build_client_with_zen_mode_using_auth_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, username='user', api_key='123', auth_address='auth.example.com')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, ZenAPIKeyAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.api_key, '123')
        self.assertEqual(client.auth_type.zen_auth_address, 'https://auth.example.com')

    def test_build_client_with_zen_mode_with_auth_address_already_containing_protocol(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, username='user', api_key='123', auth_address='https://auth.example.com')
        client = env.build_client()
        self.assertEqual(client.auth_type.zen_auth_address, 'https://auth.example.com')

    def test_build_client_with_zen_mode_without_auth_address_or_cp_front_door_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, username='user', api_key='123')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, ZenAPIKeyAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.api_key, '123')
        self.assertIsNone(client.auth_type.zen_auth_address)

    def test_build_client_with_zen_mode_without_username_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, api_key='123')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "username" when using "auth_mode=zen"')

    def test_build_client_with_cp_api_key_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, username='user', api_key='123', cp_front_door_address='auth.example.com')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, ZenAPIKeyAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.api_key, '123')
        self.assertEqual(client.auth_type.zen_auth_address, 'https://auth.example.com')
        self.assertIsNone(client.auth_type.override_auth_endpoint)

    def test_build_client_with_cp_api_key_mode_with_cp_front_door_address_already_containing_protocol(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, username='user', api_key='123', cp_front_door_address='https://auth.example.com')
        client = env.build_client()
        self.assertEqual(client.auth_type.zen_auth_address, 'https://auth.example.com')

    def test_build_client_with_cp_api_key_mode_using_auth_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, username='user', api_key='123', auth_address='auth.example.com')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, ZenAPIKeyAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.api_key, '123')
        self.assertEqual(client.auth_type.zen_auth_address, 'https://auth.example.com')

    def test_build_client_with_cp_api_key_mode_with_ath_address_already_containing_protocol(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, username='user', api_key='123', auth_address='https://auth.example.com')
        client = env.build_client()
        self.assertEqual(client.auth_type.zen_auth_address, 'https://auth.example.com')

    def test_build_client_with_cp_api_key_mode_without_auth_address_or_cp_front_door_address(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, username='user', api_key='123')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, ZenAPIKeyAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.api_key, '123')
        self.assertIsNone(client.auth_type.zen_auth_address)

    def test_build_client_with_cp_api_key_mode_without_username_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, api_key='123')
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "username" when using "auth_mode=cp-api-key"')

    def test_build_client_with_cp_api_key_mode_and_cp_auth_endpoint(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=CP_API_KEY_AUTH_MODE, username='user', api_key='123', cp_auth_endpoint='v2/auth')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, ZenAPIKeyAuth)
        self.assertEqual(client.auth_type.username, 'user')
        self.assertEqual(client.auth_type.api_key, '123')
        self.assertIsNone(client.auth_type.zen_auth_address)
        self.assertEqual(client.auth_type.override_auth_endpoint, 'v2/auth')

    def test_build_client_with_token_mode(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=TOKEN_AUTH_MODE, token='123')
        client = env.build_client()
        self.assertIsInstance(client.auth_type, JwtTokenAuth)
        self.assertEqual(client.auth_type.token, '123')
    
    def test_build_client_with_token_mode_without_token_fails(self):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=TOKEN_AUTH_MODE)
        with self.assertRaises(ValueError) as ctx:
            env.build_client()
        self.assertEqual(str(ctx.exception), 'Invalid CP4NA environment - must configure "token" when using "auth_mode=token"')

    #ZEN API METHOD
    #ADDRESS OVERRIDES ARE NONE

class TestLmSession(unittest.TestCase):

    def test_init(self):
        env = TNCOEnvironment(address='testing.example.com')
        session = LmSession(env)
        self.assertEqual(session.env, env)

    @mock.patch('lmctl.environment.lmenv.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_legacy_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='user', password='secret', auth_address='auth.example.com')
        session = LmSession(env)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.legacy_user_pass_auth.assert_called_once_with(username='user', password='secret', legacy_auth_address='https://auth.example.com')

    @mock.patch('lmctl.environment.lmenv.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_user_pass_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_USER_MODE, 
                              username='user', password='secret', client_id='UserClient', client_secret='c_secret')
        
        session = LmSession(env)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('https://testing.example.com')
        mock_client_builder.user_pass_auth.assert_called_once_with(username='user', password='secret', client_id='UserClient', client_secret='c_secret')

    @mock.patch('lmctl.environment.lmenv.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_okta_user_pass_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OKTA_USER_MODE, 
                              username='user', password='secret', client_id='UserClient', 
                              client_secret='c_secret', auth_address='auth.example.com', 
                              scope='test', auth_server_id='default')
        
        session = LmSession(env)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value
        mock_client_builder.address.assert_called_once_with('https://testing.example.com')
        mock_client_builder.okta_user_pass_auth.assert_called_once_with(username='user', password='secret', client_id='UserClient', client_secret='c_secret', scope='test', auth_server_id='default', okta_server='https://auth.example.com')

    @mock.patch('lmctl.environment.lmenv.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_client_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_CLIENT_MODE, client_id='UserClient', client_secret='c_secret')
        
        session = LmSession(env)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('https://testing.example.com')
        mock_client_builder.client_credentials_auth.assert_called_once_with(client_id='UserClient', client_secret='c_secret')

    @mock.patch('lmctl.environment.lmenv.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_token_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='https://testing.example.com', auth_mode=TOKEN_AUTH_MODE, token='123')
        
        session = LmSession(env)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('https://testing.example.com')
        mock_client_builder.token_auth.assert_called_once_with(token='123')

    @mock.patch('lmctl.environment.lmenv.TNCOClientBuilder')
    def test_security_ctrl_builds_client_with_zen_auth(self, mock_client_builder_init):
        env = TNCOEnvironment(address='testing.example.com', auth_mode=ZEN_AUTH_MODE, username='user', api_key='123', auth_address='https://zen.example.com')
        
        session = LmSession(env)
        driver = session.descriptor_driver #Force LmSecurityCtrl to be created
        mock_client_builder = mock_client_builder_init.return_value 
        mock_client_builder.address.assert_called_once_with('https://testing.example.com')
        mock_client_builder.zen_api_key_auth.assert_called_once_with(username='user', api_key='123', zen_auth_address='https://zen.example.com', override_auth_endpoint=None)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDescriptorDriver')
    def test_descriptor_driver(self, descriptor_driver_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com'))
        driver = session.descriptor_driver
        descriptor_driver_init.assert_called_once_with('https://testing.example.com', None)
        self.assertEqual(driver, descriptor_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDescriptorDriver')
    def test_descriptor_driver_with_security(self, descriptor_driver_init, mock_security_ctrl_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='user', password='pass'))
        driver = session.descriptor_driver
        mock_security_ctrl_init.assert_called_once_with(session.env)
        descriptor_driver_init.assert_called_once_with('https://testing.example.com', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, descriptor_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmOnboardRmDriver')
    def test_onboard_rm_driver(self, onboard_rm_driver_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com'))
        driver = session.onboard_rm_driver
        onboard_rm_driver_init.assert_called_once_with('https://testing.example.com', None)
        self.assertEqual(driver, onboard_rm_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmOnboardRmDriver')
    def test_onboard_rm_driver_with_security(self, onboard_rm_driver_init, mock_security_ctrl_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='user', password='pass'))
        driver = session.onboard_rm_driver
        mock_security_ctrl_init.assert_called_once_with(session.env)
        onboard_rm_driver_init.assert_called_once_with('https://testing.example.com', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, onboard_rm_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmTopologyDriver')
    def test_topology_driver(self, topology_driver_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com'))
        driver = session.topology_driver
        topology_driver_init.assert_called_once_with('https://testing.example.com', None)
        self.assertEqual(driver, topology_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmTopologyDriver')
    def test_topology_driver_with_security(self, topology_driver_init, mock_security_ctrl_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='user', password='pass'))
        driver = session.topology_driver
        mock_security_ctrl_init.assert_called_once_with(session.env)
        topology_driver_init.assert_called_once_with('https://testing.example.com', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, topology_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmBehaviourDriver')
    def test_behaviour_driver(self, behaviour_driver_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com'))
        driver = session.behaviour_driver
        behaviour_driver_init.assert_called_once_with('https://testing.example.com', None)
        self.assertEqual(driver, behaviour_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmBehaviourDriver')
    def test_behaviour_driver_with_security(self, behaviour_driver_init, mock_security_ctrl_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='user', password='pass'))
        driver = session.behaviour_driver
        mock_security_ctrl_init.assert_called_once_with(session.env)
        behaviour_driver_init.assert_called_once_with('https://testing.example.com', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, behaviour_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDeploymentLocationDriver')
    def test_deployment_location_driver(self, deployment_location_driver_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com'))
        driver = session.deployment_location_driver
        deployment_location_driver_init.assert_called_once_with('https://testing.example.com', None)
        self.assertEqual(driver, deployment_location_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmDeploymentLocationDriver')
    def test_deployment_location_driver_with_security(self, deployment_location_driver_init, mock_security_ctrl_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='user', password='pass'))
        driver = session.deployment_location_driver
        mock_security_ctrl_init.assert_called_once_with(session.env)
        deployment_location_driver_init.assert_called_once_with('https://testing.example.com', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, deployment_location_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmInfrastructureKeysDriver')
    def test_infrastructure_keys_driver(self, infrastructure_keys_driver_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com'))
        driver = session.infrastructure_keys_driver
        infrastructure_keys_driver_init.assert_called_once_with('https://testing.example.com', None)
        self.assertEqual(driver, infrastructure_keys_driver_init.return_value)

    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmSecurityCtrl')
    @mock.patch('lmctl.environment.lmenv.lm_drivers.LmInfrastructureKeysDriver')
    def test_infrastructure_keys_driver_with_security(self, infrastructure_keys_driver_init, mock_security_ctrl_init):
        session = LmSession(TNCOEnvironment(address='testing.example.com', auth_mode=OAUTH_LEGACY_USER_MODE, username='user', password='pass'))
        driver = session.infrastructure_keys_driver
        mock_security_ctrl_init.assert_called_once_with(session.env)
        infrastructure_keys_driver_init.assert_called_once_with('https://testing.example.com', mock_security_ctrl_init.return_value)
        self.assertEqual(driver, infrastructure_keys_driver_init.return_value)
