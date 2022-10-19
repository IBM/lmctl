import click
import logging
from .utils import TNCOCommandBuilder, Identity, Identifier
from lmctl.client import TNCOClient
from lmctl.cli.format import Column
from lmctl.utils.certificates import read_certificate_file, fix_newlines_in_cert
from typing import Dict, Any, Type

logger = logging.getLogger(__name__)

__all__ = (
    'generate_resource_driver',
    'create_resource_driver',
    'delete_resource_driver',
    'get_resource_driver',
)

tnco_builder = TNCOCommandBuilder(
    singular='resourcedriver',
    plural='resourcedrivers',
    display_name='Resource Driver'
)

id_arg = Identifier.arg_and_attr('id')
type_opt = Identifier(
    param_name='driver_type',
    obj_attribute='infrastructureType',
    param_opts=['--type']
)

default_columns = [
    Column('id', header='ID'),
    Column('type', header='Type'),
    Column('baseUri', header='Base URI')
]

@tnco_builder.make_generate_command()
def generate_resource_driver():
    return {
            'type': 'example',
            'baseUri': 'https://ansible-lifecycle-driver:8293', 
            'certifcate': '<insert certificate as multi-line string here or use "--certifcate" option to provide file path to the target command>'
        }

@tnco_builder.make_create_command()
@click.option('--certificate', type=click.Path(exists=True), help='Path to a file containing the public certificate of the resource driver')
def create_resource_driver(tnco_client: TNCOClient, obj: Dict[str, Any], certificate: str = None):
    if certificate is not None:
        try:
            obj['certificate'] = read_certificate_file(certificate)
        except IOError as e:
            raise RuntimeError(f'Error: reading certificate: {str(e)}') from e
    elif 'certificate' in obj:
        resource_driver['certificate'] = fix_newlines_in_cert(obj['certificate'])
    resource_driver = tnco_client.resource_drivers.create(obj)
    return resource_driver['id']

@tnco_builder.make_get_command(
    identifiers=[id_arg, type_opt],
    identifier_required=True,
    default_columns=default_columns
)
@click.argument(id_arg.param_name, required=False)
@click.option(*type_opt.param_opts, type_opt.param_name, type=str, help='Type of driver to fetch')
def get_resource_driver(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.resource_drivers
    if identity.identifier.param_name == id_arg.param_name:
        driver_id = identity.value
        return api.get(driver_id)
    else:
        driver_type = identity.value
        return api.get_by_type(driver_type)

@tnco_builder.make_delete_command(identifiers=[id_arg, type_opt])
@click.argument(id_arg.param_name, required=False)
@click.option(*type_opt.param_opts, type_opt.param_name, type=str, help='Type of driver to delete')
def delete_resource_driver(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.resource_drivers
    driver_id = None
    if identity.identifier.param_name == id_arg.param_name:
        driver_id = identity.value
        api.delete(driver_id)
    else:
        driver_type = identity.value
        resource_driver = api.get_by_type(driver_type)
        driver_id = resource_driver['id']
        api.delete(driver_id)

    return driver_id



##### Deprecated 
import lmctl.cli.ctlmgmt as ctlmgmt
from lmctl.cli.safety_net import lm_driver_safety_net
from lmctl.cli.format import determine_format_class, TableFormat
from lmctl.utils.certificates import read_certificate_file

logger = logging.getLogger(__name__)


@click.group(hidden=True, short_help='Use "lmctl create/get/delete resourcedriver"', help='deprecated in v3.0: Commands for managing Resource drivers (CP4NA orchestration 2.2+ only)')
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
