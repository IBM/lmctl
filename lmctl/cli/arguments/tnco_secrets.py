import click
from typing import List, Sequence

__all__ = (
    'TNCOPwdOption',
    'TNCOClientSecretOption',
    'TNCOTokenOption',
)

default_pwd_help = 'CP4NA orchestration password used for authenticating.'\
    + ' Only required if the environment is secure and a username has been included in your configuration file with no password (api_key if using auth_mode: zen)'

class TNCOPwdOption(click.Option):

    def __init__(
            self, 
            param_decls: Sequence[str] = ['--pwd', '--api-key'],
            help: str = default_pwd_help,
            **kwargs):
        param_decls = [p for p in param_decls]
        super().__init__(
            param_decls,
            help=help,
            **kwargs
        )

default_secret_help = 'CP4NA orchestration client secret used for authenticating.'\
    + ' Only required if the environment is secure and a client_id has been included in your configuration file with no client_secret'

class TNCOClientSecretOption(click.Option):
    
    def __init__(
            self, 
            param_decls: Sequence[str] = ['--client-secret'],
            help: str = default_secret_help,
            **kwargs):
        param_decls = [p for p in param_decls]
        super().__init__(
            param_decls,
            help=help,
            **kwargs
        )

default_token_help = 'CP4NA orchestration auth token used for authenticating.'\
    + ' Only required if the environment is secure and "auth_mode" is set to "token", without a "token" in your configuration file'

class TNCOTokenOption(click.Option):
    
    def __init__(
            self, 
            param_decls: Sequence[str] = ['--token'],
            help: str = default_token_help,
            **kwargs):
        param_decls = [p for p in param_decls]
        super().__init__(
            param_decls,
            help=help,
            **kwargs
        )
