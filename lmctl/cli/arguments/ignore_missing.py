import click
from typing import Sequence

__all__ = (
    'IgnoreMissingOption',
    'ignore_missing_option',
)

default_param_decls = ['--ignore-missing']

class IgnoreMissingOption(click.Option):

    def __init__(
            self, 
            param_decls: Sequence[str] = default_param_decls,
            help: str = 'Ignore if object not found', 
            **kwargs):
        param_decls = [p for p in param_decls]
        super().__init__(
            param_decls,
            is_flag=True,
            help=help,
            **kwargs
        )

def ignore_missing_option(*args, **kwargs):
    def decorator(f):
        param_decls = args
        if len(param_decls) == 0:
            param_decls = default_param_decls
        return click.option(*param_decls, cls=IgnoreMissingOption, **kwargs)(f)
    return decorator