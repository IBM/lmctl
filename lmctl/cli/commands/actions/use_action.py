from .action import Action
from lmctl.cli.cmd_tags import settings_tag

@settings_tag
class Use(Action):
    name = 'use'
    group_attrs = {
        'help': 'Change active environment'
    }
