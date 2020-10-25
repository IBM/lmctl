import click
import os
from collections import OrderedDict
from lmctl.cli.format import InputFormat, JsonFormat, YamlFormat, BadFormatError

JSON_VALUE = 'json'
YAML_VALUE = 'yaml'

class FileInputs:

    def __init__(self):
        self._formats = OrderedDict()

    def add_format(self, name: str, format_instance: InputFormat) -> 'InputFormats':
        self._formats[name] = format_instance
        return self

    def _callback(self, ctx, param, value):
        if value is None:
            return None
        if not os.path.exists(value):
            raise click.BadParameter(f'File path given does not exist: {value}', ctx=ctx, param=param)
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

    def option(self):
        def decorator(f):
            return click.option('-f', '--file', 'file_content', 
                                help='Path to file used to create the object',
                                required=False,
                                callback=self._callback
                            )(f)
        return decorator

def file_inputs_handler():
    return FileInputs()

def default_file_inputs_handler():
    return file_inputs_handler()\
        .add_format(YAML_VALUE, YamlFormat())\
        .add_format(JSON_VALUE, JsonFormat())

