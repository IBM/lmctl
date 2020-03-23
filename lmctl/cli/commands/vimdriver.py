import click
import logging
import lmctl.cli.ctlmgmt as ctlmgmt
import lmctl.cli.clirunners as clirunners
from lmctl.cli.format import determine_format_class, TableFormat
from lmctl.utils.certificates import read_certificate_file

logger = logging.getLogger(__name__)

@click.group(help='Commands for managing VIM drivers')
def vimdriver():
    logger.debug('vimdriver')

def get_vim_driver_mgmt_driver(environment_name, config_path, pwd):
    lm_session = ctlmgmt.create_lm_session(environment_name, pwd, config_path)
    return lm_session.vim_driver_mgmt_driver

def format_vim_driver(output_format, vim_driver):
    formatter_class = determine_format_class(output_format)
    if formatter_class is TableFormat:
        formatter = formatter_class(vim_driver_headers, vim_driver_row_processor)
    else:
        formatter = formatter_class()
    result = formatter.convert_element(vim_driver)
    return result

@vimdriver.command(help='Add a VIM driver to LM')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', 'inf_type', default='Openstack', help='Infrastructure type of the VIM driver to add')
@click.option('--url', help='url of VIM driver to add')
@click.option('--certificate', help='filename of a file containing the public certificate of the VIM driver')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def add(environment, config, pwd, inf_type, url, certificate, output_format):
    """Add a VIM driver"""
    vim_mgmt_driver = get_vim_driver_mgmt_driver(environment, config, pwd)
    new_vim_driver = {
        'infrastructureType': inf_type,
        'baseUri': url
    }

    if certificate is not None:
        try:
            new_vim_driver['certificate'] = read_certificate_file(certificate)
        except IOError as e:
            click.echo('Error: reading certificate: {0}'.format(str(e)), err=True)
            exit(1)

    with clirunners.lm_driver_safety():
        vim_driver = vim_mgmt_driver.add_vim_driver(new_vim_driver)
    click.echo(format_vim_driver(output_format, vim_driver))


@vimdriver.command(help='Remove a VIM driver from LM by ID (or by infrastructure type)')
@click.argument('environment')
@click.argument('driver-id', required=False)
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', 'inf_type', help='Infrastructure type used to identify the VIM driver to remove. Use this instead of the driver-id argument')
def delete(environment, driver_id, config, pwd, inf_type):
    """Remove a VIM driver by ID or type"""
    vim_mgmt_driver = get_vim_driver_mgmt_driver(environment, config, pwd)
    if driver_id is None:
        if inf_type is None:
            click.echo('Error: Must specify driver-id argument or type option')
            exit(1)
        with clirunners.lm_driver_safety():
            vim_driver = vim_mgmt_driver.get_vim_driver_by_type(inf_type)
        driver_id = vim_driver['id']
        click.echo('Found VIM driver matching type \'{0}\'. Id: {1}'.format(inf_type, driver_id))
    click.echo('Deleting VIM driver: {0}...'.format(driver_id))
    with clirunners.lm_driver_safety():
        vim_mgmt_driver.delete_vim_driver(driver_id)
    click.echo('Deleted VIM driver: {0}'.format(driver_id))

@vimdriver.command(help='Get VIM driver by ID (or by infrastructure type)')
@click.argument('environment')
@click.argument('driver-id', required=False)
@click.option('--config', default=None, help='configuration file')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
@click.option('--type', 'inf_type', help='Infrastructure type used to identify the VIM driver to get. Use this instead of the driver-id argument')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def get(environment, driver_id, config, pwd, inf_type, output_format):
    """Get VIM driver"""
    vim_mgmt_driver = get_vim_driver_mgmt_driver(environment, config, pwd)
    if driver_id is None:
        if inf_type is None:
            click.echo('Error: Must specify driver-id argument or type option')
            exit(1)
        with clirunners.lm_driver_safety():
            vim_driver = vim_mgmt_driver.get_vim_driver_by_type(inf_type)
    else:
        with clirunners.lm_driver_safety():
            vim_driver = vim_mgmt_driver.get_vim_driver(driver_id)
    click.echo(format_vim_driver(output_format, vim_driver))

vim_driver_headers = ['id', 'infrastructureType', 'baseUri']
def vim_driver_row_processor(vim_driver):
    table_row = []
    table_row.append(vim_driver.get('id', ''))
    table_row.append(vim_driver.get('infrastructureType', ''))
    table_row.append(vim_driver.get('baseUri', ''))
    return table_row
