import click
import logging
import lmctl.cli.ctlmgmt as ctlmgmt
import lmctl.cli.clirunners as clirunners
from lmctl.cli.format import determine_format_class, TableFormat
from lmctl.utils.certificates import read_certificate_file

logger = logging.getLogger(__name__)

@click.group(help='Commands for managing Resource drivers (LM 2.2+ only)')
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

@resourcedriver.command(help='Add a resource driver to LM')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
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

    with clirunners.lm_driver_safety():
        resource_driver = resource_mgmt_driver.add_resource_driver(new_resource_driver)
    click.echo(format_resource_driver(output_format, resource_driver))


@resourcedriver.command(help='Remove a resource driver from LM by ID (or by type)')
@click.argument('environment')
@click.argument('driver-id', required=False)
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', 'driver_type', help='Driver type used to identify the resource driver to remove. Use this instead of the driver-id argument')
def delete(environment, driver_id, config, pwd, driver_type):
    """Remove a resource driver by ID or type"""
    resource_mgmt_driver = get_resource_driver_mgmt_driver(environment, config, pwd)
    if driver_id is None:
        if driver_type is None:
            click.echo('Error: Must specify driver-id argument or type option')
            exit(1)
        with clirunners.lm_driver_safety():
            resource_driver = resource_mgmt_driver.get_resource_driver_by_type(driver_type)
        driver_id = resource_driver['id']
        click.echo('Found resource driver matching type \'{0}\'. Id: {1}'.format(driver_type, driver_id))
    click.echo('Deleting resource driver: {0}...'.format(driver_id))
    with clirunners.lm_driver_safety():
        resource_mgmt_driver.delete_resource_driver(driver_id)
    click.echo('Deleted resource driver: {0}'.format(driver_id))

@resourcedriver.command(help='Get resource driver by ID (or by type)')
@click.argument('environment')
@click.argument('driver-id', required=False)
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', 'driver_type', help='Driver type used to identify the resource driver to get. Use this instead of the driver-id argument')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def get(environment, driver_id, config, pwd, driver_type, output_format):
    """Get resource driver"""
    resource_mgmt_driver = get_resource_driver_mgmt_driver(environment, config, pwd)
    if driver_id is None:
        if driver_type is None:
            click.echo('Error: Must specify driver-id argument or type option')
            exit(1)
        with clirunners.lm_driver_safety():
            resource_driver = resource_mgmt_driver.get_resource_driver_by_type(driver_type)
    else:
        with clirunners.lm_driver_safety():
            resource_driver = resource_mgmt_driver.get_resource_driver(driver_id)
    click.echo(format_resource_driver(output_format, resource_driver))

resource_driver_headers = ['id', 'type', 'baseUri']
def resource_driver_row_processor(resource_driver):
    table_row = []
    table_row.append(resource_driver.get('id', ''))
    table_row.append(resource_driver.get('type', ''))
    table_row.append(resource_driver.get('baseUri', ''))
    return table_row
