import click
from typing import Dict
from lmctl.client import TNCOClient, TNCOClientHttpError
from lmctl.cli.arguments import common_output_format_handler, default_file_inputs_handler, default_output_format_handler, set_param_option
from lmctl.cli.format import Table, Column
from .tnco_target import TNCOTarget, LmGet, LmCreate, LmUpdate, LmDelete, LmCmd, LmGen

class DescriptorTemplatesTable(Table):
    
    columns = [
        Column('name', header='Name'),
        Column('description', header='Description', accessor=lambda x: (x.get('description')[:75].strip() + '..') if x.get('description', None) is not None and len(x.get('description')) > 75 else x.get('description'))
    ]

output_formats = common_output_format_handler(table=DescriptorTemplatesTable())
render_output_formats = default_output_format_handler()
file_inputs = default_file_inputs_handler()

class DescriptorTemplates(TNCOTarget):
    name = 'descriptortemplate'
    plural = 'descriptortemplates'
    display_name = 'Descriptor Template'

    @LmGen()
    def genfile(self, ctx: click.Context, name: str):
        return {
            'name': name,
            'properties': {
                'injected_prop': {'type': 'string'}
            },
            'template': 'name: assembly::{{ injected_prop }}::1.0',
        }

    @LmCmd(short_help=f'Render a {display_name} and view the output', 
                help=f'''\
                        Render a {display_name} and view the output
                        \n\nNote: the file passed to "-f, --file" only identifies the template, that should exist on the server, to be rendered. It does not represent the literal template to be rendered 
                      ''')
    @click.argument('name', required=False)
    @render_output_formats.option()
    @file_inputs.option(var_name='template_file_content', help='Path to file with the name of the template to be rendered')
    @file_inputs.option(var_name='request_file_content', options=['-r', '--request-file'], help='Path to file with properties to be used on the render request')
    @set_param_option()
    @set_param_option(options=['--prop'], var_name='prop_values', help='Directly set a property passed to the render request')
    @click.option('--raw', is_flag=True, help='''\
                            Include this option to request the server does not attempt to parse the output to a Descriptor, 
                            instead passing the output back unchecked. This is useful for debugging normal render requests 
                            of a template which produce output that cannot be parsed as YAML
                            NOTE: when this option is enabled, the value of "-o" is ignored as the output must be in plain text''')
    def render(self, tnco_client: TNCOClient, ctx: click.Context, output_format: str, name: str = None, raw: bool = False, set_values: Dict = None, prop_values: Dict = None, template_file_content: Dict = None, request_file_content: Dict = None):
        api = tnco_client.descriptor_templates
        if template_file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            name = template_file_content.get('name', None)
            if name is None:
                raise click.BadArgumentUsage(message='Object from file does not contain a "name" attribute', ctx=ctx)
        elif name is None:
            raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
        if request_file_content is not None and len(request_file_content) > 0:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-r, --request-file" option', ctx=ctx)
            if prop_values is not None and len(prop_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--prop" option when using "-r, --request-file" option', ctx=ctx)
            render_request = request_file_content
        else:
            render_request = set_values
            if render_request is None:
                render_request = {}
            if 'properties' not in render_request or type(render_request['properties']) != dict:
                render_request['properties'] = {}
            if prop_values is not None:
                render_request['properties'].update(prop_values)
        ctl = self._get_controller()
        if raw: 
            result = api.render_raw(template_name=name, render_request=render_request)
            ctl.io.print(result)
        else:
            result = api.render(template_name=name, render_request=render_request)   
            output_formatter = output_formats.resolve_choice(output_format)
            ctl.io.print(output_formatter.convert_element(result))

    @LmGet(output_formats=output_formats, help=f'''\
                                            Get a summary of all {display_name}s or get the details of one by name\
                                            \n\nUse NAME argument to get one by name\
                                            \n\nOmit NAME argument to get all''')
    @click.argument('name', required=False)
    def get(self, tnco_client: TNCOClient, ctx: click.Context, name: str = None):
        api = tnco_client.descriptor_templates
        if name is not None:
            return api.get(name)
        else:
            return api.all()
        
    @LmCreate()
    def create(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None):
        api = tnco_client.descriptor_templates
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-f, --file" option', ctx=ctx)
            descriptor = file_content
        else:
            descriptor = set_values
        api.create(descriptor)
        return descriptor.get('name')

    @LmUpdate()
    @click.argument('name', required=False)
    def update(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, name: str = None, set_values: Dict = None):
        api = tnco_client.descriptor_templates
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
    def delete(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, name: str = None, ignore_missing: bool = None):
        api = tnco_client.descriptor_templates
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
        except TNCOClientHttpError as e:
            if e.status_code == 404:
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    ctl.io.print(f'No {self.display_name} found with name {descriptor_name} (ignoring)')
                    return
            raise
        return descriptor_name