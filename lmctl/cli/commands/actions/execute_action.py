from .action import Action

class Execute(Action):
    name = 'execute'
    group_attrs = {
        'help': 'Execute scenarios or another supported object'
    }
