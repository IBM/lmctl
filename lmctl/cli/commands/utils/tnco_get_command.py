import click
from typing import Dict, Any, Sequence
from .identifier import Identifier, determine_identifier, strip_identifiers
from .tnco_env_command import TNCOEnvironmentCommand
from .constraints import mutually_exclusive
from lmctl.cli.controller import get_global_controller
from lmctl.cli.arguments import FileInputOption, OutputFormatOption
from lmctl.cli.format import Column, OutputFormat

__all__ = (
    'TNCOGetCommand',
)

class TNCOGetCommand(TNCOEnvironmentCommand):
    
    def __init__(self, 
                type_display_name: str, 
                *args, 
                identifiers: Sequence[Identifier] = None,
                identifier_required: bool = True,
                additional_help: str = None, 
                default_columns: Sequence[Column] = None,
                allow_file_input: bool = True,
                **kwargs
            ):
        self.type_display_name = type_display_name
        self.identifiers = identifiers
        self.identifier_required = identifier_required
        self.additional_help = additional_help
        self.default_columns = default_columns
        self.allow_file_input = allow_file_input
        if 'help' not in kwargs or kwargs['help'] is None:
            kwargs['help'] = self._build_help()
        if 'short_help' not in kwargs or kwargs['short_help'] is None:
            kwargs['short_help'] = f'Get a {self.type_display_name}'
        super().__init__(*args, **kwargs)
        if self.allow_file_input:
            file_input_option = FileInputOption()
            self.params.append(file_input_option)
        self.params.append(OutputFormatOption(default_columns=default_columns))

        self.get_behaviour = self.callback
        self.callback = self._callback

        if len(self.identifiers) > 1 or (allow_file_input and len(self.identifiers) > 0):
            exclusive_params = [(i.param_name, i.get_cli_display_name()) for i in self.identifiers]
            if allow_file_input:
                exclusive_params.append((file_input_option.name, ','.join(file_input_option.opts)))
            self.callback = mutually_exclusive(*exclusive_params)(self.callback)

    def _callback(self, 
                    *args, 
                    output_format: OutputFormat,
                    environment_name: str = None,
                    pwd: str = None,
                    client_secret: str = None,
                    token: str = None,
                    file_content: Dict[str, Any] = None,
                    **kwargs):
        identity = determine_identifier(self.identifiers, required=self.identifier_required, file_content=file_content, **kwargs)
        tnco_client = self._get_tnco_client(environment_name, pwd, client_secret, token)

        stripped_kwargs = strip_identifiers(self.identifiers, **kwargs)

        result = self.get_behaviour(*args, tnco_client=tnco_client, identity=identity, **stripped_kwargs)

        io = get_global_controller().io
        if isinstance(result, list):
            io.print(output_format.convert_list(result))
        else:
            io.print(output_format.convert_element(result))

    def _build_help(self) -> str:
        help_msg = f'Get a {self.type_display_name}'
        if not self.identifier_required:
            help_msg += f' or get a list of instances'
        if self.identifiers is not None and len(self.identifiers) > 0:
            help_msg += '\n\n'
            help_msg += self._produce_identifer_str()
        if self.additional_help:
            help_msg += f'\n\n{self.additional_help}'
        return help_msg

    def _produce_identifer_str(self) -> str:
        identifiers_str = f'Identify the {self.type_display_name} to be retrieved'

        if len(self.identifiers) == 1:
            identifiers_str += f' using the "{self.identifiers[0].get_cli_display_name()}" parameter'
        else:
            identifiers_str += ' using one parameter from [' + ', '.join([f'"{p.get_cli_display_name()}"' for p in self.identifiers]) + ']'

        if self.allow_file_input:
            attr_identifiers = [p for p in self.identifiers if p.obj_attribute is not None]
            if len(attr_identifiers) > 1:
                identifiers_str += f' or by including one of the following attributes'
                file_attr_str = ', '.join([f'"{p.obj_attribute}"' for p in attr_identifiers])
                identifiers_str += f' [{file_attr_str}] in the given object/file'
            elif len(attr_identifiers) == 1:
                identifiers_str += f' or by including the "{attr_identifiers[0].obj_attribute}" attribute in the given object/file'
        return identifiers_str