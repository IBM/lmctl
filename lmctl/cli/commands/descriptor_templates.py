import click
from .actions import render
from .utils import TNCOCommandBuilder, Identity, Identifier, pass_io, shallow_merge_objs
from lmctl.client import TNCOClient
from lmctl.cli.io import IOController
from lmctl.cli.format import Column, OutputFormat
from lmctl.cli.arguments import set_param_option, file_input_option, output_format_option
from typing import Dict, Any, Type

__all__ = (
    'generate_descriptor_template',
    'create_descriptor_template',
    'update_descriptor_template',
    'delete_descriptor_template',
    'get_descriptor_template'
)

tnco_builder = TNCOCommandBuilder(
    singular='descriptortemplate',
    plural='descriptortemplates',
    display_name='Descriptor Template'
)

name = Identifier.arg_and_attr('name')

default_columns = [
    Column('name', header='Name'),
    Column('description', header='Description', accessor=lambda x: (x.get('description')[:75].strip() + '..') if x.get('description', None) is not None and len(x.get('description')) > 75 else x.get('description'))    
]

@tnco_builder.make_generate_command()
def generate_descriptor_template():
    return {
            'name': 'assembly-template::example::1.0',
            'properties': {
                'injected_prop': {'type': 'string'}
            },
            'template': 'name: assembly::{{ injected_prop }}::1.0',
        }


@tnco_builder.make_create_command()
def create_descriptor_template(tnco_client: TNCOClient, obj: Dict[str, Any]):
    tnco_client.descriptor_templates.create(obj)
    descriptor_template_name = obj['name']
    return descriptor_template_name

@tnco_builder.make_update_command(identifiers=[name])
@click.argument(name.param_name, required=False)
def update_descriptor_template(tnco_client: TNCOClient, identity: Identity, obj: Dict[str, Any], patchable: bool):
    if patchable:
        patch_values = obj
        obj = tnco_client.descriptor_templates.get(identity.value)
        obj.update(patch_values)
    else:
        obj['name'] = identity.value
    tnco_client.descriptor_templates.update(obj)
    descriptor_template_name = obj['name']
    return descriptor_template_name

@tnco_builder.make_get_command(
    identifiers=[name],
    identifier_required=False,
    default_columns=default_columns
)
@click.argument(name.param_name, required=False)
def get_descriptor_template(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.descriptor_templates
    if identity is not None:
        descriptor_template_name = identity.value
        return api.get(descriptor_template_name)
    else:
        return api.all()

@tnco_builder.make_delete_command(identifiers=[name])
@click.argument(name.param_name, required=False)
def delete_descriptor_template(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.descriptor_templates
    descriptor_template_name = identity.value
    api.delete(name=descriptor_template_name)
    return descriptor_template_name

@tnco_builder.make_general_command(
    group=render,
    short_help=f'Render a {tnco_builder.display_name} and view the output',
    help_prefix=f'Render a {tnco_builder.display_name} and view the output',
    help_suffix='Note: the file passed to "-f, --file" only identifies the template, that should exist on the server, to be rendered. It does not represent the literal template to be rendered',
    identifiers=[name]
)
@click.argument(name.param_name, required=False)
@set_param_option(help='Set parameters on the render request')
@file_input_option('--request', '--request-file', 'request_file', help='Path to file with render request parameters')
@set_param_option('--prop', 'prop_values', help='Directly set a "properties" entry on the render request')
@output_format_option()
@click.option('--raw', is_flag=True, help='''\
                            Include this option to request the server does not attempt to parse the output to a Descriptor, 
                            instead passing the output back unchecked. This is useful for debugging normal render requests 
                            of a template which produce output that cannot be parsed as YAML
                            NOTE: when this option is enabled, the value of "-o" is ignored as the output must be in plain text''')
@pass_io
def render_template(
        tnco_client: TNCOClient,
        identity: Identity,
        io: IOController,
        set_values: Dict[str, Any],
        request_file: Dict[str, Any],
        prop_values: Dict[str, Any],
        output_format: OutputFormat,
        raw: bool
    ):
    render_request = shallow_merge_objs(request_file, set_values)
    if prop_values is not None:
        if 'properties' not in render_request:
            render_request['properties'] = prop_values
        else:
            render_request['properties'] = shallow_merge_objs(render_request['properties'], prop_values)
    
    api = tnco_client.descriptor_templates
    if raw: 
        result = api.render_raw(template_name=identity.value, render_request=render_request)
        io.print(result)
    else:
        result = api.render(template_name=identity.value, render_request=render_request)   
        io.print(output_format.convert_element(result))
