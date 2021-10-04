import click
from typing import Sequence, Any
from lmctl.cli.format import OutputFormat, Table, Column, JsonFormat, YamlFormat, TableFormat

JSON_VALUE = 'json'
YAML_VALUE = 'yaml'
TABLE_VALUE = 'table'

__all__ = (
    'OutputFormatOption',
    'output_format_option',
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
