from typing import TypeVar, Callable, Any, cast
from functools import update_wrapper

__all__ = (
    'Func',
    'FuncDecorator',
    'wrap',
)

# Func is a function with any valid call signature and can return anything
Func = TypeVar('Func', bound=Callable[..., Any])

# Decorator is a function which accepts a function and returns a new function
FuncDecorator = TypeVar('FuncDecorator', bound=Callable[[Func], Func])


def wrap(orig_f, new_f):
    return update_wrapper(cast(Func, new_f), orig_f)
