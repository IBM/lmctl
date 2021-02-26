import click
from typing import Dict
from lmctl.client import TNCOClient, TNCOClientHttpError
from lmctl.cli.arguments import common_output_format_handler
from lmctl.cli.format import Table, Column
from .tnco_target import TNCOTarget, LmGet, LmCreate, LmUpdate, LmDelete, LmGen

class ProjectTable(Table):
    
    columns = [
        Column('name', header='Name'),
        Column('description', header='Description')
    ]

output_formats = common_output_format_handler(table=ProjectTable())

class Projects(TNCOTarget):
    name = 'behaviourproject'
    plural = 'behaviourprojects'
    display_name = 'Behaviour Project'

    @LmGen()
    def genfile(self, ctx: click.Context, name: str):
        return {
            'name': f'assembly::{name}::1.0',
        }

    @LmGet(output_formats=output_formats, help=f'''\
                                            Get all {display_name}s or get one by name\
                                            \n\nUse NAME argument to get by one by name\
                                            \n\nOmit NAME argument get all projects\
                                            \n\nNote: all Assembly descriptors have a Behaviour Project associated with them so can be found using their name e.g. assembly::example::1.0''')
    @click.argument('name', required=False)
    def get(self, tnco_client: TNCOClient, ctx: click.Context, name: str = None):
        api = tnco_client.behaviour_projects
        if name is not None:
            return api.get(name)
        else:
            return api.all()

    @LmCreate()
    def create(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None):
        api = tnco_client.behaviour_projects
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-f, --file" option', ctx=ctx)
            project = file_content
        else:
            project = set_values
        result = api.create(project)
        return result.get('name')

    @LmUpdate()
    @click.argument('name', required=False)
    def update(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, name: str = None, set_values: Dict = None):
        api = tnco_client.behaviour_projects
        if file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            project = file_content
        else:
            if name is None:
                raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
            project = api.get(name)
            project.update(set_values)
        result = api.update(project)
        return project.get('name')

    @LmDelete()
    @click.argument('name', required=False)
    def delete(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, name: str = None, ignore_missing: bool = None):
        api = tnco_client.behaviour_projects
        if file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            project = file_content
            project_id = project.get('id', project.get('name', None))
            if project_id is None:
                raise click.BadArgumentUsage(message='Object from file does not contain an "name" (or "id") attribute', ctx=ctx)
        else:
            if name is None:
                raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
            project_id = name
        try:
            result = api.delete(project_id)
        except TNCOClientHttpError as e:
            if e.status_code == 404:
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    ctl.io.print(f'No {self.display_name} found with name (ID) {project_id} (ignoring)')
                    return
            raise
        return project_id