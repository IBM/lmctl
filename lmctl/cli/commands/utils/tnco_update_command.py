import click
from typing import Dict, Any, Sequence
from .tnco_env_command import TNCOEnvironmentCommand
from .obj_utils import shallow_merge_objs
from .identifier import Identifier, determine_identifier, strip_identifiers
from .constraints import mutually_exclusive
from lmctl.cli.controller import get_global_controller
from lmctl.cli.arguments import FileInputOption, SetParamOption

__all__ = (
    'TNCOUpdateCommand',
)

class TNCOUpdateCommand(TNCOEnvironmentCommand):
    
    def __init__(self, 
                type_display_name: str, 
                *args, 
                identifiers: Sequence[Identifier] = None,
                print_result: bool = True, 
                result_prefix: str = 'Updated: ', 
                additional_help: str = None, 
                allow_patch: bool = True,
                **kwargs
            ):
        self.type_display_name = type_display_name
        self.identifiers = identifiers
        self.print_result = print_result
        self.result_prefix = result_prefix
        self.additional_help = additional_help
        self.allow_patch = allow_patch
        if 'help' not in kwargs or kwargs['help'] is None:
            kwargs['help'] = self._build_help()
        if 'short_help' not in kwargs or kwargs['short_help'] is None:
            kwargs['short_help'] = f'Update a {self.type_display_name}'
        super().__init__(*args, **kwargs)
        self.params.append(FileInputOption())
        self.params.append(SetParamOption())

        self.update_behaviour = self.callback
        self.callback = self._callback

        if len(self.identifiers) > 1:
            self.callback = mutually_exclusive(
                *[(i.param_name, i.get_cli_display_name()) for i in self.identifiers]
            )(self.callback)

    def _callback(self, 
                    *args, 
                    environment_name: str = None,
                    pwd: str = None,
                    client_secret: str = None,
                    token: str = None,
                    file_content: Dict[str, Any] = None,
                    set_values: Dict[str, Any] = None,
                    **kwargs):
        obj = shallow_merge_objs(file_content, set_values)
        identity = determine_identifier(self.identifiers, required=True, file_content=file_content, **kwargs)
        stripped_kwargs = strip_identifiers(self.identifiers, **kwargs)

        if self.allow_patch:
            # Patch update supported if file_content not specified
            stripped_kwargs['patchable'] = file_content is None

        tnco_client = self._get_tnco_client(environment_name, pwd, client_secret, token)
        result = self.update_behaviour(*args, tnco_client=tnco_client, obj=obj, identity=identity, **stripped_kwargs)
    
        if self.print_result:
            io = get_global_controller().io
            text = ''
            if self.result_prefix:
                text += str(self.result_prefix)
            text += str(result)
            io.print(text)

    def _build_help(self) -> str:
        help_msg = f'Update a {self.type_display_name}'
        help_msg += f'\n\nUse the "-f, --file" option to parse input data as a file in a supported format.'
        help_msg += f'\nOtherwise, use "--set" option to set attributes as key=value pairs.'
        if self.identifiers is not None and len(self.identifiers) > 0:
            help_msg += '\n\n'
            help_msg += self._produce_identifer_str()
        if self.additional_help:
            help_msg += f'\n\n{self.additional_help}'
        return help_msg

    def _produce_identifer_str(self) -> str:
        identifiers_str = f'Identify the {self.type_display_name} to be updated'

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
