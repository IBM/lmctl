import click
from typing import Sequence, Any
from lmctl.cli.format import OutputFormat, Table, Column, JsonFormat, YamlFormat, TableFormat

JSON_VALUE = 'json'
YAML_VALUE = 'yaml'
TABLE_VALUE = 'table'

__all__ = (
    'OutputFormatOption',
    'output_format_option',
    'OutputFormats',
    'output_format_handler', 
    'common_output_format_handler', 
    'default_output_format_handler'
)

class OutputFormatOption(click.Option):
    default_param_decls = ['-o', '--output', 'output_format']
    
    def __init__(
            self,  
            param_decls: Sequence[str] = default_param_decls,
            help: str = 'Format of output', 
            default: str = None,
            show_default: bool = True,
            default_columns: Sequence[Column] = None,
            **kwargs):
        param_decls = [p for p in param_decls]

        self.formatters = {
            YAML_VALUE: YamlFormat(),
            JSON_VALUE: JsonFormat()
        }
        if default_columns is not None:
            self.formatters[TABLE_VALUE] = TableFormat(table=Table(default_columns))
        if default is None:
            default = YAML_VALUE if default_columns is None else TABLE_VALUE

        self.wrapped_callback = kwargs.pop('callback', None)

        super().__init__(
            param_decls,
            help=help,
            type=click.Choice([n for n in self.formatters.keys()], case_sensitive=False),
            default=default,
            show_default=show_default,
            callback=self._callback,
            **kwargs
        )

    def _callback(self, ctx: click.Context, param: click.Parameter, value: Any):
        formatter = self.formatters.get(value)
        return formatter


def output_format_option(*args, **kwargs):
    def decorator(f):
        param_decls = args
        if len(param_decls) == 0:
            param_decls = OutputFormatOption.default_param_decls
        return click.option(*param_decls, cls=OutputFormatOption, **kwargs)(f)
    return decorator


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

