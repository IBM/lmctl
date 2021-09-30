import click
import logging
import lmctl.cli.ctlmgmt as ctlmgmt
from lmctl.cli.safety_net import lm_driver_safety_net
from lmctl.cli.format import determine_format_class, TableFormat
from lmctl.utils.certificates import read_certificate_file
from lmctl.cli.cmd_tags import deprecated_tag

logger = logging.getLogger(__name__)

@deprecated_tag
@click.group(short_help='Use "lmctl create/get/delete resourcedriver"', help='deprecated in v3.0: Commands for managing Resource drivers (CP4NA orchestration 2.2+ only)')
def resourcedriver():
    logger.debug('resourcedriver')

def get_resource_driver_mgmt_driver(environment_name, config_path, pwd):
    lm_session = ctlmgmt.create_lm_session(environment_name, pwd, config_path)
    return lm_session.resource_driver_mgmt_driver

def format_resource_driver(output_format, resource_driver):
    formatter_class = determine_format_class(output_format)
    if formatter_class is TableFormat:
        formatter = formatter_class(resource_driver_headers, resource_driver_row_processor)
    else:
        formatter = formatter_class()
    result = formatter.convert_element(resource_driver)
    return result

@resourcedriver.command(help='Add a resource driver to CP4NA orchestration')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('--type', 'driver_type', default='Ansible', help='Driver type of the driver to add')
@click.option('--url', help='url of resource driver to add')
@click.option('--certificate', help='filename of a file containing the public certificate of the resource driver')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def add(environment, config, pwd, driver_type, url, certificate, output_format):
    """Add a resource driver"""
    resource_mgmt_driver = get_resource_driver_mgmt_driver(environment, config, pwd)
    new_resource_driver = {
        'type': driver_type,
        'baseUri': url
    }

    if certificate is not None:
        try:
            new_resource_driver['certificate'] = read_certificate_file(certificate)
        except IOError as e:
            click.echo('Error: reading certificate: {0}'.format(str(e)), err=True)
            exit(1)

    with lm_driver_safety_net():
        resource_driver = resource_mgmt_driver.add_resource_driver(new_resource_driver)
    click.echo(format_resource_driver(output_format, resource_driver))


@resourcedriver.command(help='Remove a resource driver from CP4NA orchestration by ID (or by type)')
@click.argument('environment')
@click.argument('driver-id', required=False)
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('--type', 'driver_type', help='Driver type used to identify the resource driver to remove. Use this instead of the driver-id argument')
def delete(environment, driver_id, config, pwd, driver_type):
    """Remove a resource driver by ID or type"""
    resource_mgmt_driver = get_resource_driver_mgmt_driver(environment, config, pwd)
    if driver_id is None:
        if driver_type is None:
            click.echo('Error: Must specify driver-id argument or type option')
            exit(1)
        with lm_driver_safety_net():
            resource_driver = resource_mgmt_driver.get_resource_driver_by_type(driver_type)
        driver_id = resource_driver['id']
        click.echo('Found resource driver matching type \'{0}\'. Id: {1}'.format(driver_type, driver_id))
    click.echo('Deleting resource driver: {0}...'.format(driver_id))
    with lm_driver_safety_net():
        resource_mgmt_driver.delete_resource_driver(driver_id)
    click.echo('Deleted resource driver: {0}'.format(driver_id))

@resourcedriver.command(help='Get resource driver by ID (or by type)')
@click.argument('environment')
@click.argument('driver-id', required=False)
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('--type', 'driver_type', help='Driver type used to identify the resource driver to get. Use this instead of the driver-id argument')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def get(environment, driver_id, config, pwd, driver_type, output_format):
    """Get resource driver"""
    resource_mgmt_driver = get_resource_driver_mgmt_driver(environment, config, pwd)
    if driver_id is None:
        if driver_type is None:
            click.echo('Error: Must specify driver-id argument or type option')
            exit(1)
        with lm_driver_safety_net():
            resource_driver = resource_mgmt_driver.get_resource_driver_by_type(driver_type)
    else:
        with lm_driver_safety_net():
            resource_driver = resource_mgmt_driver.get_resource_driver(driver_id)
    click.echo(format_resource_driver(output_format, resource_driver))

resource_driver_headers = ['id', 'type', 'baseUri']
def resource_driver_row_processor(resource_driver):
    table_row = []
    table_row.append(resource_driver.get('id', ''))
    table_row.append(resource_driver.get('type', ''))
    table_row.append(resource_driver.get('baseUri', ''))
    return table_row
