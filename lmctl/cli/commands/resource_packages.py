import click
from .actions import create, update
from .utils import TNCOCommandBuilder, Identity, Identifier, pass_io
from lmctl.cli.io import IOController
from lmctl.client import TNCOClient

__all__ = (
    'create_resource_package',
    'update_resource_package',
    'delete_resource_package',
)

tnco_builder = TNCOCommandBuilder(
    singular='resourcepkg',
    plural='resourcepkgs',
    display_name='Resource Package'
)

name_arg = Identifier.arg_and_attr('name')

@tnco_builder.make_general_command(
    group=create,
    allow_file_input=False,
    short_help=f'Upload a {tnco_builder.display_name}',
    help=f'''Upload {tnco_builder.display_name}\
            \n\nNOTE: Resource Packages are not synonymous with LMCTL project packages, even when the project contains a Resource.
            The package for an LMCTL package can be extracted to find the Resource Package with zip/tar, depending on the chosen package format for your project'''
)
@click.option('-f','--file', 'file_path',  required=True, type=click.Path(exists=True), help='Path to Resource Package zip/tar')
@pass_io
def create_resource_package(tnco_client: TNCOClient, file_path: str, io: IOController):
    resource_name = tnco_client.resource_packages.create(file_path)
    io.print(f'Created from package: {resource_name}')

@tnco_builder.make_general_command(
    group=update,
    allow_file_input=False,
    short_help=f'Upload an updated {tnco_builder.display_name}',
    help=f'''Upload an updated {tnco_builder.display_name}\
            \n\nNOTE: Resource Packages are not synonymous with LMCTL project packages, even when the project contains a Resource.
            The package for an LMCTL package can be extracted to find the Resource Package with zip/tar, depending on the chosen package format for your project'''
)
@click.argument(name_arg.param_name, required=True)
@click.option('-f','--file', 'file_path',  required=True, type=click.Path(exists=True), help='Path to Resource Package zip/tar')
@pass_io
def update_resource_package(tnco_client: TNCOClient, name: str, file_path: str, io: IOController):
    tnco_client.resource_packages.update(name, file_path)
    io.print(f'Updated package for: {name}')

@tnco_builder.make_delete_command(identifiers=[name_arg], result_prefix='Removed package for: ')
@click.argument(name_arg.param_name, required=False)
def delete_resource_package(tnco_client: TNCOClient, identity: Identity): 
    resource_name = identity.value
    tnco_client.resource_packages.delete(resource_name)
    return resource_name

