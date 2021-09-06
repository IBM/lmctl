import click
from typing import List, Sequence

__all__ = (
    'TNCOPwdOption',
    'TNCOClientSecretHelp',
    'TNCOTokenHelp',
    'tnco_pwd_option',
    'tnco_client_secret_option',
    'tnco_token_option'
)

default_pwd_help = 'CP4NA orchestration password used for authenticating.'\
    + ' Only required if the environment is secure and a username has been included in your configuration file with no password'

class TNCOPwdOption(click.Option):

    def __init__(
            self, 
            param_decls: Sequence[str] = ['--pwd'],
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

class TNCOClientSecretHelp(click.Option):
    
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

class TNCOTokenHelp(click.Option):
    
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

def tnco_pwd_option(options: List = ['--pwd'], var_name: str = 'pwd', help: str = default_pwd_help):
    def decorator(f):
        return click.option(*options, var_name, 
                        help=help
                        )(f)
    return decorator


def tnco_client_secret_option(options: List = ['--client-secret'], var_name: str = 'client_secret', help: str = default_secret_help):
    def decorator(f):
        return click.option(*options, var_name, 
                        help=help
                        )(f)
    return decorator


def tnco_token_option(options: List = ['--token'], var_name: str = 'token', help: str = default_token_help):
    def decorator(f):
        return click.option(*options, var_name, 
                        help=help
                        )(f)
    return decorator