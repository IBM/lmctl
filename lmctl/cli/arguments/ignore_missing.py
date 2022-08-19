import click
from typing import Sequence

__all__ = (
    'IgnoreMissingOption',
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
