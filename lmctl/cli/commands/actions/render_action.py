from .action import Action

class Render(Action):
    name = 'render'
    group_attrs = {
        'help': 'Render Descriptor Templates or any other supported objects'
    }
