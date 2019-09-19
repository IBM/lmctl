import click
import logging
import yaml
import os
import json
import lmctl.cli.ctlmgmt as ctlmgmt
from lmctl.cli.format import determine_format_class, TableFormat

logger = logging.getLogger(__name__)


@click.group(name='deployment', help='Commands for managing Deployment Locations')
def deployment():
    logger.debug('Deployment Location Management')


dl_headers = ['name', 'resourceManager', 'infrastructureType', 'description']


def dl_row_processor(dl):
    table_row = []
    table_row.append(dl.get('name', ''))
    table_row.append(dl.get('resourceManager', ''))
    table_row.append(dl.get('infrastructureType', ''))
    table_row.append(dl.get('description', ''))
    return table_row


@deployment.command(name='list', help='List deployment locations on an LM environment')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def list_locations(environment, config, pwd, output_format):
    dl_driver = get_dl_driver(environment, config, pwd)
    dl_list = dl_driver.get_locations()
    formatter_class = determine_format_class(output_format)
    if formatter_class is TableFormat:
        formatter = formatter_class(dl_headers, dl_row_processor)
    else:
        formatter = formatter_class()
    result = formatter.convert_list(dl_list)
    click.echo(result)


@deployment.command(name='add', help='Add a deployment location to an LM environment')
@click.argument('environment')
@click.argument('name')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('-r', '--rm', help='name of Resource Manager to associate the Deployment Location with')
@click.option('-i', '--infrastructure-type', help='type of infrastructure managed by the Deployment Location')
@click.option('-d', '--description', help='description of the Deployment Location')
@click.option('-p', '--properties', help='path to yaml/json file containing properties for the Deployment Location')
def add(environment, name, config, pwd, rm, infrastructure_type, description, properties):
    dl_driver = get_dl_driver(environment, config, pwd)
    new_dl = {
        'name': name,
        'description': description,
        'resourceManager': rm,
        'infrastructureType': infrastructure_type
    }
    if properties is not None:
        loaded_properties = load_properties_file(properties)
        new_dl['infrastructureSpecificProperties'] = loaded_properties
    click.echo('Creating deployment location with: {0}'.format(new_dl))
    dl_driver.add_location(new_dl)
    click.echo('Success: created deployment location \'{0}\''.format(name))


@deployment.command(name='delete', help='Remove a deployment location from an LM environment')
@click.argument('environment')
@click.argument('name')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
def delete(environment, name, config, pwd):
    dl_driver = get_dl_driver(environment, config, pwd)
    dl_list = dl_driver.get_locations_by_name(name)
    if len(dl_list) == 0:
        click.echo('Error: No deployment location with name: {0}'.format(name), err=True)
        exit(1)
    matched_dl = dl_list[0]
    dl_id = matched_dl['id']
    click.echo('Deleting deployment location with id \'{0}\'...'.format(dl_id))
    dl_driver.delete_location(dl_id)
    click.echo('Success: deleted deployment location \'{0}\''.format(dl_id))


def load_properties_file(properties_file):
    file_name, file_extension = os.path.splitext(properties_file)
    if file_extension in ['.yaml', '.yml']:
        with open(properties_file, 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)
    elif file_extension == '.json':
        with open(properties_file, 'r') as json_file:
            data = json.load(json_file)
    else:
        click.echo('Cannot determine properties file type with extension: {0}'.format(file_extension), err=True)
        exit(1)
    return data

def get_dl_driver(environment_name, config_path, pwd):
    lm_session = ctlmgmt.create_lm_session(environment_name, pwd, config_path)
    return lm_session.deployment_location_driver
