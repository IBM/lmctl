import click
import logging
from .utils import TNCOCommandBuilder, Identity, Identifier
from lmctl.client import TNCOClient
from lmctl.cli.format import Column
from typing import Dict, Any, Type

logger = logging.getLogger(__name__)


__all__ = (
    'generate_deployment_location',
    'create_deployment_location',
    'update_deployment_location',
    'delete_deployment_location',
    'get_deployment_location',
)

tnco_builder = TNCOCommandBuilder(
    singular='deploymentlocation',
    plural='deploymentlocations',
    display_name='Deployment Location'
)

name = Identifier.arg_and_attr('name')
name_contains_opt = Identifier(
    param_name='name_contains',
    param_opts=['--name-contains']
)

default_columns = [
    Column('name', header='Name'),
    Column('resourceManager', header='Resource Manager'),
    Column('infrastructureType', header='Infrastructure Type'),
    Column('description', header='Description')
]

@tnco_builder.make_generate_command()
def generate_deployment_location():
    return {
            'name': 'Example',
            'resourceManager': 'brent',
            'infrastructureType': 'Other',
            'infrastructureSpecificProperties': {
                'locationPropertyA': 'valueA'
            }
        }

@tnco_builder.make_create_command()
def create_deployment_location(tnco_client: TNCOClient, obj: Dict[str, Any]):
    tnco_client.deployment_locations.create(obj)
    deployment_location_name = obj['name']
    return deployment_location_name

@tnco_builder.make_update_command(identifiers=[name])
@click.argument(name.param_name, required=False)
def update_deployment_location(tnco_client: TNCOClient, identity: Identity, obj: Dict[str, Any], patchable: bool):
    if patchable:
        patch_values = obj
        obj = tnco_client.deployment_locations.get(identity.value)
        obj.update(patch_values)
    else:
        obj['name'] = identity.value
        obj['id'] = identity.value
    tnco_client.deployment_locations.update(obj)
    deployment_location_name = obj['name']
    return deployment_location_name

