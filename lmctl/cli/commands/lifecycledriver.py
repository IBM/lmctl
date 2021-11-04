import click
import logging
import lmctl.cli.ctlmgmt as ctlmgmt
from lmctl.cli.safety_net import lm_driver_safety_net
from lmctl.cli.format import determine_format_class, TableFormat
from lmctl.utils.certificates import read_certificate_file
from lmctl.cli.cmd_tags import deprecated_tag

logger = logging.getLogger(__name__)

@deprecated_tag
@click.group(short_help='Use "lmctl create/get/delete resourcedriver"', help='deprecated in v3.0: Commands for managing Lifecycle drivers (CP4NA orchestration 2.1 only)')
def lifecycledriver():
    click.echo('WARNING: lifecycledriver command support should only be used with 2.1 versions of CP4NA orchestration')

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

@lifecycledriver.command(help='Add a lifecycle driver to CP4NA orchestration')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
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

    with lm_driver_safety_net():
        lifecycle_driver = lifecycle_mgmt_driver.add_lifecycle_driver(new_lifecycle_driver)
    click.echo(format_lifecycle_driver(output_format, lifecycle_driver))


@lifecycledriver.command(help='Remove a lifecycle driver from CP4NA orchestration by ID (or by type)')
@click.argument('environment')
@click.argument('driver-id', required=False)
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('--type', 'lifecycle_type', help='Lifecycle type used to identify the lifecycle driver to remove. Use this instead of the driver-id argument')
def delete(environment, driver_id, config, pwd, lifecycle_type):
    """Remove a Lifecycle driver by ID or type"""
    lifecycle_mgmt_driver = get_lifecycle_driver_mgmt_driver(environment, config, pwd)
    if driver_id is None:
        if lifecycle_type is None:
            click.echo('Error: Must specify driver-id argument or type option')
            exit(1)
        with lm_driver_safety_net():
            lifecycle_driver = lifecycle_mgmt_driver.get_lifecycle_driver_by_type(lifecycle_type)
        driver_id = lifecycle_driver['id']
        click.echo('Found lifecycle driver matching type \'{0}\'. Id: {1}'.format(lifecycle_type, driver_id))
    click.echo('Deleting lifecycle driver: {0}...'.format(driver_id))
    with lm_driver_safety_net():
        lifecycle_mgmt_driver.delete_lifecycle_driver(driver_id)
    click.echo('Deleted lifecycle driver: {0}'.format(driver_id))

@lifecycledriver.command(help='Get lifecycle driver by ID (or by type)')
@click.argument('environment')
@click.argument('driver-id', required=False)
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('--type', 'lifecycle_type', help='Lifecycle type used to identify the lifecycle driver to get. Use this instead of the driver-id argument')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def get(environment, driver_id, config, pwd, lifecycle_type, output_format):
    """Get VIM driver"""
    lifecycle_mgmt_driver = get_lifecycle_driver_mgmt_driver(environment, config, pwd)
    if driver_id is None:
        if lifecycle_type is None:
            click.echo('Error: Must specify driver-id argument or type option')
            exit(1)
        with lm_driver_safety_net():
            lifecycle_driver = lifecycle_mgmt_driver.get_lifecycle_driver_by_type(lifecycle_type)
    else:
        with lm_driver_safety_net():
            lifecycle_driver = lifecycle_mgmt_driver.get_lifecycle_driver(driver_id)
    click.echo(format_lifecycle_driver(output_format, lifecycle_driver))

lifecycle_driver_headers = ['id', 'type', 'baseUri']
def lifecycle_driver_row_processor(lifecycle_driver):
    table_row = []
    table_row.append(lifecycle_driver.get('id', ''))
    table_row.append(lifecycle_driver.get('type', ''))
    table_row.append(lifecycle_driver.get('baseUri', ''))
    return table_row
