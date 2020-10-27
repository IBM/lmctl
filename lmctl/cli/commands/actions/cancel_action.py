from .action import Action

class Cancel(Action):
    name = 'cancel'
    group_attrs = {
        'help': 'Cancel scenario executions or another supported object'
    }
