from .output_format import OutputFormat
from .input_format import InputFormat
from .json import JsonFormat
from .yaml import YamlFormat
from .table import TableFormat, Table, Column
from .exceptions import BadFormatError
import warnings

TABLE_FORMAT = 'table'
YAML_FORMAT = 'yaml'
JSON_FORMAT = 'json'

def determine_format_class(output_format):
    warnings.warn('determine_format_class is deprecated, use lmctl.cli.argument.format.FormatOptionBuilder instead', DeprecationWarning)
    if output_format == TABLE_FORMAT:
        result = TableFormat
    elif output_format == YAML_FORMAT:
        result = YamlFormat
    elif output_format == JSON_FORMAT:
        result = JsonFormat
    else:
        from lmctl.cli.io import IOController
        IOController.get().print_error('OutputFormat {0} is not a valid option'.format(output_format))
        exit(1)
    return result

##Backwards compatibility
Format = OutputFormat