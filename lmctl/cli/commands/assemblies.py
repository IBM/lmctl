import click
from .utils import TNCOCommandBuilder, Identity, Identifier, pass_io
from .actions import changestate, adopt
from lmctl.cli.io import IOController
from lmctl.cli.arguments import set_param_option
from lmctl.client import TNCOClient, TNCOClientHttpError
from lmctl.cli.format import Column
from typing import Dict, Any, Tuple

__all__ = (
    'generate_assembly',
    'create_assembly',
    'update_assembly',
    'delete_assembly',
    'get_assembly'
)

default_columns = [
    Column('id', header='ID'),
    Column('name', header='Name'),
    Column('descriptorName', header='Descriptor Name'),
    Column('state', header='State')
]

tnco_builder = TNCOCommandBuilder(
    singular='assembly',
    plural='assemblies',
    display_name='Assembly'
)

name_arg = Identifier(
    param_name='name',
    obj_attribute='assemblyName'
)
id_opt = Identifier(
    param_name='id',
    obj_attribute='assemblyId',
    param_opts=['--id']
)
name_contains_opt = Identifier(
    param_name='name_contains',
    param_opts=['--name-contains']
)
top_N_opt = Identifier(
    param_name='topn',
    param_opts=['--topN']
)

accepted_process_prefix = 'Accepted - Process: '

@tnco_builder.make_generate_command()
def generate_assembly():
    return {
            'name': 'example',
            'assemblyName': 'assembly::example::1.0',
            'intendedState': 'Active',
            'properties': {
                'examplePropA': 'exampleValue'
            }
        }

create_help_str = f'''\
The request can include the following parameters:
\n\nassemblyName - A unique name by which this {tnco_builder.display_name} will be known externally. This cannot contain spaces, consecutive underscores or start with a numeric character.\
\n\ndescriptorName - The descriptor name from which this {tnco_builder.display_name} will be created\
\n\nintendedState - The final intended state that the {tnco_builder.display_name} should be brought into
\n\nproperties - An optional map of name and value pairs supplied to the new {tnco_builder.display_name}
'''

@tnco_builder.make_create_command(
    result_prefix=accepted_process_prefix,
    additional_help=create_help_str
)
@set_param_option('--prop', 'prop_values', help='Directly set a property passed to the request')
def create_assembly(tnco_client: TNCOClient, obj: Dict[str, Any], prop_values: Dict[str, Any] = None):
    if prop_values is not None:
        if 'properties' not in obj:
            obj['properties'] = prop_values
        else:
            obj['properties'].update(prop_values)
    process_id = tnco_client.assemblies.intent_create(obj)
    return process_id

update_help_str = f'''\
The request can include the following parameters:
\n\n\tdescriptorName - The descriptor name from which this {tnco_builder.display_name} will be updated to\
\n\n\tproperties - An optional map of name and string value properties that is supplied to the updated {tnco_builder.display_name}\
\n\n Examples:
\n\nUpgrade {tnco_builder.display_name} using file: lmctl update assembly -f my-request.yaml
\n\nUpgrade {tnco_builder.display_name} by name: lmctl update assembly my-assembly-name --set descriptorName=assembly::my-service::2.0
\n\nUpgrade {tnco_builder.display_name} by ID: lmctl update assembly --id bd83f0df-1e82-48ac-8faa-1d772e0c49cd --set descriptorName=assembly::my-service::2.0
'''

@tnco_builder.make_update_command(
    identifiers=[id_opt, name_arg],
    result_prefix=accepted_process_prefix,
    additional_help=update_help_str,
    allow_patch=False
)
@click.argument(name_arg.param_name, required=False)
@click.option(*id_opt.param_opts, help='Reference the target Assembly by ID instead of name')
@set_param_option('--prop', 'prop_values', help='Directly set a property passed to the request')
def update_assembly(tnco_client: TNCOClient, identity: Identity, obj: Dict[str, Any], prop_values: Dict[str, Any] = None):
    obj[identity.identifier.obj_attribute] = identity.value
    if prop_values is not None:
        if 'properties' not in obj:
            obj['properties'] = prop_values
        else:
            obj['properties'].update(prop_values)
    process_id = tnco_client.assemblies.intent_upgrade(obj)
    return process_id