@tnco_builder.make_get_command(
    identifiers=[name, name_contains_opt],
    identifier_required=False,
    default_columns=default_columns
)
@click.argument(name.param_name, required=False)
@click.option(*name_contains_opt.param_opts, help='Partial name search string')
def get_deployment_location(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.deployment_locations
    if identity is None:
        return api.all()
    else:
        if identity.identifier.param_name == name.param_name:
            deployment_location_name = identity.value
            return api.get(deployment_location_name)
        else:
            search_str = identity.value
            return api.all_with_name(search_str)

@tnco_builder.make_delete_command(identifiers=[name])
@click.argument(name.param_name, required=False)
def delete_deployment_location(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.deployment_locations
    deployment_location_name = identity.value
    api.delete(deployment_location_name)
    return deployment_location_name

##### Deprecated 
import yaml
import os
import json
import lmctl.cli.ctlmgmt as ctlmgmt
from lmctl.cli.safety_net import lm_driver_safety_net
from lmctl.cli.format import determine_format_class, TableFormat

@click.group(name='deployment', hidden=True, short_help='Use "lmctl create/get/update/delete deploymentlocation"', help='deprecated in v3.0: Commands for managing Deployment Locations')
def deployment():
    logger.debug('Deployment Location Management')

dl_headers = ['id', 'name', 'resourceManager', 'infrastructureType', 'description']

def dl_row_processor(dl):
    table_row = []
    table_row.append(dl.get('id', ''))
    table_row.append(dl.get('name', ''))
    table_row.append(dl.get('resourceManager', ''))
    table_row.append(dl.get('infrastructureType', ''))
    table_row.append(dl.get('description', ''))
    return table_row

def format_dl(output_format, deployment_location):
    formatter_class = determine_format_class(output_format)
    if formatter_class is TableFormat:
        formatter = formatter_class(dl_headers, dl_row_processor)
    else:
        formatter = formatter_class()
    result = formatter.convert_element(deployment_location)
    return result

def format_dl_list(output_format, dl_list):
    formatter_class = determine_format_class(output_format)
    if formatter_class is TableFormat:
        formatter = formatter_class(dl_headers, dl_row_processor)
    else:
        formatter = formatter_class()
    result = formatter.convert_list(dl_list)
    return result

@deployment.command(name='list', help='List deployment locations on an CP4NA orchestration environment')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
@click.option('--objectgroupid', default=None, help='create the new location in the specified object group')
def list_locations(environment, config, pwd, objectgroupid, output_format):
    dl_driver = get_dl_driver(environment, config, pwd)
    with lm_driver_safety_net():
        dl_list = dl_driver.get_locations(object_group_id=objectgroupid)
    result = format_dl_list(output_format, dl_list)
    click.echo(result)

@deployment.command(name='add', help='Add a deployment location to an CP4NA orchestration environment')
@click.argument('environment')
@click.argument('name')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('-r', '--rm', required=True, help='name of Resource Manager to associate the Deployment Location with')
@click.option('-i', '--infrastructure-type', help='type of infrastructure managed by the Deployment Location')
@click.option('-d', '--description', help='description of the Deployment Location')
@click.option('-p', '--properties', help='path to yaml/json file containing properties for the Deployment Location')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
@click.option('--objectgroupid', default=None, help='create the new location in the specified object group')
def add(environment, name, config, pwd, rm, infrastructure_type, objectgroupid, description, properties, output_format):
    dl_driver = get_dl_driver(environment, config, pwd, objectgroupid)
    new_dl = {
        'name': name,
        'description': description,
        'resourceManager': rm,
        'infrastructureType': infrastructure_type
    }
    if objectgroupid is not None:
        new_dl['objectGroupId'] = objectgroupid
    if properties is not None:
        loaded_properties = load_properties_file(properties)
        new_dl['infrastructureSpecificProperties'] = loaded_properties
    else:
        new_dl['infrastructureSpecificProperties'] = {}
    with lm_driver_safety_net():
        new_dl = dl_driver.add_location(new_dl)
    click.echo(format_dl(output_format, new_dl))

@deployment.command(name='delete', help='Remove a deployment location from an CP4NA orchestration environment')
@click.argument('environment')
@click.argument('name')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
def delete(environment, name, config, pwd):
    dl_driver = get_dl_driver(environment, config, pwd)
    with lm_driver_safety_net():
        dl_list = dl_driver.get_locations_by_name(name)
    if len(dl_list) == 0:
        click.echo('Error: No deployment location with name: {0}'.format(name), err=True)
        exit(1)
    matched_dl = dl_list[0]
    dl_id = matched_dl['id']
    click.echo('Deleting deployment location: {0}...'.format(dl_id))
    with lm_driver_safety_net():
        dl_driver.delete_location(dl_id)
    click.echo('Deleted deployment location: {0}'.format(dl_id))

@deployment.command(help='Get deployment location by name')
@click.argument('environment')
@click.argument('name')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def get(environment, name, config, pwd, output_format):
    dl_driver = get_dl_driver(environment, config, pwd)
    with lm_driver_safety_net():
        dl_list = dl_driver.get_locations_by_name(name)
    if len(dl_list) == 0:
        click.echo('Error: No deployment location with name: {0}'.format(name), err=True)
        exit(1)
    matched_dl = dl_list[0]
    click.echo(format_dl(output_format, matched_dl))

def load_properties_file(properties_file):
    file_name, file_extension = os.path.splitext(properties_file)
    if file_extension in ['.yaml', '.yml']:
        with open(properties_file, 'r') as yaml_file:
            try:
                data = yaml.safe_load(yaml_file)
            except yaml.YAMLError as e:
                logger.exception(e)
                click.echo('Error: failed to load YAML: {0}'.format(str(e)), err=True)
                exit(1)
    elif file_extension == '.json':
        with open(properties_file, 'r') as json_file:
            try:
                data = json.load(json_file)
            except json.JSONDecodeError as e:
                logger.exception(e)
                click.echo('Error: failed to load YAML: {0}'.format(str(e)), err=True)
                exit(1)
    else:
        click.echo('Cannot determine properties file type with extension: {0}'.format(file_extension), err=True)
        exit(1)
    return data

def get_dl_driver(environment_name, config_path, pwd, object_group_id=None):
    lm_session = ctlmgmt.create_lm_session(environment_name, pwd, config_path, object_group_id)
    return lm_session.deployment_location_driver
