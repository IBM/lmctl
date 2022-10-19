import click
from .actions import scale
from .utils import TNCOCommandBuilder, Identity, Identifier, pass_io
from .assemblies import accepted_process_prefix
from typing import Dict, Any
from lmctl.client import TNCOClient
from lmctl.cli.io import IOController

__all__ = (
    'scale_resource_cluster',
)

tnco_builder = TNCOCommandBuilder(
    singular='resourcecluster',
    plural='resourceclusters',
    display_name='Resource Cluster'
)

name_arg = Identifier(
    param_name='name',
    obj_attribute='clusterName'
)
assembly_name_opt = Identifier(
    param_name='assembly_name',
    obj_attribute='assemblyName',
    param_opts=['--assembly-name']
)
assembly_id_opt = Identifier(
    param_name='assembly_id',
    obj_attribute='assemblyId',
    param_opts=['--assembly-id']
)

help_suffix = f'''\
Request an intent to scale out/in a {tnco_builder.display_name} of an Assembly.
\n\nUse "--out" option to indicate a scale out request or "--in" to indicate a scale in
\n\nThe target Assembly may be identified by the "--assembly-name" option or the "--assembly-id" option
\n\nFor example:
\n\nScale out using Assembly name: lmctl scale resourcecluster my-cluster-name --assembly-name my-assembly-name --out 
\n\nScale out using Assembly ID: lmctl scale resourcecluster my-cluster-name --id bd83f0df-1e82-48ac-8faa-1d772e0c49cd --out 
'''

@tnco_builder.make_general_command(
    group=scale,
    short_help=f'Request an intent to scale out/in a {tnco_builder.display_name} of an Assembly',
    help_prefix=f'Request an intent to scale out/in a {tnco_builder.display_name} of an Assembly',
    help_suffix=help_suffix,
    identifiers=[name_arg],
    additional_identifiers={
        'assembly_identity': (True, [assembly_name_opt, assembly_id_opt])
    },
    pass_file_content=True
)
@click.argument(name_arg.param_name, required=False)
@click.option(*assembly_name_opt.param_opts, help=f'Reference the owning Assembly by name')
@click.option(*assembly_id_opt.param_opts, help=f'Reference the owning Assembly by ID')
@click.option('--in/--out', 'scale_in', default=False, help=f'Scale the {tnco_builder.display_name} in or out')
@pass_io
def scale_resource_cluster(
        tnco_client: TNCOClient,
        obj: Dict[str, Any],
        io: IOController, 
        identity: Identity,
        assembly_identity: Identity,
        scale_in: bool,
    ):
    obj['clusterName'] = identity.value
    if assembly_identity.identifier.param_name == assembly_name_opt.param_name:
        obj[assembly_name_opt.obj_attribute] = assembly_identity.value
        obj.pop(assembly_id_opt.obj_attribute, None)
    else:
        obj[assembly_id_opt.obj_attribute] = assembly_identity.value
        obj.pop(assembly_name_opt.obj_attribute, None)

    if scale_in:
        process_id = tnco_client.assemblies.intent_scale_in(obj)
    else:
        process_id = tnco_client.assemblies.intent_scale_out(obj)
    io.print(f'{accepted_process_prefix}{process_id}')
