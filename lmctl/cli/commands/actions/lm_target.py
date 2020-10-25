
from .target import Target
from typing import Callable, Any
from lmctl.cli.arguments import (OutputFormats, 
                                FileInputs, 
                                default_output_format_handler, 
                                environment_name_option, 
                                default_file_inputs_handler,
                                set_param_option,
                                ignore_missing_option)
import click
import functools

class LmTarget(Target):

    def __init__(self, display_name: str = None, **kwargs):
        super().__init__(**kwargs)
        if display_name is None:
            if not hasattr(self, 'display_name'):
                self.display_name = self.name
        else:
            self.display_name = display_name
        self._populate_cmd_builders()

    def _populate_cmd_builders(self):
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if callable(attr_value) and hasattr(attr_value, '__lm_cmd_type__'):
                cmd_type = attr_value.__lm_cmd_type__
                if cmd_type == 'LmGet':
                    wrapper = self._wrap_with_builder(self._get_cmd_builder, attr_value)
                elif cmd_type == 'LmCreate':
                    wrapper = self._wrap_with_builder(self._create_cmd_builder, attr_value)
                elif cmd_type == 'LmUpdate':
                    wrapper = self._wrap_with_builder(self._update_cmd_builder, attr_value)
                elif cmd_type == 'LmDelete':
                    wrapper = self._wrap_with_builder(self._delete_cmd_builder, attr_value)
                else:
                    raise ValueError(f'Unknown value for "__lm_cmd_type__": {cmd_type}')
                setattr(self, attr_name, wrapper)

    def _wrap_with_builder(self, wrapper_function: Callable, handler_function: Callable):
        def wrapped_cmd_builder():
            return wrapper_function(handler_function)
        functools.update_wrapper(wrapped_cmd_builder, handler_function)
        return wrapped_cmd_builder

    def _get_help(self, handler_function: Callable, default_help: str = None):
        if hasattr(handler_function, '__help__'):
            return handler_function.__help__
        else:
            return default_help

    def _get_cmd_builder(self, handler_function: Callable) -> click.Command:
        if hasattr(handler_function, '__output_formats__'):
            output_formats = handler_function.__output_formats__
        else:
            output_formats = default_output_format_handler()

        # Build up a command (but don't decorate it as one yet)
        @environment_name_option()
        @output_formats.option()
        @click.pass_context
        def cmd(ctx: click.Context, environment_name: str, output_format: str, **kwargs):
            ctl = self._get_controller()
            output_formatter = output_formats.resolve_choice(output_format)
            with ctl.lm_client_safety_net():
                lm_client = ctl.get_lm_client(environment_name)
                result = handler_function(lm_client, ctx=ctx, **kwargs)
                if isinstance(result, list):
                    ctl.io.print(output_formatter.convert_list(result))
                else:
                    ctl.io.print(output_formatter.convert_element(result))

        # Add any extra arguments or options decorated on the handler_function
        if hasattr(handler_function, '__click_params__'):
            cmd.__click_params__.extend(handler_function.__click_params__)
        # Build final command
        cmd = click.command(help=self._get_help(handler_function, f'Get {self.display_name} by name'))(cmd)
        return cmd

    def _create_cmd_builder(self, handler_function: Callable) -> click.Command:
        if hasattr(handler_function, '__file_inputs__'):
            file_inputs = handler_function.__file_inputs__
        else:
            file_inputs = default_file_inputs_handler()

        @environment_name_option()
        @file_inputs.option()
        @set_param_option()
        @click.pass_context
        def cmd(ctx: click.Context, environment_name: str, file_content: Any, set_values: Any, **kwargs):
            ctl = self._get_controller()
            with ctl.lm_client_safety_net():
                lm_client = ctl.get_lm_client(environment_name)
                result = handler_function(lm_client, ctx=ctx, file_content=file_content, set_values=set_values, **kwargs)
                if result is not None:
                    ctl.io.print(f'Created: {result}')
        # Add any extra arguments or options decorated on the handler_function
        if hasattr(handler_function, '__click_params__'):
            cmd.__click_params__.extend(handler_function.__click_params__)
        # Build final command
        cmd = click.command(help=self._get_help(handler_function, f'Create {self.display_name}'))(cmd)
        return cmd

    def _update_cmd_builder(self, handler_function: Callable) -> click.Command:
        if hasattr(handler_function, '__file_inputs__'):
            file_inputs = handler_function.__file_inputs__
        else:
            file_inputs = default_file_inputs_handler()

        @environment_name_option()
        @file_inputs.option()
        @set_param_option()
        @click.pass_context
        def cmd(ctx: click.Context, environment_name: str, file_content: Any, set_values: Any, **kwargs):
            ctl = self._get_controller()
            with ctl.lm_client_safety_net():
                lm_client = ctl.get_lm_client(environment_name)
                result = handler_function(lm_client, ctx=ctx, file_content=file_content, set_values=set_values, **kwargs)
                if result is not None:
                    ctl.io.print(f'Updated: {result}')
        # Add any extra arguments or options decorated on the handler_function
        if hasattr(handler_function, '__click_params__'):
            cmd.__click_params__.extend(handler_function.__click_params__)
        # Build final command
        cmd = click.command(help=self._get_help(handler_function, f'Update {self.display_name}'))(cmd)
        return cmd

    def _delete_cmd_builder(self, handler_function: Callable) -> click.Command:
        if hasattr(handler_function, '__file_inputs__'):
            file_inputs = handler_function.__file_inputs__
        else:
            file_inputs = default_file_inputs_handler()

        @environment_name_option()
        @file_inputs.option()
        @ignore_missing_option()
        @click.pass_context
        def cmd(ctx: click.Context, environment_name: str, file_content: Any, ignore_missing: bool, **kwargs):
            ctl = self._get_controller()
            with ctl.lm_client_safety_net():
                lm_client = ctl.get_lm_client(environment_name)
                result = handler_function(lm_client, ctx=ctx, file_content=file_content, ignore_missing=ignore_missing, **kwargs)
                if result is not None:
                    ctl.io.print(f'Removed: {result}')
        # Add any extra arguments or options decorated on the handler_function
        if hasattr(handler_function, '__click_params__'):
            cmd.__click_params__.extend(handler_function.__click_params__)
        # Build final command
        cmd = click.command(help=self._get_help(handler_function, f'Remove {self.display_name}'))(cmd)
        return cmd

def LmGet(help: str = None, output_formats: OutputFormats = None):
    def decorator(f):
        if output_formats is not None:
            f.__output_formats__ = output_formats
        if help is not None:
            f.__help__ = help
        f.__lm_cmd_type__ = 'LmGet'
        return f
    return decorator

def LmCreate(help: str = None, file_inputs: FileInputs = None):
    def decorator(f):
        if file_inputs is not None:
            f.__file_inputs__ = file_inputs
        if help is not None:
            f.__help__ = help
        f.__lm_cmd_type__ = 'LmCreate'
        return f
    return decorator


def LmUpdate(help: str = None, file_inputs: FileInputs = None):
    def decorator(f):
        if file_inputs is not None:
            f.__file_inputs__ = file_inputs
        if help is not None:
            f.__help__ = help
        f.__lm_cmd_type__ = 'LmUpdate'
        return f
    return decorator

def LmDelete(help: str = None, file_inputs: FileInputs = None):
    def decorator(f):
        if file_inputs is not None:
            f.__file_inputs__ = file_inputs
        if help is not None:
            f.__help__ = help
        f.__lm_cmd_type__ = 'LmDelete'
        return f
    return decorator