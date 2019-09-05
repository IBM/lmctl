import click
import logging
import os
import lmctl.cli.ctlmgmt as ctlmgmt
from lmctl.cli.format import determine_format_class, TableFormat

logger = logging.getLogger(__name__)

vim_driver_headers = ['id', 'infrastructureType', 'baseUri']
def vim_driver_row_processor(vim_driver):
    table_row = []
    table_row.append(vim_driver.get('id', ''))
    table_row.append(vim_driver.get('infrastructureType', ''))
    table_row.append(vim_driver.get('baseUri', ''))
    return table_row

lifecycle_driver_headers = ['id', 'type', 'baseUri']
def lifecycle_driver_row_processor(vim_driver):
    table_row = []
    table_row.append(vim_driver.get('id', ''))
    table_row.append(vim_driver.get('type', ''))
    table_row.append(vim_driver.get('baseUri', ''))
    return table_row

######################################################
# Manage Brent RM drivers
######################################################
@click.group(help='Commands for managing Brent Resource Manager')
def brent():
    logger.debug('Brent Resource Manager')

@brent.command(help='Add a VIM driver to Brent')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', default='Openstack', help='Infrastructure type')
@click.option('--url', help='url of VIM driver to add to Brent')
def add_vd(environment, config, pwd, type, url):
    """Add a VIM driver"""
    brent_driver = get_brent_driver(environment, config, pwd)
    new_vim_driver = {
        'infrastructureType': type,
        'baseUri': url
    }
    click.echo('Creating VIM driver with: {0}'.format(new_vim_driver))
    click.echo(brent_driver.add_vim_driver(new_vim_driver))

@brent.command(help='Add a lifecycle driver to Brent')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', default='Ansible', help='Lifecycle type')
@click.option('--url', help='url of lifecycle driver to add to Brent')
def add_ld(environment, config, pwd, type, url):
    """Add a lifecycle driver"""
    brent_driver = get_brent_driver(environment, config, pwd)
    new_lifecycle_driver = {
        'type': type,
        'baseUri': url
    }
    click.echo('Creating Lifecycle driver with: {0}'.format(new_lifecycle_driver))
    click.echo(brent_driver.add_lifecycle_driver(new_lifecycle_driver))

@brent.command(help='Remove a Brent VIM driver')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', default='Ansible', help='Infrastructure type')
def remove_vd(environment, config, pwd, type):
    """Remove a VIM driver from Brent"""
    brent_driver = get_brent_driver(environment, config, pwd)
    vim_drivers_list = brent_driver.get_vim_drivers_by_type(type)
    if len(vim_drivers_list) == 0:
        click.echo('No VIM drivers of type: {0}'.format(type), err=True)
        exit(1)
    matched_vim_driver = vim_drivers_list[0]
    vim_driver_id = matched_vim_driver['id']
    click.echo('Deleting VIM driver with id \'{0}\'...'.format(vim_driver_id))
    brent_driver.remove_vim_driver(vim_driver_id)
    click.echo('Success: deleted VIM driver \'{0}\''.format(vim_driver_id))

@brent.command(help='Remove a Brent Lifecycle driver')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', default='Ansible', help='Lifecycle type')
def remove_ld(environment, config, pwd, type):
    """Remove a Lifecycle driver from Brent"""
    brent_driver = get_brent_driver(environment, config, pwd)
    lifecycle_drivers_list = brent_driver.get_lifecycle_drivers_by_type(type)
    if len(lifecycle_drivers_list) == 0:
        click.echo('No Lifecycle drivers of type: {0}'.format(type), err=True)
        exit(1)
    matched_lifecycle_driver = lifecycle_drivers_list[0]
    lifecycle_driver_id = matched_lifecycle_driver['id']
    click.echo('Deleting Lifecycle driver with id \'{0}\'...'.format(lifecycle_driver_id))
    brent_driver.remove_lifecycle_driver(lifecycle_driver_id)
    click.echo('Success: deleted Lifecycle driver \'{0}\''.format(lifecycle_driver_id))

@brent.command(help='Get Brent VIM driver by infrastructureType')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', default='Ansible', help='Infrastructure type')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def get_vd(environment, config, pwd, type, output_format):
    """List Brent VIM drivers"""
    brent_driver = get_brent_driver(environment, config, pwd)
    vim_drivers_list = brent_driver.get_vim_drivers_by_type(type)
    formatter_class = determine_format_class(output_format)
    if formatter_class is TableFormat:
        formatter = formatter_class(vim_driver_headers, vim_driver_row_processor)
    else:
        formatter = formatter_class()
    result = formatter.convert_list(vim_drivers_list)
    click.echo(result)

@brent.command(help='Get Brent Lifecycle driver by type')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', default='Ansible', help='Lifecycle type')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def get_ld(environment, config, pwd, type, output_format):
    """List Brent Lifecycle drivers"""
    brent_driver = get_brent_driver(environment, config, pwd)
    lifecycle_drivers_list = brent_driver.get_lifecycle_drivers_by_type(type)
    formatter_class = determine_format_class(output_format)
    if formatter_class is TableFormat:
        formatter = formatter_class(lifecycle_driver_headers, lifecycle_driver_row_processor)
    else:
        formatter = formatter_class()
    result = formatter.convert_list(lifecycle_drivers_list)
    click.echo(result)

def get_brent_driver(environment_name, config_path, pwd):
    lm_session = ctlmgmt.create_lm_session(environment_name, pwd, config_path)
    return lm_session.brent_driver
