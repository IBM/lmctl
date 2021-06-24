import click
from typing import Dict
from lmctl.client import TNCOClient, TNCOClientHttpError
from lmctl.cli.arguments import common_output_format_handler
from lmctl.cli.format import Table, Column
from .tnco_target import TNCOTarget, LmGet, LmCreate, LmDelete, LmGen
from lmctl.utils.certificates import read_certificate_file, fix_newlines_in_cert

class ResourceDriverTable(Table):
    
    columns = [
        Column('id', header='ID'),
        Column('type', header='Type'),
        Column('baseUri', header='Base URI')
    ]

output_formats = common_output_format_handler(table=ResourceDriverTable())
    
class ResourceDrivers(TNCOTarget):
    name = 'resourcedriver'
    plural = 'resourcedrivers'
    display_name = 'Resource Driver'

    @LmGen()
    def genfile(self, ctx: click.Context, name: str):
        return {
            'type': name,
            'baseUri': 'https://ansible-lifecycle-driver:8293', 
            'certifcate': '<insert certificate as multi-line string here or use "--certifcate" option to provide file path to the target command>'
        }

    @LmGet(output_formats=output_formats, help=f'''\
                                            Get {display_name} by ID or type\
                                            \n\nUse ID argument to get by ID\
                                            \n\nOmit ID and use --type option to get by type''')
    @click.argument('ID', required=False)
    @click.option('--type', 'driver_type', help='Type of driver to fetch')
    def get(self, tnco_client: TNCOClient, ctx: click.Context, id: str = None, driver_type: str = None):
        api = tnco_client.resource_drivers
        if id is not None:
            if driver_type is not None:
                raise click.BadArgumentUsage('Do not use "ID" argument when using the "--type" option', ctx=ctx)
            return api.get(id)
        elif driver_type is not None:
            return api.get_by_type(driver_type)
        else:
            raise click.BadArgumentUsage('Must set either "ID" argument or "--type" option', ctx=ctx) 
        
    @LmCreate()
    @click.option('--certificate', type=click.Path(exists=True), help='Path to a file containing the public certificate of the resource driver')
    def create(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None, certificate: str = None):
        api = tnco_client.resource_drivers
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-f, --file" option', ctx=ctx)
            resource_driver = file_content
        else:
            resource_driver = set_values
        if certificate is not None:
            try:
                resource_driver['certificate'] = read_certificate_file(certificate)
            except IOError as e:
                ctl = self._get_controller()
                ctl.io.print_error(f'Error: reading certificate: {str(e)}')
                exit(1)
        elif 'certificate' in resource_driver:
            resource_driver['certificate'] = fix_newlines_in_cert(resource_driver['certificate'])
        result = api.create(resource_driver)
        return result.get('id')

    @LmDelete(help=f'''\
                Delete {display_name} by ID or type\
                \n\nUse ID argument to delete by ID\
                \n\nOmit ID and use --type option to delete by type\
                \n\nAlternatively, set a file path on the "-f, --file" option and the ID/type (discovered in that order) in this file will be used''')
    @click.argument('ID', required=False)
    @click.option('--type', 'driver_type', help='Type of driver to remove')
    def delete(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, id: str = None, driver_type: str = None, ignore_missing: bool = None):
        api = tnco_client.resource_drivers
        resource_driver_id = None
        resource_driver_type = None
        if file_content is not None:
            if id is not None:
                raise click.BadArgumentUsage(message='Do not use "ID" argument when using "-f, --file" option', ctx=ctx)
            if driver_type is not None:
                raise click.BadArgumentUsage(message='Do not use "--type" option when using "-f, --file" option', ctx=ctx)
            resource_driver = file_content
            resource_driver_id = resource_driver.get('id', None)
            if resource_driver_id is None:
                resource_driver_type = resource_driver.get('type', None)
            if resource_driver_id is None and resource_driver_type is None:
                raise click.BadArgumentUsage(message='Object from file does not contain an "id" or "type" attribute', ctx=ctx)
        elif id is not None:
            if driver_type is not None:
                raise click.BadArgumentUsage(message='Do not use "--type" option when using "ID" argument', ctx=ctx)
            resource_driver_id = id
        elif driver_type is not None:
            resource_driver_type = driver_type
        else:
            raise click.BadArgumentUsage('Must set either "ID" argument or "--type" option or "-f, --file" option', ctx=ctx)
        try:
            if resource_driver_id:
                api.delete(resource_driver_id)
                return resource_driver_id
            else:
                resource_driver_get = api.get_by_type(resource_driver_type)
                api.delete(resource_driver_get['id'])
                return resource_driver_get['id']
        except TNCOClientHttpError as e:
            if e.status_code == 404:
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    if resource_driver_id:
                        ctl.io.print(f'No {self.display_name} found with ID {resource_driver_id} (ignoring)')
                    else:
                        ctl.io.print(f'No {self.display_name} found with type {resource_driver_type} (ignoring)')
                    return
            raise