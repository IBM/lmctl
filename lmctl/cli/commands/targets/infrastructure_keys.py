import click
from typing import Dict
from lmctl.client import TNCOClient, TNCOClientHttpError
from lmctl.cli.arguments import common_output_format_handler
from lmctl.cli.format import Table, Column
from .tnco_target import TNCOTarget, LmGet, LmCreate, LmUpdate, LmDelete, LmGen

class InfrastructureKeyTable(Table):
    
    columns = [
        Column('name', header='Name'),
        Column('id', header='ID'),
        Column('description', header='Description')
    ]

output_formats = common_output_format_handler(table=InfrastructureKeyTable())
    
class InfrastructureKeys(TNCOTarget):
    name = 'infrastructurekey'
    plural = 'infrastructurekeys'
    display_name = 'Infrastructure Key'

    @LmGen()
    def genfile(self, ctx: click.Context, name: str):
        return {
            'name': name,
            'description': 'An infrastructure key', 
            'privateKey': 'the-private-part',
            'publicKey': 'the-public-part'
        }

    @LmGet(output_formats=output_formats, help=f'''\
                                            Get all {display_name}s or get by name\
                                            \n\nUse NAME argument to get by name\
                                            \n\nOmit NAME argument to get all''')
    @click.argument('name', required=False)
    @click.option('--include-private', is_flag=True, help='Include private key value for each key in the response')
    def get(self, tnco_client: TNCOClient, ctx: click.Context, name: str = None, include_private: bool = False):
        api = tnco_client.shared_inf_keys
        if name is not None:
            return api.get(name, include_private_key=include_private)
        else:
            return api.all(include_private_key=include_private) 

    @LmCreate()
    def create(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None):
        api = tnco_client.shared_inf_keys
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-f, --file" option', ctx=ctx)
            inf_key = file_content
        else:
            inf_key = set_values
        result = api.create(inf_key)
        return result.get('name')

    @LmUpdate()
    @click.argument('name', required=False)
    def update(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, name: str = None, set_values: Dict = None):
        api = tnco_client.shared_inf_keys
        if file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            inf_key = file_content
        else:
            if name is None:
                raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
            inf_key = api.get(name)
            inf_key.update(set_values)
        result = api.update(inf_key)
        return inf_key.get('name')

    @LmDelete()
    @click.argument('name', required=False)
    def delete(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, name: str = None, ignore_missing: bool = None):
        api = tnco_client.shared_inf_keys
        if file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            inf_key = file_content
            inf_key_name = inf_key.get('name', None)
            if inf_key_name is None:
                raise click.BadArgumentUsage(message='Object from file does not contain a "name" attribute', ctx=ctx)
        else:
            if name is None:
                raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
            inf_key_name = name
        try:
            result = api.delete(inf_key_name)
        except TNCOClientHttpError as e:
            if e.status_code == 404:
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    ctl.io.print(f'No {self.display_name} found with name {inf_key_name} (ignoring)')
                    return
            raise
        return inf_key_name