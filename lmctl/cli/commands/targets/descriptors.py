import click
from typing import Dict
from lmctl.client import LmClient, LmClientHttpError
from lmctl.cli.arguments import common_output_format_handler
from lmctl.cli.format import Table, Column
from .lm_target import LmTarget, LmGet, LmCreate, LmUpdate, LmDelete

class DescriptorTable(Table):
    
    columns = [
        Column('name', header='Name'),
        Column('description', header='Description', accessor=lambda x: (x.get('description')[:75].strip() + '..') if x.get('description', None) is not None and len(x.get('description')) > 75 else x.get('description'))
    ]

output_formats = common_output_format_handler(table=DescriptorTable())
    
class Descriptors(LmTarget):
    name = 'descriptor'
    plural = 'descriptors'
    display_name = 'Descriptor'

    @LmGet(output_formats=output_formats, help=f'''\
                                            Get a summary of all {display_name}s or get the details of one by name\
                                            \n\nUse NAME argument to get one by name\
                                            \n\nOmit NAME argument to get all''')
    @click.argument('name', required=False)
    def get(self, lm_client: LmClient, ctx: click.Context, name: str = None):
        api = lm_client.descriptors
        if name is not None:
            return api.get(name)
        else:
            return api.all()
        
    @LmCreate()
    def create(self, lm_client: LmClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None):
        api = lm_client.descriptors
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "set" option when using "-f, --file" option', ctx=ctx)
            descriptor = file_content
        else:
            descriptor = set_values
        api.create(descriptor)
        return descriptor.get('name')

    @LmUpdate()
    @click.argument('name', required=False)
    def update(self, lm_client: LmClient, ctx: click.Context, file_content: Dict = None, name: str = None, set_values: Dict = None):
        api = lm_client.descriptors
        if file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            descriptor = file_content
        else:
            if name is None:
                raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
            descriptor = api.get(name)
            descriptor.update(set_values)
        api.update(descriptor)
        return descriptor.get('name')

    @LmDelete()
    @click.argument('name', required=False)
    def delete(self, lm_client: LmClient, ctx: click.Context, file_content: Dict = None, name: str = None, ignore_missing: bool = None):
        api = lm_client.descriptors
        if file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            descriptor = file_content
            descriptor_name = descriptor.get('name', None)
            if descriptor_name is None:
                raise click.BadArgumentUsage(message='Object from file does not contain a "name" attribute', ctx=ctx)
        else:
            if name is None:
                raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
            descriptor_name = name
        try:
            result = api.delete(descriptor_name)
        except LmClientHttpError as e:
            if e.status_code == 404:
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    ctl.io.print(f'No {self.display_name} found with name {descriptor_name} (ignoring)')
                    return
            raise
        return descriptor_name