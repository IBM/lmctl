from lmctl.client.client_credentials_auth import ClientCredentialsAuth
from lmctl.client.pass_auth import UserPassAuth, LegacyUserPassAuth, OktaUserPassAuth
from lmctl.client.zen_auth import ZenAPIKeyAuth
from lmctl.client.token_auth import JwtTokenAuth
from typing import Dict

class AuthTesting:

    def __init__(self, client_credentials: ClientCredentialsAuth, 
                    user_pass: UserPassAuth, 
                    legacy_user_pass: LegacyUserPassAuth,
                    zen_api_key: ZenAPIKeyAuth,
                    token_auth: JwtTokenAuth,
                    okta_user_pass_auth: OktaUserPassAuth):
        self.client_credentials = client_credentials
        self.user_pass = user_pass
        self.legacy_user_pass = legacy_user_pass
        self.zen_api_key = zen_api_key
        self.token_auth = token_auth
        self.okta_user_pass_auth = okta_user_pass_auth

    @staticmethod
    def from_dict(client_credentials: Dict = None, 
                    user_pass: Dict = None, 
                    legacy_user_pass: Dict = None,
                    zen_api_key: Dict = None,
                    token_auth: Dict = None,
                    okta_user_pass_auth = None):
        return AuthTesting(
            zen_api_key=ZenAPIKeyAuth(**zen_api_key) if zen_api_key is not None else None,
            client_credentials=ClientCredentialsAuth(**client_credentials) if client_credentials is not None else None,
            user_pass=UserPassAuth(**user_pass) if user_pass is not None else None,
            legacy_user_pass=LegacyUserPassAuth(**legacy_user_pass) if legacy_user_pass is not None else None,
            token_auth=JwtTokenAuth(**token_auth) if token_auth is not None else None,
            okta_user_pass_auth=OktaUserPassAuth(**okta_user_pass_auth) if okta_user_pass_auth is not None else None
        )

class IntegrationTestProperties:

    def __init__(self, config: Dict, auth_testing: AuthTesting):
        self.config = config
        self.auth_testing = auth_testing

    @staticmethod
    def from_dict(config: Dict, auth_testing: Dict):
        return IntegrationTestProperties(
            config=config,
            auth_testing=AuthTesting.from_dict(**auth_testing) 
        )
