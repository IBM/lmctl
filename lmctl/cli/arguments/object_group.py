import click
from typing import Any, Sequence

__all__ = (
    'ObjectGroupOption',
    'ObjectGroupIDOption',
    'object_group_option',
    'object_group_id_option'
)

default_param_decls = ['--og', '--object-group', 'object_group']
default_id_param_decls = ['--ogid', '--object-group-id', 'object_group_id']

class ObjectGroupOption(click.Option):

    def __init__(self, 
            param_decls: Sequence[str] = default_param_decls,
            help: str = 'Object Group to perform the request in', 
            **kwargs
        ):
        
        param_decls = [p for p in param_decls]

        super().__init__(
            param_decls,
            help=help,
            **kwargs
        )

class ObjectGroupIDOption(click.Option):

    def __init__(self, 
            param_decls: Sequence[str] = default_id_param_decls,
            help: str = 'ID of the Object Group to perform the request in', 
            **kwargs
        ):
        
        param_decls = [p for p in param_decls]
        super().__init__(
            param_decls,
            help=help,
            **kwargs
        )

def object_group_option(*args, **kwargs):
    def decorator(f):
        param_decls = args
        if len(param_decls) == 0:
            param_decls = default_param_decls
        return click.option(*param_decls, cls=ObjectGroupOption, **kwargs)(f)
    return decorator

def object_group_id_option(*args, **kwargs):
    def decorator(f):
        param_decls = args
        if len(param_decls) == 0:
            param_decls = default_param_decls
        return click.option(*param_decls, cls=ObjectGroupIDOption, **kwargs)(f)
    return decorator