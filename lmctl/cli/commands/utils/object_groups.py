from lmctl.cli.arguments import object_group_id_option, object_group_option, OBJECT_GROUP_ID_PARAM_NAME, OBJECT_GROUP_ID_PARAM_OPTS_STR, OBJECT_GROUP_PARAM_NAME, OBJECT_GROUP_PARAM_OPTS_STR
from .constraints import mutually_exclusive

__all__ = (
    'object_group_options',
)

def object_group_options():
    def decorator(f):
        f = object_group_id_option()(f)
        f = object_group_option()(f)
        return mutually_exclusive((OBJECT_GROUP_PARAM_NAME, OBJECT_GROUP_PARAM_OPTS_STR), (OBJECT_GROUP_ID_PARAM_NAME, OBJECT_GROUP_ID_PARAM_OPTS_STR))(f)
    return decorator
