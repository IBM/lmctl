import click
from typing import Dict
from lmctl.client import TNCOClient, TNCOClientHttpError
from lmctl.cli.arguments import common_output_format_handler
from lmctl.cli.format import Table, Column
from .tnco_target import TNCOTarget, LmGet, LmCreate, LmUpdate, LmDelete, LmGen

class DeploymentLocationTable(Table):
    
    columns = [
        Column('name', header='Name'),
        Column('resourceManager', header='Resource Manager'),
        Column('infrastructureType', header='Infrastructure Type'),
        Column('description', header='Description')
    ]

output_formats = common_output_format_handler(table=DeploymentLocationTable())
    
class DeploymentLocations(TNCOTarget):
    name = 'deploymentlocation'
    plural = 'deploymentlocations'
    display_name = 'Deployment Location'

    @LmGen()
    def genfile(self, ctx: click.Context, name: str):
        return {
            'name': name,
            'resourceManager': 'brent',
            'infrastructureType': 'Other',
            'infrastructureSpecificProperties': {
                'locationPropertyA': 'valueA'
            }
        }

    @LmGet(output_formats=output_formats, help=f'''\
                                            Get all {display_name}s or get by name or get by partial name match\
                                            \n\nUse NAME argument to get by name\
                                            \n\nOmit NAME argument to get all\
                                            \n\nOmit NAME argument and use --name-contains option to get by partial name match''')
    @click.argument('name', required=False)
    @click.option('--name-contains', help='Partial name search string')
    def get(self, tnco_client: TNCOClient, ctx: click.Context, name: str = None, name_contains: str = None):
        api = tnco_client.deployment_locations
        if name is not None:
            if name_contains is not None:
                raise click.BadArgumentUsage('Do not use "NAME" argument when using the "--name-contains" option', ctx=ctx)
            return api.get(name)
        elif name_contains is not None:
            return api.all_with_name(name_contains)
        else:
            return api.all() 
        
    @LmCreate()
    def create(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None):
        api = tnco_client.deployment_locations
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-f, --file" option', ctx=ctx)
            deployment_location = file_content
        else:
            deployment_location = set_values
        result = api.create(deployment_location)
        return result.get('name')

    @LmUpdate()
    @click.argument('name', required=False)
    def update(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, name: str = None, set_values: Dict = None):
        api = tnco_client.deployment_locations
        if file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            deployment_location = file_content
        else:
            if name is None:
                raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
            deployment_location = api.get(name)
            deployment_location.update(set_values)
        if 'id' not in deployment_location:
            deployment_location['id'] = deployment_location.get('name', None)
        result = api.update(deployment_location)
        return deployment_location.get('name')

    @LmDelete()
    @click.argument('name', required=False)
    def delete(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, name: str = None, ignore_missing: bool = None):
        api = tnco_client.deployment_locations
        if file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            deployment_location = file_content
            deployment_location_id = deployment_location.get('id', deployment_location.get('name', None))
            if deployment_location_id is None:
                raise click.BadArgumentUsage(message='Object from file does not contain an "id" or "name" attribute', ctx=ctx)
        else:
            if name is None:
                raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
            deployment_location_id = name
        try:
            result = api.delete(deployment_location_id)
        except TNCOClientHttpError as e:
            if e.status_code == 404:
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    ctl.io.print(f'No {self.display_name} found with name {deployment_location_id} (ignoring)')
                    return
            raise
        return deployment_location_id