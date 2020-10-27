from .action import Action

class ChangeState(Action):
    name = 'changestate'
    group_attrs = {
        'help': 'Change state of an Assembly or another supported object'
    }
