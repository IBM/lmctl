import click
import os
from typing import Sequence, Any, List
from collections import OrderedDict
from lmctl.cli.format import InputFormat, JsonFormat, YamlFormat, BadFormatError

__all__ = (
    'FileInputOption',
    'file_input_option'
)

JSON_VALUE = 'json'
YAML_VALUE = 'yaml'

default_param_decls = ['-f', '--file', 'file_content']

class FileInputOption(click.Option):

    def __init__(
            self, 
            param_decls: Sequence[str] = default_param_decls,
            help: str = 'Path to file representing the object data', 
            **kwargs):
        param_decls = [p for p in param_decls]

        self.formatters = {
            JSON_VALUE: JsonFormat(),
            YAML_VALUE: YamlFormat()
        }
        self.wrapped_callback = kwargs.pop('callback', None)

        super().__init__(
            param_decls,
            help=help,
            type=click.Path(exists=True),
            callback=self._callback,
            **kwargs
        )

    def _callback(self, ctx: click.Context, param: click.Parameter, value: Any):
        return_value = None
        if value is not None:
            with open(value) as f:
                content = f.read()
            failures = OrderedDict()
            for name, format_instance in self.formatters.items():
                try:
                    return_value = format_instance.read(content)
                except BadFormatError as e:
                    failures[name] = str(e)
            if return_value is None:
                error_msg = 'Failed to read content to supported formats: '
                for name, error in failures.items():
                    error_msg += f'\n\t{name}: {error}'
                raise click.BadParameter(error_msg, ctx=ctx, param=param)
        if self.wrapped_callback is not None:
            return self.wrapped_callback(return_value)
        else:
            return return_value

def file_input_option(*args, **kwargs):
    def decorator(f):
        param_decls = args
        if len(param_decls) == 0:
            param_decls = default_param_decls
        return click.option(*param_decls, cls=FileInputOption, **kwargs)(f)
    return decorator