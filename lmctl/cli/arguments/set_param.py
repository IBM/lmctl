import click
from typing import Dict

def _parse_value(ctx, param, value) -> Dict:
    parse_result = {}
    for v in value:
        split = v.split('=')
        if len(split) != 2:
            raise click.BadParameter('--set value must use format <key>=<value>', ctx=ctx, param=param)
        parse_result[split[0]] = split[1]
    return parse_result

def set_param_option(help: str = None):
    def decorator(f):
        return click.option('--set', 'set_values', 
                        help=help or 'Set parameters on the object',
                        multiple=True,
                        callback=_parse_value
                        )(f)
    return decorator
