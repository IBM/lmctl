import click
from .wrap_utils import wrap, Func, FuncDecorator
from typing import Union, Dict, Any, Callable, Tuple

__all__ = (
    'constraint',
    'mutually_exclusive',
)

def constraint(constraint_check: Callable[...,Tuple[bool,str]]) -> FuncDecorator:
    """
    Wraps behaviour of the callback to check a constraint
    """
    def decorator(cmd_callback: Func) -> Func:
        # Build new function
        def wrapper(*args, **kwargs):
            result, reason = constraint_check(*args, **kwargs)
            if result is False:
                raise click.UsageError(reason if reason is not None else f'N/A (No reason given by constraint: {cmd_callback.__name__})', ctx=click.get_current_context())

            return cmd_callback(*args, **kwargs)

        new_callback = wrap(cmd_callback, wrapper)
        return new_callback
        
    return decorator

def mutually_exclusive(*params: Tuple[str, str]) -> FuncDecorator:
    def mutex_check(*args, **kwargs):
        found_param = None
        for param in params:
            param_name = param[0]
            param_opts = param[1]
            value = kwargs.get(param_name, None)
            if value is not None and value is not False:
                if found_param is not None:
                    return False, f'Cannot use "{param_opts}" with "{found_param}" as they are mutually exclusive'
                else:
                    found_param = param_opts
        return True, None
    return constraint(mutex_check)