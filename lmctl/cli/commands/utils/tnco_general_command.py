import click
from typing import Dict, Any, Sequence, Tuple
from .identifier import Identifier, determine_identifier, strip_identifiers
from .tnco_env_command import TNCOEnvironmentCommand
from .constraints import mutually_exclusive
from lmctl.cli.controller import get_global_controller
from lmctl.cli.arguments import FileInputOption, OutputFormatOption
from lmctl.cli.format import Column, OutputFormat

__all__ = (
    'TNCOGeneralCommand',
)

class TNCOGeneralCommand(TNCOEnvironmentCommand):
    
    def __init__(self, 
                type_display_name: str, 
                *args, 
                identifiers: Sequence[Identifier] = None,
                identifier_required: bool = True,
                additional_identifiers: Dict[str, Tuple[bool, Sequence[Identifier]]] = None,
                help_prefix: str = None,
                help_suffix: str = None, 
                allow_file_input: bool = True, 
                file_mutually_exclusive_with_identifiers: bool = True,
                pass_file_content: bool = False,
                **kwargs
            ):
        self.type_display_name = type_display_name
        self.identifiers = identifiers or []
        self.identifier_required = identifier_required
        self.help_prefix = help_prefix
        self.help_suffix = help_suffix
        self.additional_identifiers = additional_identifiers or {}
        self.allow_file_input = allow_file_input
        self.pass_file_content = pass_file_content
        if 'help' not in kwargs or kwargs['help'] is None:
            kwargs['help'] = self._build_help()
        super().__init__(*args, **kwargs)
        if allow_file_input:
            file_input_option = FileInputOption()
            self.params.append(file_input_option)

        self.behaviour = self.callback
        self.callback = self._callback

        if len(self.identifiers) > 1 or (file_mutually_exclusive_with_identifiers and allow_file_input and len(self.identifiers) > 0):
            exclusive_params = [(i.param_name, i.get_cli_display_name()) for i in self.identifiers]
            if file_mutually_exclusive_with_identifiers and allow_file_input:
                exclusive_params.append((file_input_option.name, ','.join(file_input_option.opts)))
            self.callback = mutually_exclusive(*exclusive_params)(self.callback)

        for arg_name, identifier_tplf in self.additional_identifiers.items():
            identifiers = identifier_tplf[1]
            if len(identifiers) > 0 or (file_mutually_exclusive_with_identifiers and allow_file_input and len(identifiers) > 0):
                exclusive_params = [(i.param_name, i.get_cli_display_name()) for i in identifiers]
                if file_mutually_exclusive_with_identifiers and allow_file_input:
                    exclusive_params.append((file_input_option.name, ','.join(file_input_option.opts)))
                self.callback = mutually_exclusive(*exclusive_params)(self.callback)

    def _callback(self, 
                    *args, 
                    environment_name: str = None,
                    pwd: str = None,
                    client_secret: str = None,
                    token: str = None,
                    file_content: Dict[str, Any] = None,
                    **kwargs):
        if len(self.identifiers) > 0:
            identity = determine_identifier(self.identifiers, required=self.identifier_required, file_content=file_content, **kwargs)
        tnco_client = self._get_tnco_client(environment_name, pwd, client_secret, token)

        stripped_kwargs = strip_identifiers(self.identifiers, **kwargs)
        additional_identifier_values = {}
        if len(self.additional_identifiers) > 0:
            for identifier_name, identifier_tpl in self.additional_identifiers.items():
                added_identity = determine_identifier(identifier_tpl[1], required=identifier_tpl[0], file_content=file_content, **kwargs)
                additional_identifier_values[identifier_name] = added_identity
                stripped_kwargs = strip_identifiers(identifier_tpl[1], **stripped_kwargs)
            stripped_kwargs.update(additional_identifier_values)

        if self.pass_file_content:
            stripped_kwargs['obj'] = file_content or {}

        if len(self.identifiers) > 0:
            # Add to kwargs at the end so "identity" is not stripped by accident
            stripped_kwargs['identity'] = identity

        result = self.behaviour(*args, tnco_client=tnco_client, **stripped_kwargs)

        return result

    def _build_help(self) -> str:
        help_msg = self.help_prefix or ''
        if self.identifiers is not None and len(self.identifiers) > 0:
            if len(help_msg) > 0:
                help_msg += '\n\n'
            help_msg += self._produce_identifer_str()
        if self.help_suffix:
            if len(help_msg) > 0:
                help_msg += '\n\n'
            help_msg += self.help_suffix
        return help_msg

    def _produce_identifer_str(self) -> str:
        identifiers_str = f'Identify the {self.type_display_name}'

        if len(self.identifiers) == 1:
            identifiers_str += f' using the "{self.identifiers[0].get_cli_display_name()}" parameter'
        else:
            identifiers_str += ' using one paramter from [' + ', '.join([f'"{p.get_cli_display_name()}"' for p in self.identifiers]) + ']'

        attr_identifiers = [p for p in self.identifiers if p.obj_attribute is not None]
        if len(attr_identifiers) > 1:
            identifiers_str += f' or by including one of the following attributes'
            file_attr_str = ', '.join([f'"{p.obj_attribute}"' for p in attr_identifiers])
            identifiers_str += f' [{file_attr_str}] in the given object/file'
        elif len(attr_identifiers) == 1:
            identifiers_str += f' or by including the "{attr_identifiers[0].obj_attribute}" attribute in the given object/file'
        return identifiers_str