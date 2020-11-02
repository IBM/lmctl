from lmctl.client.client_credentials_auth import ClientCredentialsAuth
from lmctl.client.pass_auth import UserPassAuth, LegacyUserPassAuth
from typing import Dict

class AuthTesting:

    def __init__(self, client_credentials: ClientCredentialsAuth, 
                    user_pass: UserPassAuth, 
                    legacy_user_pass: LegacyUserPassAuth):
        self.client_credentials = client_credentials
        self.user_pass = user_pass
        self.legacy_user_pass = legacy_user_pass

    @staticmethod
    def from_dict(client_credentials: Dict, 
                    user_pass: Dict, 
                    legacy_user_pass: Dict):
        return AuthTesting(
            client_credentials=ClientCredentialsAuth(**client_credentials),
            user_pass=UserPassAuth(**user_pass),
            legacy_user_pass=LegacyUserPassAuth(**legacy_user_pass)
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
