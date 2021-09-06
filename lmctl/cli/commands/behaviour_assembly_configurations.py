import click
from .utils import TNCOCommandBuilder, Identity, Identifier
from lmctl.client import TNCOClient
from lmctl.cli.format import Column
from typing import Dict, Any, Type

__all__ = (
    'generate_assembly_configuration',
    'create_assembly_configuration',
    'update_assembly_configuration',
    'delete_assembly_configuration',
    'get_assembly_configuration'
)

tnco_builder = TNCOCommandBuilder(
    singular='assemblyconfig',
    plural='assemblyconfigs',
    display_name='Assembly Configuration'
)

id_arg = Identifier.arg_and_attr('id')

project_id_opt = Identifier(
    param_name='project',
    obj_attribute='projectId',
    param_opts=['--project']
)

default_columns = [
    Column('id', header='ID'),
    Column('name', header='Name'),
    Column('description', header='Description'),
    Column('descriptorName', header='Descriptor Name')
]

@tnco_builder.make_generate_command()
def generate_assembly_configuration():
    return {
            'name': 'example',
            'projectId': 'assembly::example::1.0',
            'description': 'Example Assembly Configuration. projectId determines the descriptor project this config will be added to',
            'descriptorName': 'assembly::example::1.0',
            'properties': {
                'propA': 'exampleValue'
            }
        }


@tnco_builder.make_create_command()
def create_assembly_configuration(tnco_client: TNCOClient, obj: Dict[str, Any]):
    result = tnco_client.behaviour_assembly_configs.create(obj)
    return result['id'] + ' (' + result['name'] + ')'

@tnco_builder.make_update_command(
    identifiers=[id_arg]
)
@click.argument(id_arg.param_name, required=False)
def update_assembly_configuration(tnco_client: TNCOClient, identity: Identity, obj: Dict[str, Any], patchable: bool):
    if patchable:
        patch_values = obj
        obj = tnco_client.behaviour_assembly_configs.get(identity.value)
        obj.update(patch_values)
    else:
        obj['id'] = identity.value
    tnco_client.behaviour_assembly_configs.update(obj)
    return obj['id'] + ' (' + obj['name'] + ')'

@tnco_builder.make_get_command(
    identifiers=[id_arg, project_id_opt],
    identifier_required=True,
    default_columns=default_columns
)
@click.argument(id_arg.param_name, required=False)
@click.option(*project_id_opt.param_opts, required=False, help='Retrieve all Assembly Configurations in a given Project')
def get_assembly_configuration(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.behaviour_assembly_configs
    if identity.identifier.param_name == project_id_opt.param_name:
        return api.all_in_project(project_id=identity.value)
    else:
        return api.get(id=identity.value)

@tnco_builder.make_delete_command(identifiers=[id_arg])
@click.argument(id_arg.param_name, required=False)
def delete_assembly_configuration(tnco_client: TNCOClient, identity: Identity):
    config_id = identity.value
    tnco_client.behaviour_assembly_configs.delete(id=config_id)
    return config_id