@tnco_builder.make_get_command(
    identifiers=[name_arg, id_opt, name_contains_opt, top_N_opt],
    identifier_required=True,
    default_columns=default_columns
)
@click.argument(name_arg.param_name, required=False)
@click.option(*id_opt.param_opts, help='Get by ID')
@click.option(*name_contains_opt.param_opts, help='Partial name search string')
@click.option(*top_N_opt.param_opts, is_flag=True, help=f'Get {tnco_builder.display_name} instances that have recently changed')
def get_assembly(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.assemblies
    identifier_param_used = identity.identifier.param_name
    if identifier_param_used == name_contains_opt.param_name:
        return api.all_with_name_containing(identity.value).get('assemblies', [])
    elif identifier_param_used == top_N_opt.param_name:
        return api.get_topN()
    elif identifier_param_used == id_opt.param_name:
        return api.get(identity.value)
    else:
        return api.get_by_name(identity.value)

def missing_detector(e: Exception) -> Tuple[bool, str]:
    if isinstance(e, TNCOClientHttpError):
        if e.status_code == 400 and ('Cannot find assembly instance with name' in e.detail_message or 'Cannot find assembly instance with id' in e.detail_message):
            return True, e.detail_message
    return False, None

@tnco_builder.make_delete_command(
    identifiers=[name_arg, id_opt],
    missing_detector=missing_detector,
    result_prefix=accepted_process_prefix
)
@click.argument(name_arg.param_name, required=False)
@click.option(*id_opt.param_opts, help='Reference the target Assembly by ID instead of name')
def delete_assembly(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.assemblies
    identifier_param_used = identity.identifier.param_name
    if identifier_param_used == id_opt.param_name:
        delete_req = {'assemblyId': identity.value}
    else:
        delete_req = {'assemblyName': identity.value}
    process_id = api.intent_delete(delete_req)
    return process_id

def ensure_assembly_identified(identity: Identity, obj: Dict[str, Any]):
    if identity.identifier.param_name == name_arg.param_name:
        obj['assemblyName'] = identity.value
        obj.pop('assemblyId', None)
    else:
        obj['assemblyId'] = identity.value
        obj.pop('assemblyName', None)

change_state_help_suffix = f'''\
For example:
\n\nChange state using file: lmctl changestate assembly -f my-request.yaml
\n\nChange state by name: lmctl changestate assembly my-assembly-name --intended-state Inactive
\n\nChange state by ID: lmctl changestate assembly --id bd83f0df-1e82-48ac-8faa-1d772e0c49cd --intended-state Inactive
'''

@tnco_builder.make_general_command(
    group=changestate,
    short_help=f'Request an intent to change state of an {tnco_builder.display_name}',
    help_prefix=f'Request an intent to change state of an {tnco_builder.display_name}',
    help_suffix=change_state_help_suffix,
    identifiers=[name_arg, id_opt],
    pass_file_content=True
)
@click.argument(name_arg.param_name, required=False)
@click.option(*id_opt.param_opts, help='Reference the target Assembly by ID instead of name')
@click.option('--intended-state', '--state', help='Intended state to change to, if not included in "-f, --file" option')
@pass_io
def change_assembly_state(tnco_client: TNCOClient, identity: Identity, obj: Dict[str, Any], intended_state: str, io: IOController):
    if intended_state is not None:
        obj['intendedState'] = intended_state
    if 'intendedState' not in obj:
        raise click.UsageError(message=f'Must set "--intended-state, --state" option or include "intendedState" attribute in content of file passed to "-f, --file" option to change Assembly state', ctx=click.get_current_context())
    ensure_assembly_identified(identity, obj)

    process_id = tnco_client.assemblies.intent_change_state(obj)
    io.print(f'{accepted_process_prefix}{process_id}')

adopt_help_str = f'''\
Request an intent to adopt an {tnco_builder.display_name}. The request can include the following properties:
\n\nassemblyName - A unique name by which this {tnco_builder.display_name} will be known externally. This cannot contain spaces, consecutive underscores or start with a numeric character.\
\n\ndescriptorName - The descriptor name from which this {tnco_builder.display_name} will be created\
\n\nintendedState - The final intended state that the {tnco_builder.display_name} should be brought into
\n\nproperties - An optional map of name and string value properties that is supplied to the new {tnco_builder.display_name}
\n\nclusters - An optional map of cluster sizes, if the descriptor includes clusters\
\n\nresources - Associated topology for each resource instance
'''

@tnco_builder.make_general_command(
    group=adopt,
    short_help=f'Request an intent to adopt an {tnco_builder.display_name}',
    help=adopt_help_str,
    pass_file_content=True
)
@set_param_option('--prop', 'prop_values', help='Directly set a property passed to the request')
@pass_io
def adopt_assembly(tnco_client: TNCOClient, obj: Dict[str, Any], io: IOController, prop_values: Dict[str, Any]):
    if prop_values is not None:
        if 'properties' not in obj:
            obj['properties'] = prop_values
        else:
            obj['properties'].update(prop_values)
    process_id = tnco_client.assemblies.intent_adopt(obj)
    io.print(f'{accepted_process_prefix}{process_id}')
