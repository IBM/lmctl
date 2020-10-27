from .action import Action

class Adopt(Action):
    name = 'adopt'
    group_attrs = {
        'help': 'Adopt Assembly or any other supported objects'
    }
