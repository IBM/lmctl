import click
from typing import Sequence

__all__ = (
    'OutputFileOption',
    'OverwriteOption',
    'output_file_option',
    'overwrite_file_option'
)

class OutputFileOption(click.Option):
    default_param_decls = ['--path']

    def __init__(
            self, 
            *args, 
            param_decls: Sequence[str] = default_param_decls,
            required: bool = False, 
            help: str = 'Path of file to create', 
            **kwargs):
        param_decls = [p for p in param_decls]
        super().__init__(
            *args,
            param_decls,
            required=required,
            type=click.Path(writable=True),
            help=help,
            **kwargs
        )
    
def output_file_option(*args, **kwargs):
    def decorator(f):
        param_decls = args
        if len(param_decls) == 0:
            param_decls = OutputFileOption.default_param_decls
        return click.option(*param_decls, cls=OutputFileOption, **kwargs)(f)
    return decorator

class OverwriteOption(click.Option):
    default_param_decls = ['--overwrite']

    def __init__(
            self, 
            param_decls: Sequence[str] = default_param_decls,
            help: str = 'Overwrite existing file',
            default: bool = False,
            show_default: bool = True,
            **kwargs):
        param_decls = [p for p in param_decls]
        super().__init__(
            param_decls,
            is_flag=True,
            default=default,
            show_default=show_default,
            help=help,
            **kwargs
        )

def overwrite_file_option(*args, **kwargs):
    def decorator(f):
        param_decls = args
        if len(param_decls) == 0:
            param_decls = OverwriteOption.default_param_decls
        return click.option(*param_decls, cls=OverwriteOption, **kwargs)(f)
    return decorator