
from .target import Target
from typing import Callable, Any
from lmctl.cli.arguments import (OutputFormats, 
                                FileInputs, 
                                default_output_format_handler, 
                                environment_name_option, 
                                default_file_inputs_handler,
                                set_param_option,
                                ignore_missing_option, 
                                tnco_client_secret_option, 
                                tnco_pwd_option)
import os
import click
import functools

class TNCOTarget(Target):

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
                elif cmd_type == 'LmGen':
                    wrapper = self._wrap_with_builder(self._gen_cmd_builder, attr_value)
                elif cmd_type == 'LmCmd':
                    wrapper = self._wrap_with_builder(self._basic_cmd_builder, attr_value)
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

    def _basic_cmd_builder(self, handler_function: Callable) -> click.Command:
        # Build up a command (but don't decorate it as one yet)
        @environment_name_option()
        @tnco_client_secret_option()
        @tnco_pwd_option()
        @click.pass_context
        def cmd(ctx: click.Context, environment_name: str, pwd: str = None, client_secret: str = None, **kwargs):
            ctl = self._get_controller()
            with ctl.tnco_client_safety_net():
                tnco_client = ctl.get_tnco_client(environment_name, input_pwd=pwd, input_client_secret=client_secret)
                result = handler_function(tnco_client, ctx=ctx, **kwargs)
                if result is not None:
                    ctl.io.print(result)
        # Add any extra arguments or options decorated on the handler_function
        if hasattr(handler_function, '__click_params__'):
            cmd.__click_params__.extend(handler_function.__click_params__)
        # Build final command
        cmd_kwargs = {} if not hasattr(handler_function, '__cmd_kwargs__') else handler_function.__cmd_kwargs__
        cmd = click.command(**cmd_kwargs)(cmd)
        return cmd

    def _gen_cmd_builder(self, handler_function: Callable) -> click.Command:
        if hasattr(handler_function, '__output_formats__'):
            output_formats = handler_function.__output_formats__
        else:
            output_formats = default_output_format_handler()

        # Build up a command (but don't decorate it as one yet)
        @click.option('--path', required=False, help=f'Path to create the file (otherwise a file will be created in the current directory)')
        @click.option('--overwrite', is_flag=True, default=False, show_default=True, help='Overwrite existing file')
        @output_formats.option()
        @click.pass_context
        def cmd(ctx: click.Context, path: str, overwrite: bool, output_format: str, **kwargs):
            ctl = self._get_controller()
            output_formatter = output_formats.resolve_choice(output_format)
            name = 'example'
            if path is None:
                path = self.name
                if output_format == 'yaml':
                    path += '.yaml'
                elif output_format == 'json':
                    path += '.json'
            if os.path.exists(path) and not overwrite:
                ctl.io.print_error(f'File with name "{path}" already exists. Choose different file path or use "--overwrite" to replace the existing file')
                exit(1)
            result = handler_function(ctx=ctx, name=name, **kwargs)
            converted_result = output_formatter.convert_element(result)
            with open(path, 'w') as f:
                f.write(converted_result)
            ctl.io.print(f'Generated file: {path}')

        # Add any extra arguments or options decorated on the handler_function
        if hasattr(handler_function, '__click_params__'):
            cmd.__click_params__.extend(handler_function.__click_params__)
        # Build final command
        cmd_kwargs = {} if not hasattr(handler_function, '__cmd_kwargs__') else handler_function.__cmd_kwargs__
        if 'help' not in cmd_kwargs:
            help = f'Generate file for {self.display_name}'
            cmd_kwargs['help'] = help
        if 'short_help' not in cmd_kwargs:
            cmd_kwargs['short_help'] = f'Generate file for {self.display_name}'
        cmd = click.command(**cmd_kwargs)(cmd)
        return cmd

    def _get_cmd_builder(self, handler_function: Callable) -> click.Command:
        if hasattr(handler_function, '__output_formats__'):
            output_formats = handler_function.__output_formats__
        else:
            output_formats = default_output_format_handler()

        # Build up a command (but don't decorate it as one yet)
        @environment_name_option()
        @output_formats.option()
        @tnco_client_secret_option()
        @tnco_pwd_option()
        @click.pass_context
        def cmd(ctx: click.Context, environment_name: str, output_format: str, pwd: str = None, client_secret: str = None, **kwargs):
            ctl = self._get_controller()
            output_formatter = output_formats.resolve_choice(output_format)
            with ctl.tnco_client_safety_net():
                tnco_client = ctl.get_tnco_client(environment_name, input_pwd=pwd, input_client_secret=client_secret)
                result = handler_function(tnco_client, ctx=ctx, **kwargs)
                if isinstance(result, list):
                    ctl.io.print(output_formatter.convert_list(result))
                else:
                    ctl.io.print(output_formatter.convert_element(result))

        # Add any extra arguments or options decorated on the handler_function
        if hasattr(handler_function, '__click_params__'):
            cmd.__click_params__.extend(handler_function.__click_params__)
        # Build final command
        cmd_kwargs = {} if not hasattr(handler_function, '__cmd_kwargs__') else handler_function.__cmd_kwargs__
        if 'help' not in cmd_kwargs:
            help = f'Get {self.display_name}'
            cmd_kwargs['help'] = help
        if 'short_help' not in cmd_kwargs:
            cmd_kwargs['short_help'] = f'Get {self.display_name}'
        cmd = click.command(**cmd_kwargs)(cmd)
        return cmd

    def _create_cmd_builder(self, handler_function: Callable) -> click.Command:
        if hasattr(handler_function, '__file_inputs__'):
            file_inputs = handler_function.__file_inputs__
        else:
            file_inputs = default_file_inputs_handler()
        print_result = True
        if hasattr(handler_function, '__print_result__'):
            print_result = handler_function.__print_result__

        @environment_name_option()
        @file_inputs.option()
        @set_param_option()
        @tnco_client_secret_option()
        @tnco_pwd_option()
        @click.pass_context
        def cmd(ctx: click.Context, environment_name: str, file_content: Any, set_values: Any, pwd: str = None, client_secret: str = None, **kwargs):
            ctl = self._get_controller()
            with ctl.tnco_client_safety_net():
                tnco_client = ctl.get_tnco_client(environment_name, input_pwd=pwd, input_client_secret=client_secret)
                result = handler_function(tnco_client, ctx=ctx, file_content=file_content, set_values=set_values, **kwargs)
                if result is not None and print_result:
                    ctl.io.print(f'Created: {result}')
        # Add any extra arguments or options decorated on the handler_function
        if hasattr(handler_function, '__click_params__'):
            cmd.__click_params__.extend(handler_function.__click_params__)
        # Build final command
        cmd_kwargs = {} if not hasattr(handler_function, '__cmd_kwargs__') else handler_function.__cmd_kwargs__
        if 'help' not in cmd_kwargs:
            help = f'Create {self.display_name}'
            help += f'\n\nUse the "-f, --file" option to parse a file in a supported format: {list(file_inputs.formats.keys())}'
            help += f'\n\nOtherwise, use "--set" option to set attributes as key=value pairs'
            cmd_kwargs['help'] = help
        if 'short_help' not in cmd_kwargs:
            cmd_kwargs['short_help'] = f'Create {self.display_name}'
        cmd = click.command(**cmd_kwargs)(cmd)
        return cmd

    def _update_cmd_builder(self, handler_function: Callable) -> click.Command:
        if hasattr(handler_function, '__file_inputs__'):
            file_inputs = handler_function.__file_inputs__
        else:
            file_inputs = default_file_inputs_handler()
        print_result = True
        if hasattr(handler_function, '__print_result__'):
            print_result = handler_function.__print_result__

        @environment_name_option()
        @file_inputs.option()
        @set_param_option()
        @tnco_client_secret_option()
        @tnco_pwd_option()
        @click.pass_context
        def cmd(ctx: click.Context, environment_name: str, file_content: Any, set_values: Any, pwd: str = None, client_secret: str = None, **kwargs):
            ctl = self._get_controller()
            with ctl.tnco_client_safety_net():
                tnco_client = ctl.get_tnco_client(environment_name, input_pwd=pwd, input_client_secret=client_secret)
                result = handler_function(tnco_client, ctx=ctx, file_content=file_content, set_values=set_values, **kwargs)
                if result is not None and print_result:
                    ctl.io.print(f'Updated: {result}')
        # Add any extra arguments or options decorated on the handler_function
        if hasattr(handler_function, '__click_params__'):
            cmd.__click_params__.extend(handler_function.__click_params__)
        # Build final command
        cmd_kwargs = {} if not hasattr(handler_function, '__cmd_kwargs__') else handler_function.__cmd_kwargs__
        if 'help' not in cmd_kwargs:
            help = f'Update {self.display_name}'
            help += f'\n\nUse the "-f, --file" option to parse a file in a supported format: {list(file_inputs.formats.keys())}'
            help += f'\n\nOtherwise, use "--set" option to set attributes as key=value pairs'
            cmd_kwargs['help'] = help
        if 'short_help' not in cmd_kwargs:
            cmd_kwargs['short_help'] = f'Update {self.display_name}'
        cmd = click.command(**cmd_kwargs)(cmd)
        return cmd

    def _delete_cmd_builder(self, handler_function: Callable) -> click.Command:
        if hasattr(handler_function, '__file_inputs__'):
            file_inputs = handler_function.__file_inputs__
        else:
            file_inputs = default_file_inputs_handler()
        print_result = True
        if hasattr(handler_function, '__print_result__'):
            print_result = handler_function.__print_result__

        @environment_name_option()
        @file_inputs.option()
        @ignore_missing_option()
        @tnco_client_secret_option()
        @tnco_pwd_option()
        @click.pass_context
        def cmd(ctx: click.Context, environment_name: str, file_content: Any, ignore_missing: bool, pwd: str = None, client_secret: str = None, **kwargs):
            ctl = self._get_controller()
            with ctl.tnco_client_safety_net():
                tnco_client = ctl.get_tnco_client(environment_name, input_pwd=pwd, input_client_secret=client_secret)
                result = handler_function(tnco_client, ctx=ctx, file_content=file_content, ignore_missing=ignore_missing, **kwargs)
                if result is not None and print_result:
                    ctl.io.print(f'Removed: {result}')
        # Add any extra arguments or options decorated on the handler_function
        if hasattr(handler_function, '__click_params__'):
            cmd.__click_params__.extend(handler_function.__click_params__)
        # Build final command
        cmd_kwargs = {} if not hasattr(handler_function, '__cmd_kwargs__') else handler_function.__cmd_kwargs__
        if 'help' not in cmd_kwargs:
            help = f'Delete {self.display_name}'
            help += f'\n\n If "-f, --file" option is set then the target {self.display_name} will be discovered from this file'
            cmd_kwargs['help'] = help
        if 'short_help' not in cmd_kwargs:
            cmd_kwargs['short_help'] = f'Delete {self.display_name}'
        cmd = click.command(**cmd_kwargs)(cmd)
        return cmd

