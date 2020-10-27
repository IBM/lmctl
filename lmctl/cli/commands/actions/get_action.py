from .action import Action

class Get(Action):
    name = 'get'
    group_attrs = {
        'help': 'Display details of supported objects'
    }
