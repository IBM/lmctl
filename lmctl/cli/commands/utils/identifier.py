import click
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Any, Dict

__all__ = (
    'Identifier',
    'determine_identifier',
    'Identity'
)

@dataclass
class Identifier:
    obj_attribute: Optional[str] = None
    param_name: Optional[str] = None
    param_opts: Optional[List[str]] = field(default_factory=list)

    def get_cli_display_name(self):
        if len(self.param_opts) > 0:
            return ', '.join(self.param_opts)
        return self.param_name

    @staticmethod
    def arg_and_attr(name):
        return Identifier(
            obj_attribute=name,
            param_name=name
        )

@dataclass
class Identity:
    identifier: Identifier
    value: Any
    from_file: bool = False
    from_params: bool = True

def strip_identifiers(identifiers, **input_param_values):
    # strip identifier args
    name_of_identifiers = [i.param_name for i in identifiers if i.param_name]
    stripped = {
        k:v for k,v in input_param_values.items() if k not in name_of_identifiers
    }
    return stripped

def determine_identifier(potential_identifiers: Sequence[Identifier], 
                        file_content: Dict[str, Any] = None,
                        required: bool = False,
                        **input_param_values):
    identifier_from_params = []
    identifier_from_file = []
    for potential_identifier in potential_identifiers:

        if has_identifier_been_specified_on_cli(potential_identifier, **input_param_values):
            identifier_from_params.append(potential_identifier)

        if has_identifier_been_specified_in_file(potential_identifier, file_content):
            identifier_from_file.append(potential_identifier)

    if len(identifier_from_params) > 0:
        # More than one identifier provided on command line
        # We just use the first one. If the params are supposed to be mutually exclusive then the user should make use of the MutuallyExclusive option
        return Identity(
            identifier=identifier_from_params[0],
            value=input_param_values.get(identifier_from_params[0].param_name),
            from_params=True
        )
    elif len(identifier_from_file) > 0:
        # No cli_params used, but the file specifies the target
        return Identity(
            identifier=identifier_from_file[0],
            value=file_content.get(identifier_from_file[0].obj_attribute),
            from_file=True
        )
    elif required:
        error_msg = 'Must identify the target by specifying'
        if len(potential_identifiers) > 1:
            error_msg += ' one parameter from'
            identifers_str = ', '.join([f'"{p.get_cli_display_name()}"' for p in potential_identifiers])
            error_msg += f' [{identifers_str}]'
        else:
            error_msg += f' the "{potential_identifiers[0].get_cli_display_name()}" parameter'
        
        attr_identifiers = [p for p in potential_identifiers if p.obj_attribute is not None]
        if len(attr_identifiers) > 1:
            error_msg += f' or by including one of the following attributes'
            file_attr_str = ', '.join([f'"{p.obj_attribute}"' for p in attr_identifiers])
            error_msg += f' [{file_attr_str}] in the given object/file'
        elif len(attr_identifiers) == 1:
            error_msg += f' or by including the "{attr_identifiers[0].obj_attribute}" attribute in the given object/file'
        raise click.UsageError(error_msg, ctx=click.get_current_context()) 
            
def has_identifier_been_specified_on_cli(identifier: Identifier, **input_param_values) -> bool:
    if identifier.param_name is None:
        return False
    param_val = input_param_values.get(identifier.param_name, None)
    return param_val is not None and param_val is not False

def has_identifier_been_specified_in_file(identifier: Identifier, file_content: Dict) -> bool:
    if identifier.obj_attribute is None:
        return False
    if file_content is None:
        return False
    value = file_content.get(identifier.obj_attribute, None)
    return value is not None and value is not False
