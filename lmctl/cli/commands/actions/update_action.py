from .action import Action

class Update(Action):
    name = 'update'
    group_attrs = {
        'help': 'Update supported objects'
    }