def LmGet(output_formats: OutputFormats = None, **cmd_kwargs):
    def decorator(f):
        if output_formats is not None:
            f.__output_formats__ = output_formats
        if len(cmd_kwargs) > 0:
            f.__cmd_kwargs__ = cmd_kwargs
        f.__lm_cmd_type__ = 'LmGet'
        return f
    return decorator

def LmCreate(file_inputs: FileInputs = None, print_result: bool = True, **cmd_kwargs):
    def decorator(f):
        if file_inputs is not None:
            f.__file_inputs__ = file_inputs
        f.__print_result__ = print_result
        if len(cmd_kwargs) > 0:
            f.__cmd_kwargs__ = cmd_kwargs
        f.__lm_cmd_type__ = 'LmCreate'
        return f
    return decorator


def LmUpdate(file_inputs: FileInputs = None, print_result: bool = True, **cmd_kwargs):
    def decorator(f):
        if file_inputs is not None:
            f.__file_inputs__ = file_inputs
        f.__print_result__ = print_result
        if len(cmd_kwargs) > 0:
            f.__cmd_kwargs__ = cmd_kwargs
        f.__lm_cmd_type__ = 'LmUpdate'
        return f
    return decorator

def LmDelete(file_inputs: FileInputs = None, print_result: bool = True, **cmd_kwargs):
    def decorator(f):
        if file_inputs is not None:
            f.__file_inputs__ = file_inputs
        f.__print_result__ = print_result
        if len(cmd_kwargs) > 0:
            f.__cmd_kwargs__ = cmd_kwargs
        f.__lm_cmd_type__ = 'LmDelete'
        return f
    return decorator

def LmGen(output_formats: OutputFormats = None, **cmd_kwargs):
    def decorator(f):
        if output_formats is not None:
            f.__output_formats__ = output_formats
        if len(cmd_kwargs) > 0:
            f.__cmd_kwargs__ = cmd_kwargs
        f.__lm_cmd_type__ = 'LmGen'
        return f
    return decorator

def LmCmd(**cmd_kwargs):
    def decorator(f):
        if len(cmd_kwargs) > 0:
            f.__cmd_kwargs__ = cmd_kwargs
        f.__lm_cmd_type__ = 'LmCmd'
        return f
    return decorator