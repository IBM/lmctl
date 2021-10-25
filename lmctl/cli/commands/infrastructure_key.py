import click
import logging
import os
import lmctl.cli.ctlmgmt as ctlmgmt
from lmctl.cli.safety_net import lm_driver_safety_net
from lmctl.cli.format import determine_format_class, TableFormat
from lmctl.cli.cmd_tags import deprecated_tag

logger = logging.getLogger(__name__)

@deprecated_tag
@click.group(name='key', short_help='Use "lmctl create/get/update/delete infrastructurekey"', help='deprecated in v3.0: Commands for managing shared infrastructure keys')
def key():
    logger.debug('Infrastructure Key Management')

ik_headers = ['id', 'name', 'description', 'publicKey']

def ik_row_processor(ik):
    table_row = []
    table_row.append(ik.get('id', ''))
    table_row.append(ik.get('name', ''))
    table_row.append(ik.get('description', ''))
    table_row.append(ik.get('publicKey', ''))
    return table_row

def format_ik(output_format, infrastructure_key):
    formatter_class = determine_format_class(output_format)
    if formatter_class is TableFormat:
        formatter = formatter_class(ik_headers, ik_row_processor)
    else:
        formatter = formatter_class()
    result = formatter.convert_element(infrastructure_key)
    return result

def format_ik_list(output_format, ik_list):
    formatter_class = determine_format_class(output_format)
    if formatter_class is TableFormat:
        formatter = formatter_class(ik_headers, ik_row_processor)
    else:
        formatter = formatter_class()
    result = formatter.convert_list(ik_list)
    return result

@key.command(name='list', help='List all shared infrastructure keys for an CP4NA orchestration environment')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def list_keys(environment, config, pwd, output_format):
    ik_driver = get_ik_driver(environment, config, pwd)
    with lm_driver_safety_net():
        ik_list = ik_driver.get_infrastructure_keys()
    result = format_ik_list(output_format, ik_list)
    click.echo(result)

def get_ik_driver(environment_name, config_path, pwd):
    lm_session = ctlmgmt.create_lm_session(environment_name, pwd, config_path)
    return lm_session.infrastructure_keys_driver

@key.command(name='get', help='Get details for a shared infrastructure key by name')
@click.argument('environment')
@click.argument('name')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def get(environment, name, config, pwd, output_format):
    """Get infrastructure key"""
    infrastructure_keys = get_ik_driver(environment, config, pwd)
    with lm_driver_safety_net():
        infrastructure_key = infrastructure_keys.get_infrastructure_key_by_name(name)
    if infrastructure_key is None:
        click.echo('Error: No infrastructure key with name: {0}'.format(name), err=True)
        exit(1)
    else:
        click.echo(format_ik(output_format, infrastructure_key))

@key.command(name='add', help='Add a shared infrastructure key to an CP4NA orchestration environment')
@click.argument('environment')
@click.argument('name')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('-u', '--public', 'public_key', help='path to the file containing the public key (usually a .pub)')
@click.option('-i', '--private', 'private_key', help='path to the file containing the private key (usually a .pem)')
@click.option('-d', '--description', help='description of the shared infrastructure key')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def add(environment, name, config, pwd, public_key, private_key, description, output_format):
    ik_driver = get_ik_driver(environment, config, pwd)
    new_ik = {
        'name': name,
    }

    if description is not None:
        new_ik['description'] = description

    if public_key is not None:
        loaded_public = load_key_file(public_key, 'public')
        new_ik['publicKey'] = loaded_public

    if private_key is not None:
        loaded_private = load_key_file(private_key, 'private')
        new_ik['privateKey'] = loaded_private

    with lm_driver_safety_net():
        new_ik = ik_driver.add_infrastructure_key(new_ik)
    click.echo(format_ik(output_format, new_ik))

def load_key_file(key_file, filetype):
    try:
        with open(key_file, 'r') as key_file:
            try:
                data = key_file.read()
            except IOError as e:
                logger.exception(e)
                click.echo('Error: reading {1} key file: {0}'.format(str(e), filetype), err=True)
                exit(1)
    except FileNotFoundError as e:
        logger.exception(e)
        click.echo('Error: reading {1} key file: {0}'.format(str(e), filetype), err=True)
        exit(1)
    return data

@key.command(name='delete', help='Remove a shared infrastructure key from an CP4NA orchestration environment')
@click.argument('environment')
@click.argument('name')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
def delete(environment, name, config, pwd):
    ik_driver = get_ik_driver(environment, config, pwd)
    with lm_driver_safety_net():
        ik = ik_driver.get_infrastructure_key_by_name(name)
    if ik is None:
        click.echo('Error: No infrastructure key with name: {0}'.format(name), err=True)
        exit(1)
    ik_name = ik['name']
    click.echo('Deleting infrastructure key: {0}...'.format(ik_name))
    with lm_driver_safety_net():
        ik_driver.delete_infrastructure_key(ik_name)
    click.echo('Deleted infrastructure key: {0}'.format(ik_name))
