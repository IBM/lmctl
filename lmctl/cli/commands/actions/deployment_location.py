import click
from typing import Dict
from lmctl.client import LmClient
from lmctl.cli.arguments import common_output_format_handler
from lmctl.cli.format import Table, Column
from .lm_target import LmTarget, LmGet, LmCreate, LmUpdate, LmDelete

class DeploymentLocationTable(Table):
    
    columns = [
        Column('name', header='Name'),
        Column('resourceManager', header='Resource Manager'),
        Column('infrastructureType', header='Infrastructure Type'),
        Column('description', header='Description')
    ]

output_formats = common_output_format_handler(table=DeploymentLocationTable())
    
class DeploymentLocation(LmTarget):
    name = 'deploymentlocation'
    plural = 'deploymentlocations'
    display_name = 'Deployment Location'

    @LmGet(output_formats=output_formats, help=f'''
                                            Get all {display_name}s or get by name or get by partial name match\
                                            - Use NAME argument to get by name\
                                            - Omit NAME argument to get all\
                                            - Omit name and use --name-contains option to get by partial name match''')
    @click.argument('name', required=False)
    @click.option('--name-contains', help='Partial name search string')
    def get(self, lm_client: LmClient, ctx: click.Context, name: str = None, name_contains: str = None):
        api = lm_client.deployment_locations
        if name is not None:
            if name_contains is not None:
                raise click.BadArgumentUsage('Do not use "NAME" argument when using the "--name-contains" option', ctx=ctx)
            return api.get(name)
        elif name_contains is not None:
            return api.all_with_name(name_contains)
        else:
            return api.all() 
        
    @LmCreate()
    def create(self, lm_client: LmClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None):
        api = lm_client.deployment_locations
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "set" option when using "-f, --file" option', ctx=ctx)
            deployment_location = file_content
        else:
            deployment_location = set_values
        result = api.create(deployment_location)
        return result.get('name')

    @LmUpdate()
    @click.argument('name', required=False)
    def update(self, lm_client: LmClient, ctx: click.Context, file_content: Dict = None, name: str = None, set_values: Dict = None):
        api = lm_client.deployment_locations
        if file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            deployment_location = file_content
        else:
            if name is None:
                raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
            deployment_location = set_values
            deployment_location['name'] = name
        if 'id' not in deployment_location:
            deployment_location['id'] = deployment_location.get('name', None)
        result = api.update(deployment_location)
        return deployment_location.get('name')

    @LmDelete()
    @click.argument('name', required=False)
    def delete(self, lm_client: LmClient, ctx: click.Context, file_content: Dict = None, name: str = None, ignore_missing: bool = None):
        api = lm_client.deployment_locations
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
        result = api.delete(deployment_location_id)
        return deployment_location_id