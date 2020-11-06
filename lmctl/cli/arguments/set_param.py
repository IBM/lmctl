import click
from typing import Dict, List

def _parser(options):
    def _parse_value(ctx, param, value) -> Dict:
        parse_result = {}
        for v in value:
            split = v.split('=')
            if len(split) != 2:
                raise click.BadParameter(f'{options} value must use format <key>=<value>', ctx=ctx, param=param)
            parse_result[split[0]] = split[1]
        return parse_result
    return _parse_value

def set_param_option(options: List = ['--set'], var_name: str = 'set_values', help: str = 'Set parameters on the object'):
    def decorator(f):
        return click.option(*options, var_name, 
                        help=help,
                        multiple=True,
                        callback=_parser(options)
                        )(f)
    return decorator
