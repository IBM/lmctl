import click
from typing import Any, Sequence

__all__ = (
    'ObjectGroupOption',
    'ObjectGroupIDOption',
    'object_group_option',
    'object_group_id_option',
    'OBJECT_GROUP_PARAM_NAME',
    'OBJECT_GROUP_PARAM_OPTS',
    'OBJECT_GROUP_PARAM_OPTS_STR',
    'OBJECT_GROUP_ID_PARAM_NAME',
    'OBJECT_GROUP_ID_PARAM_OPTS',
    'OBJECT_GROUP_ID_PARAM_OPTS_STR'
)

OBJECT_GROUP_PARAM_NAME = 'object_group_name'
OBJECT_GROUP_PARAM_OPTS = ['--og', '--object-group']
OBJECT_GROUP_PARAM_OPTS_STR = ','.join(OBJECT_GROUP_PARAM_OPTS)

OBJECT_GROUP_ID_PARAM_NAME = 'object_group_id'
OBJECT_GROUP_ID_PARAM_OPTS = ['--ogid', '--object-group-id']
OBJECT_GROUP_ID_PARAM_OPTS_STR = ','.join(OBJECT_GROUP_ID_PARAM_OPTS)

default_param_decls = [*OBJECT_GROUP_PARAM_OPTS, OBJECT_GROUP_PARAM_NAME]
default_id_param_decls = [*OBJECT_GROUP_ID_PARAM_OPTS, OBJECT_GROUP_ID_PARAM_NAME]

class ObjectGroupOption(click.Option):

    def __init__(self, 
            param_decls: Sequence[str] = default_param_decls,
            help: str = 'Name of the Object Group to perform the request in', 
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
            param_decls = default_id_param_decls
        return click.option(*param_decls, cls=ObjectGroupIDOption, **kwargs)(f)
    return decorator