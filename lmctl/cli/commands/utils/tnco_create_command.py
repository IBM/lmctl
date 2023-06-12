from typing import Dict, Any
from .tnco_env_command import TNCOEnvironmentCommand
from .obj_utils import shallow_merge_objs
from .constraints import mutually_exclusive
from lmctl.cli.controller import get_global_controller
from lmctl.cli.arguments import (
    FileInputOption, SetParamOption, ObjectGroupOption, ObjectGroupIDOption, 
    OBJECT_GROUP_PARAM_NAME, OBJECT_GROUP_ID_PARAM_NAME, OBJECT_GROUP_PARAM_OPTS_STR, OBJECT_GROUP_ID_PARAM_OPTS_STR
)

__all__ = (
    'TNCOCreateCommand',
)

class TNCOCreateCommand(TNCOEnvironmentCommand):
    
    def __init__(self, 
                 type_display_name: str, 
                 *args, 
                 print_result: bool = True, 
                 result_prefix: str = 'Created: ', 
                 additional_help: str = None, 
                 allow_object_group: bool = False, 
                 **kwargs
            ):
        self.type_display_name = type_display_name
        self.result_prefix = result_prefix
        self.additional_help = additional_help
        self.print_result = print_result
        self.allow_object_group = allow_object_group
        if 'help' not in kwargs or kwargs['help'] is None:
            kwargs['help'] = self._build_help()
        if 'short_help' not in kwargs or kwargs['short_help'] is None:
            kwargs['short_help'] = f'Create a {self.type_display_name}'
        super().__init__(*args, **kwargs)
        self.params.append(FileInputOption())
        self.params.append(SetParamOption())
        if self.allow_object_group:
            self.params.append(ObjectGroupOption())
            self.params.append(ObjectGroupIDOption())

        self.create_behaviour = self.callback
        self.callback = self._callback

        if self.allow_object_group:
            self.callback = mutually_exclusive((OBJECT_GROUP_PARAM_NAME, OBJECT_GROUP_PARAM_OPTS_STR), (OBJECT_GROUP_ID_PARAM_NAME, OBJECT_GROUP_ID_PARAM_OPTS_STR))(self.callback)

    def _callback(self, 
                    *args, 
                    environment_name: str = None,
                    pwd: str = None,
                    client_secret: str = None,
                    token: str = None,
                    file_content: Dict[str, Any] = None,
                    set_values: Dict[str, Any] = None,
                    object_group_name: str = None,
                    object_group_id: str = None,
                    **kwargs):
        tnco_client = self._get_tnco_client(environment_name, pwd, client_secret, token)
        obj = shallow_merge_objs(file_content, set_values)

        if self.allow_object_group:
            if object_group_name is not None:
                kwargs['object_group_id'] = tnco_client.object_groups.get_by_name(object_group_name)['id']
            else:
                kwargs['object_group_id'] = object_group_id

        result = self.create_behaviour(*args, tnco_client=tnco_client, obj=obj, **kwargs)

        if self.print_result:
            io = get_global_controller().io
            text = ''
            if self.result_prefix:
                text += str(self.result_prefix)
            text += str(result)
            io.print(text)

    def _build_help(self) -> str:
        help_msg = f'Create a {self.type_display_name}'
        help_msg += f'\n\nUse the "-f, --file" option to parse input data as a file in a supported format.'
        help_msg += f'\nOtherwise, use "--set" option to set attributes as key=value pairs.'
        if self.additional_help:
            help_msg += f'\n\n{self.additional_help}'
        return help_msg
