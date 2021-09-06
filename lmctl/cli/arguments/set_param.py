import click
from typing import Dict, List, Any, Sequence

__all__ = (
    'SetParamOption',
    'set_param_option'
)

default_param_decls = ['--set', 'set_values']

class SetParamOption(click.Option):

    def __init__(
            self, 
            param_decls: Sequence[str] = default_param_decls,
            help: str = 'Set parameters on the object', 
            **kwargs):
        param_decls = [p for p in param_decls]

        self.wrapped_callback = kwargs.pop('callback', None)
        super().__init__(
            param_decls,
            help=help,
            multiple=True,
            callback=self._callback,
            **kwargs
        )

    def _callback(self, ctx: click.Context, param: click.Parameter, value: Any):
        parse_result = {}
        if value is None:
            value = []
        for v in value:
            split = v.split('=')
            if len(split) != 2:
                raise click.BadParameter(f'value must use format <key>=<value>', ctx=ctx, param=param)
            parse_result[split[0]] = split[1]
        if self.wrapped_callback is not None:
            return self.wrapped_callback(parse_result)
        else:
            return parse_result

def set_param_option(*args, **kwargs):
    def decorator(f):
        param_decls = args
        if len(param_decls) == 0:
            param_decls = default_param_decls
        return click.option(*param_decls, cls=SetParamOption, **kwargs)(f)
    return decorator
