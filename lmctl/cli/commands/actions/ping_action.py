from .action import Action
from lmctl.cli.cmd_tags import settings_tag

@settings_tag
class Ping(Action):
    name = 'ping'
    group_attrs = {
        'help': 'Test connection to environments'
    }