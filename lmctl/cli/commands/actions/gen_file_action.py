from .action import Action

class GenerateFile(Action):
    name = 'genfile'
    group_attrs = {
        'help': 'Generate example file for supported object types'
    }
