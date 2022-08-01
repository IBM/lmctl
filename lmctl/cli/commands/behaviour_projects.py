import click
from .utils import TNCOCommandBuilder, Identity, Identifier
from lmctl.client import TNCOClient
from lmctl.cli.format import Column
from typing import Dict, Any, Type

__all__ = (
    'generate_project',
    'create_project',
    'update_project',
    'delete_project',
    'get_project'
)

tnco_builder = TNCOCommandBuilder(
    singular='behaviourproject',
    plural='behaviourprojects',
    display_name='Behaviour Project'
)

name = Identifier.arg_and_attr('name')

default_columns = [Column('name', header='Name'), Column('description', header='Description')]

@tnco_builder.make_generate_command()
def generate_project():
    return {
            'name': f'assembly::example::1.0',
        }

@tnco_builder.make_create_command()
def create_project(tnco_client: TNCOClient, obj: Dict[str, Any]):
    tnco_client.behaviour_projects.create(obj)
    return obj['name']

@tnco_builder.make_update_command(identifiers=[name])
@click.argument(name.param_name, required=False)
def update_project(tnco_client: TNCOClient, identity: Identity, obj: Dict[str, Any], patchable: bool):
    if patchable:
        patch_values = obj
        obj = tnco_client.behaviour_projects.get(identity.value)
        obj.update(patch_values)
    else:
        obj['name'] = identity.value
    tnco_client.behaviour_projects.update(obj)
    return obj['name']

@tnco_builder.make_get_command(
    identifiers=[name],
    identifier_required=False,
    default_columns=default_columns
)
@click.argument(name.param_name, required=False)
def get_project(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.behaviour_projects
    if identity is not None:
        project_name = identity.value
        return api.get(project_name)
    else:
        return api.all()

@tnco_builder.make_delete_command(identifiers=[name])
@click.argument(name.param_name, required=False)
def delete_project(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.behaviour_projects
    project_name = identity.value
    api.delete(project_name)
    return project_name
