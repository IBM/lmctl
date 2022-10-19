from .wrap_utils import wrap, Func, FuncDecorator
from typing import Union
from lmctl.cli.controller import get_global_controller

__all__ = (
    'pass_io',
)

def pass_io(cmd_callback: Func = None) -> Union[FuncDecorator, Func]:
    """
    Wraps behaviour of the callback to include IOController
    """
    def decorator(cmd_callback: Func) -> Func:
        # Build new function
        def wrapper(*args, **kwargs):
            return cmd_callback(*args, io=get_global_controller().io, **kwargs)

        new_callback = wrap(cmd_callback, wrapper)

        return new_callback
        
    # Decorate immediately if used like @pass_io (instead of @pass_io())
    if cmd_callback is not None:
        return decorator(cmd_callback)

    return decorator