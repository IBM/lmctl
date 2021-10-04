import click
from typing import Sequence

__all__ = (
    'EnvironmentNameOption',
)

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