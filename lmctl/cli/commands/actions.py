import click
import inspect
import sys
from typing import Optional, Iterable, Callable
from lmctl.cli.tags import SETTINGS_TAG, CP4NA_CORE_TAG, SITE_PLANNER_TAG
from .super_group import SuperGroup

action_groups = []

def action_group(*args, aliases: Optional[Iterable[str]] = None, **kwargs) -> Callable:
    def decorator(f):
        g = click.group(*args, 
                            cls=SuperGroup, tag_order=[SETTINGS_TAG, CP4NA_CORE_TAG, SITE_PLANNER_TAG], 
                            **kwargs)(f)
        action_groups.append({'group': g, 'aliases': aliases})
        return g
    return decorator

@action_group(help='Adopt Assembly or any other supported objects')
def adopt():
    pass

@action_group(help='Cancel scenario executions or another supported object')
def cancel():
    pass

@action_group(help='Change state of an Assembly or another supported object')
def changestate():
    pass

@action_group(help='Create supported objects')
def create():
    pass

@action_group(help='Delete supported objects')
def delete():
    pass

@action_group(help='Execute scenarios or another supported object')
def execute():
    pass

@action_group(aliases=['genfile'], help='Generate example file for supported object types')
def generate():
    pass

@action_group(help='Display details of supported objects')
def get():
    pass

@action_group(help='Heal Assembly components and other supported objects')
def heal():
    pass

@action_group(help='Retry an Assembly components')
def retry():
    pass

@action_group(help='Rollback an Assembly components')
def rollback():
    pass

@action_group(help='Test connection to environments')
def ping():
    pass

@action_group(help='Render Descriptor Templates or any other supported objects')
def render():
    pass

@action_group(help='Scale Assembly clusters and other supported objects')
def scale():
    pass

@action_group(help='Update supported objects')
def update():
    pass

@action_group(help='Change active environment')
def use():
    pass



# Get all groups in this module, except base classes such as SuperGroup
_group_members = inspect.getmembers(sys.modules[__name__], lambda x: isinstance(x, click.Group) and not x==SuperGroup)
_to_expose = [g[0] for g in _group_members]
_to_expose = _to_expose + ['action_groups']
__all__ = tuple(_to_expose)
