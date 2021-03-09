import click
import os
from typing import List
from collections import OrderedDict
from lmctl.cli.format import InputFormat, JsonFormat, YamlFormat, BadFormatError

JSON_VALUE = 'json'
YAML_VALUE = 'yaml'

class FileInputs:

    def __init__(self):
        self._formats = OrderedDict()

    @property
    def formats(self):
        return self._formats

    def add_format(self, name: str, format_instance: InputFormat) -> 'InputFormats':
        self._formats[name] = format_instance
        return self

    def _callback(self, ctx, param, value):
        if value is None:
            return None
        with open(value) as f:
            content = f.read()
        failures = OrderedDict()
        for name, format_instance in self._formats.items():
            try:
                return format_instance.read(content)
            except BadFormatError as e:
                failures[name] = str(e)
        error_msg = 'Failed to read content to supported formats: '
        for name, error in failures.items():
            error_msg += f'\n\t{name}: {error}'
        raise click.BadParameter(error_msg, ctx=ctx, param=param)

    def option(self, var_name: str = 'file_content', required: bool = False, 
                        help: str = 'Path to file representing the object', options: List[str] = ['-f', '--file']):
        def decorator(f):
            return click.option(*options, var_name, 
                                help=help,
                                required=required,
                                type=click.Path(exists=True),
                                callback=self._callback
                            )(f)
        return decorator

def file_inputs_handler(**kwargs):
    return FileInputs(**kwargs)

def default_file_inputs_handler(**kwargs):
    return file_inputs_handler(**kwargs)\
        .add_format(YAML_VALUE, YamlFormat())\
        .add_format(JSON_VALUE, JsonFormat())

