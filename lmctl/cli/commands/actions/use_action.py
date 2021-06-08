from .action import Action

class Use(Action):
    name = 'use'
    group_attrs = {
        'help': 'Change active environment'
    }
