import click
from lmctl.cli.format import OutputFormat, Table, JsonFormat, YamlFormat, TableFormat

JSON_VALUE = 'json'
YAML_VALUE = 'yaml'
TABLE_VALUE = 'table'

class OutputFormats:

    def __init__(self):
        self._choices = {}
        self._default_choice = None

    @property
    def choices(self):
        return self._choices

    def add_choice(self, name: str, format_instance: OutputFormat, is_default: bool = False) -> 'OutputFormats':
        self._choices[name] = format_instance
        if is_default:
            self._default_choice = name
        return self

    def option(self):
        def decorator(f):
            choice_names = [k for k in self._choices.keys()]
            return click.option('-o', '--output', 'output_format', 
                                default=self._default_choice, 
                                help='Format of output',
                                show_default=True,
                                type=click.Choice(choice_names, case_sensitive=False)
                            )(f)
        return decorator

    def resolve_choice(self, choice: str) -> OutputFormat:
        return self._choices[choice]

def output_format_handler():
    return OutputFormats()

def common_output_format_handler(table: Table):
    return output_format_handler()\
            .add_choice(TABLE_VALUE, TableFormat(table=table), is_default=True)\
            .add_choice(YAML_VALUE, YamlFormat())\
            .add_choice(JSON_VALUE, JsonFormat())

def default_output_format_handler():
    return output_format_handler()\
        .add_choice(YAML_VALUE, YamlFormat(), is_default=True)\
        .add_choice(JSON_VALUE, JsonFormat())

