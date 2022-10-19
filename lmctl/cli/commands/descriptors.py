import click
from .utils import TNCOCommandBuilder, Identity, Identifier
from lmctl.client import TNCOClient
from lmctl.cli.format import Column
from typing import Dict, Any, Type

__all__ = (
    'generate_descriptor',
    'create_descriptor',
    'update_descriptor',
    'delete_descriptor',
    'get_descriptor'
)

tnco_builder = TNCOCommandBuilder(
    singular='descriptor',
    plural='descriptors',
    display_name='Descriptor'
)

name = Identifier.arg_and_attr('name')

default_columns = [
    Column('name', header='Name'),
    Column('description', header='Description', accessor=lambda x: (x.get('description')[:75].strip() + '..') if x.get('description', None) is not None and len(x.get('description')) > 75 else x.get('description'))    
]

@tnco_builder.make_generate_command()
def generate_descriptor():
    return {
            'name': 'assembly::example::1.0',
            'properties': {
                'propA': {'type': 'string'}
            },
            'composition': {
                'A': {
                    'type': 'resource::example::1.0',
                    'properties': {
                        'propA': {
                            'value': '${propA}'
                        }
                    }
                }
            }
        }

@tnco_builder.make_create_command()
def create_descriptor(tnco_client: TNCOClient, obj: Dict[str, Any]):
    tnco_client.descriptors.create(obj)
    descriptor_name = obj['name']
    return descriptor_name

@tnco_builder.make_update_command(identifiers=[name])
@click.argument(name.param_name, required=False)
def update_descriptor(tnco_client: TNCOClient, identity: Identity, obj: Dict[str, Any], patchable: bool):
    if patchable:
        patch_values = obj
        obj = tnco_client.descriptors.get(identity.value)
        obj.update(patch_values)
    else:
        obj['name'] = identity.value
    tnco_client.descriptors.update(obj)
    descriptor_name = obj['name']
    return descriptor_name

@tnco_builder.make_get_command(
    identifiers=[name],
    identifier_required=False,
    default_columns=default_columns
)
@click.argument(name.param_name, required=False)
@click.option('--effective', is_flag=True, show_default=True, help=f'Get effective version of a {tnco_builder.display_name}, which includes all inherited properties (can only be used when retrieving a single {tnco_builder.display_name} by name)')
def get_descriptor(tnco_client: TNCOClient, identity: Identity, effective: bool):
    if identity is None and effective is True:
        raise click.UsageError(f'Cannot use "--effective" option when retrieving all {tnco_builder.display_name}s (which means the {name.param_name} argument was omitted)', ctx=click.get_current_context())
    api = tnco_client.descriptors
    if identity is not None:
        descriptor_name = identity.value
        return api.get(descriptor_name, effective=effective)
    else:
        return api.all()

@tnco_builder.make_delete_command(identifiers=[name])
@click.argument(name.param_name, required=False)
def delete_descriptor(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.descriptors
    descriptor_name = identity.value
    api.delete(name=descriptor_name)
    return descriptor_name
