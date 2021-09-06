import click
from typing import Sequence

__all__ = (
    'IgnoreMissingOption',
    'ignore_missing_option',
)

class IgnoreMissingOption(click.Option):

    def __init__(
            self, 
            param_decls: Sequence[str] = ['--ignore-missing'],
            help: str = 'Ignore if object not found', 
            **kwargs):
        param_decls = [p for p in param_decls]
        super().__init__(
            param_decls,
            is_flag=True,
            help=help,
            **kwargs
        )

def ignore_missing_option():
    def decorator(f):
        return click.option('--ignore-missing', 
                        help='Ignore if object not found',
                        is_flag=True
                        )(f)
    return decorator
