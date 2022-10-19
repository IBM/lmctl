import click
from .actions import execute
from .utils import TNCOCommandBuilder, Identity, Identifier, pass_io, shallow_merge_objs
from lmctl.client import TNCOClient
from lmctl.cli.format import Column
from lmctl.cli.io import IOController
from lmctl.cli.arguments import set_param_option, file_input_option
from typing import Dict, Any, Type

__all__ = (
    'generate_scenario',
    'create_scenario',
    'update_scenario',
    'delete_scenario',
    'get_scenario'
)

tnco_builder = TNCOCommandBuilder(
    singular='scenario',
    plural='scenarios',
    display_name='Scenario'
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
    Column('description', header='Description')
]

@tnco_builder.make_generate_command()
def generate_scenario():
    return {
            'name': 'Example',
            'projectId': 'assembly::example::1.0',
            'description': 'An example scenario',
            'stages': [
                {
                    'name': 'Default Stage',
                    'steps': [
                        {
                            'stepDefinitionName': 'Utilities::SleepForTime',
                            'properties': {
                                'sleepTime': '10',
                                'timeUnit': 'seconds'
                            }
                        }
                    ]
                }
            ],
            'assemblyActors': []
        }


@tnco_builder.make_create_command()
def create_scenario(tnco_client: TNCOClient, obj: Dict[str, Any]):
    result = tnco_client.behaviour_scenarios.create(obj)
    return result['id'] + ' (' + result['name'] + ')'

@tnco_builder.make_update_command(
    identifiers=[id_arg]
)
@click.argument(id_arg.param_name, required=False)
def update_scenario(tnco_client: TNCOClient, identity: Identity, obj: Dict[str, Any], patchable: bool):
    if patchable:
        patch_values = obj
        obj = tnco_client.behaviour_scenarios.get(identity.value)
        obj.update(patch_values)
    else:
        obj['id'] = identity.value
    tnco_client.behaviour_scenarios.update(obj)
    return obj['id'] + ' (' + obj['name'] + ')'

@tnco_builder.make_get_command(
    identifiers=[id_arg, project_id_opt],
    identifier_required=True,
    default_columns=default_columns
)
@click.argument(id_arg.param_name, required=False)
@click.option(*project_id_opt.param_opts, required=False, help='Retrieve all Scenarios in a given Project')
def get_scenario(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.behaviour_scenarios
    if identity.identifier.param_name == project_id_opt.param_name:
        return api.all_in_project(project_id=identity.value)
    else:
        return api.get(id=identity.value)

@tnco_builder.make_delete_command(identifiers=[id_arg])
@click.argument(id_arg.param_name, required=False)
def delete_scenario(tnco_client: TNCOClient, identity: Identity):
    config_id = identity.value
    tnco_client.behaviour_scenarios.delete(id=config_id)
    return config_id

@tnco_builder.make_general_command(
    group=execute,
    short_help=f'Execute a {tnco_builder.display_name}',
    help_prefix=f'Execute a {tnco_builder.display_name}',
    identifiers=[id_arg]
)
@click.argument(id_arg.param_name, required=False)
@set_param_option(help='Set parameters on the execution request')
@file_input_option('-r', '--request', '--request-file', 'request_file', help='Path to file with execution request parameters')
@pass_io
def execute_scenario(tnco_client: TNCOClient, identity: Identity, io: IOController, set_values: Dict[str, Any], request_file: Dict[str, Any]):
    execution_request = shallow_merge_objs(request_file, set_values)
    execution_id = tnco_client.behaviour_scenario_execs.execute(scenario_id=identity.value, execution_request=execution_request)
    io.print(f'Accepted - Scenario Execution: {execution_id}')