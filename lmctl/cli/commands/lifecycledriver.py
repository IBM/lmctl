import click
import logging
import lmctl.cli.ctlmgmt as ctlmgmt
import lmctl.cli.clirunners as clirunners
from lmctl.cli.format import determine_format_class, TableFormat
from lmctl.utils.certificates import read_certificate_file

logger = logging.getLogger(__name__)

@click.group(help='Commands for managing Lifecycle drivers')
def lifecycledriver():
    logger.debug('lifecycledriver')

def get_lifecycle_driver_mgmt_driver(environment_name, config_path, pwd):
    lm_session = ctlmgmt.create_lm_session(environment_name, pwd, config_path)
    return lm_session.lifecycle_driver_mgmt_driver

def format_lifecycle_driver(output_format, lifecycle_driver):
    formatter_class = determine_format_class(output_format)
    if formatter_class is TableFormat:
        formatter = formatter_class(lifecycle_driver_headers, lifecycle_driver_row_processor)
    else:
        formatter = formatter_class()
    result = formatter.convert_element(lifecycle_driver)
    return result

@lifecycledriver.command(help='Add a lifecycle driver to LM')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', 'lifecycle_type', default='Ansible', help='Lifecycle type of the driver to add')
@click.option('--url', help='url of lifecycle driver to add')
@click.option('--certificate', help='filename of a file containing the public certificate of the lifecycle driver')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def add(environment, config, pwd, lifecycle_type, url, certificate, output_format):
    """Add a lifecycle driver"""
    lifecycle_mgmt_driver = get_lifecycle_driver_mgmt_driver(environment, config, pwd)
    new_lifecycle_driver = {
        'type': lifecycle_type,
        'baseUri': url
    }

    if certificate is not None:
        try:
            new_lifecycle_driver['certificate'] = read_certificate_file(certificate)
        except IOError as e:
            click.echo('Error: reading certificate: {0}'.format(str(e)), err=True)
            exit(1)

    with clirunners.lm_driver_safety():
        lifecycle_driver = lifecycle_mgmt_driver.add_lifecycle_driver(new_lifecycle_driver)
    click.echo(format_lifecycle_driver(output_format, lifecycle_driver))


@lifecycledriver.command(help='Remove a lifecycle driver from LM by ID (or by type)')
@click.argument('environment')
@click.argument('driver-id', required=False)
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', 'lifecycle_type', help='Lifecycle type used to identify the lifecycle driver to remove. Use this instead of the driver-id argument')
def delete(environment, driver_id, config, pwd, lifecycle_type):
    """Remove a Lifecycle driver by ID or type"""
    lifecycle_mgmt_driver = get_lifecycle_driver_mgmt_driver(environment, config, pwd)
    if driver_id is None:
        if lifecycle_type is None:
            click.echo('Error: Must specify driver-id argument or type option')
            exit(1)
        with clirunners.lm_driver_safety():
            lifecycle_driver = lifecycle_mgmt_driver.get_lifecycle_driver_by_type(lifecycle_type)
        driver_id = lifecycle_driver['id']
        click.echo('Found lifecycle driver matching type \'{0}\'. Id: {1}'.format(lifecycle_type, driver_id))
    click.echo('Deleting lifecycle driver: {0}...'.format(driver_id))
    with clirunners.lm_driver_safety():
        lifecycle_mgmt_driver.delete_lifecycle_driver(driver_id)
    click.echo('Deleted lifecycle driver: {0}'.format(driver_id))

@lifecycledriver.command(help='Get lifecycle driver by ID (or by type)')
@click.argument('environment')
@click.argument('driver-id', required=False)
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', 'lifecycle_type', help='Lifecycle type used to identify the lifecycle driver to get. Use this instead of the driver-id argument')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def get(environment, driver_id, config, pwd, lifecycle_type, output_format):
    """Get VIM driver"""
    lifecycle_mgmt_driver = get_lifecycle_driver_mgmt_driver(environment, config, pwd)
    if driver_id is None:
        if lifecycle_type is None:
            click.echo('Error: Must specify driver-id argument or type option')
            exit(1)
        with clirunners.lm_driver_safety():
            lifecycle_driver = lifecycle_mgmt_driver.get_lifecycle_driver_by_type(lifecycle_type)
    else:
        with clirunners.lm_driver_safety():
            lifecycle_driver = lifecycle_mgmt_driver.get_lifecycle_driver(driver_id)
    click.echo(format_lifecycle_driver(output_format, lifecycle_driver))

lifecycle_driver_headers = ['id', 'type', 'baseUri']
def lifecycle_driver_row_processor(lifecycle_driver):
    table_row = []
    table_row.append(lifecycle_driver.get('id', ''))
    table_row.append(lifecycle_driver.get('type', ''))
    table_row.append(lifecycle_driver.get('baseUri', ''))
    return table_row
