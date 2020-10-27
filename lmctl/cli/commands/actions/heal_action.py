from .action import Action

class Heal(Action):
    name = 'heal'
    group_attrs = {
        'help': 'Heal Assembly components and other supported objects'
    }
