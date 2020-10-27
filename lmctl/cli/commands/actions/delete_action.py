from .action import Action

class Delete(Action):
    name = 'delete'
    group_attrs = {
        'help': 'Delete supported objects'
    }
