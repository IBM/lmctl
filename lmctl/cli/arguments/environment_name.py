import click
from typing import Sequence

__all__ = (
    'EnvironmentNameOption',
    'environment_name_option'
)

def environment_name_option():
    def decorator(f):
        return click.option('-e', '--environment', 'environment_name', 
                        required=False,
                        help='Name of the environment from the configuration file to be used'
                        )(f)
    return decorator


class EnvironmentNameOption(click.Option):

    def __init__(
            self, 
            param_decls: Sequence[str] = ['-e', '--environment', 'environment_name'],
            required: bool = False, 
            help: str = 'Name of the environment from the configuration file to be used', 
            **kwargs):
        param_decls = [p for p in param_decls]
        super().__init__(
            param_decls,
            required=required,
            help=help,
            **kwargs
        )