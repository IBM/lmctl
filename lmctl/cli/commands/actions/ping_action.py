from .action import Action

class Ping(Action):
    name = 'ping'
    group_attrs = {
        'help': 'Test connection to supported objects'
    }