import click
from typing import Dict
from lmctl.client import LmClient, LmClientHttpError
from lmctl.cli.arguments import common_output_format_handler
from lmctl.cli.format import Table, Column
from .lm_target import LmTarget, LmGet, LmCreate, LmUpdate, LmDelete

class AssemblyConfigurationTable(Table):
    
    columns = [
        Column('id', header='ID'),
        Column('name', header='Name'),
        Column('description', header='Description'),
        Column('descriptorName', header='Descriptor Name')
    ]

output_formats = common_output_format_handler(table=AssemblyConfigurationTable())
    
class AssemblyConfigurations(LmTarget):
    name = 'assemblyconfig'
    plural = 'assemblyconfigs'
    display_name = 'Assembly Configuration'

    @LmGet(output_formats=output_formats, help=f'''\
                                            Get {display_name} by ID or all in a Behaviour Project\
                                            \n\nUse ID argument to get by ID\
                                            \n\nOmit ID argument and set "--project" option to get all in a Behaviour Project''')
    @click.argument('ID', required=False)
    @click.option('--project', help=f'ID of a project to retrieve {display_name}s from')
    def get(self, lm_client: LmClient, ctx: click.Context, id: str = None, project: str = None):
        api = lm_client.behaviour_assembly_confs
        if id is not None:
            if project is not None:
                raise click.BadArgumentUsage('Do not use "ID" argument when using the "--project" option', ctx=ctx)
            return api.get(id)
        elif project is not None:
            return api.all_in_project(project)
        else:
            raise click.BadArgumentUsage('Must set either "ID" argument or "--project" option', ctx=ctx) 
        
    @LmCreate()
    def create(self, lm_client: LmClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None):
        api = lm_client.behaviour_assembly_confs
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "set" option when using "-f, --file" option', ctx=ctx)
            assembly_conf = file_content
        else:
            assembly_conf = set_values
        result = api.create(assembly_conf)
        return result.get('id')

    @LmUpdate()
    @click.argument('ID', required=False)
    def update(self, lm_client: LmClient, ctx: click.Context, file_content: Dict = None, id: str = None, set_values: Dict = None):
        api = lm_client.behaviour_assembly_confs
        if file_content is not None:
            if id is not None:
                raise click.BadArgumentUsage(message='Do not use "ID" argument when using "-f, --file" option', ctx=ctx)
            assembly_conf = file_content
        else:
            if id is None:
                raise click.BadArgumentUsage(message='Must set "ID" argument when no "-f, --file" option specified', ctx=ctx)
            assembly_conf = api.get(id)
            assembly_conf.update(set_values)
        result = api.update(assembly_conf)
        return assembly_conf.get('id')

    @LmDelete()
    @click.argument('ID', required=False)
    def delete(self, lm_client: LmClient, ctx: click.Context, file_content: Dict = None, id: str = None, ignore_missing: bool = None):
        api = lm_client.behaviour_assembly_confs
        if file_content is not None:
            if id is not None:
                raise click.BadArgumentUsage(message='Do not use "ID" argument when using "-f, --file" option', ctx=ctx)
            assembly_conf = file_content
            assembly_conf_id = assembly_conf.get('id', None)
            if assembly_conf_id is None:
                raise click.BadArgumentUsage(message='Object from file does not contain an "id" attribute', ctx=ctx)
        else:
            if id is None:
                raise click.BadArgumentUsage(message='Must set "ID" argument when no "-f, --file" option specified', ctx=ctx)
            assembly_conf_id = id
        try:
            result = api.delete(assembly_conf_id)
        except LmClientHttpError as e:
            if e.status_code == 404:
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    ctl.io.print(f'No {self.display_name} found with ID {assembly_conf_id} (ignoring)')
                    return
            raise
        return assembly_conf_id