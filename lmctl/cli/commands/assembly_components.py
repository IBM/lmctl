import click
from lmctl.client import TNCOClient
from lmctl.cli.io import IOController
from typing import Dict, Any
from .actions import heal
from .utils import TNCOCommandBuilder, Identity, Identifier, pass_io
from .assemblies import accepted_process_prefix

__all__ = (
    'heal_assembly_component',
    'heal_resource'
)

component_tnco_builder = TNCOCommandBuilder(
    singular='assemblycomponent',
    plural='assemblycomponents',
    display_name='Assembly Component'
)

resource_tnco_builder = TNCOCommandBuilder(
    singular='resource',
    plural='resources',
    display_name='Resource'
)

name_arg = Identifier(
    param_name='name',
    obj_attribute='brokenComponentName'
)
id_opt = Identifier(
    param_name='id',
    obj_attribute='brokenComponentId',
    param_opts=['--id']
)
metric_key_opt = Identifier(
    param_name='metric_key',
    obj_attribute='brokenComponentMetricKey',
    param_opts=['--metric-key']
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

def build_heal(tnco_builder, a_or_an = 'a', help_prefix_extra = ''):
    help_suffix = f'''\
    For example:
    \n\nHeal using {tnco_builder.display_name} name: lmctl heal {tnco_builder.singular} my-component --assembly-name my-assembly-name 
    \n\nHeal using {tnco_builder.display_name} ID: lmctl heal {tnco_builder.singular} --id 6ad3327e-79df-464f-af48-3283f871584d --assembly-name my-assembly-name 
    \n\nHeal using {tnco_builder.display_name} metric key: lmctl heal {tnco_builder.singular} --metric-key 5fd27c1e-403c-402b-a033-fef0940974d5 --assembly-name my-assembly-name 
    \n\nHeal using {tnco_builder.display_name} name and Assembly ID: lmctl heal {tnco_builder.singular} my-component --assembly-id 7f528478-8180-442d-9a3f-c4e5869c9617
    '''

    @tnco_builder.make_general_command(
        group=heal,
        short_help=f'Request an intent to heal {a_or_an} {tnco_builder.display_name} {help_prefix_extra}',
        help_prefix=f'Request an intent to heal {a_or_an} {tnco_builder.display_name} {help_prefix_extra}',
        help_suffix=help_suffix,
        identifiers=[name_arg, id_opt, metric_key_opt],
        additional_identifiers={
            'assembly_identity': (True, [assembly_name_opt, assembly_id_opt])
        },
        pass_file_content=True
    )
    @click.argument(name_arg.param_name, required=False)
    @click.option(*id_opt.param_opts, help=f'Reference the target {tnco_builder.display_name} by ID instead of name/metric key')
    @click.option(*metric_key_opt.param_opts, help=f'Reference the target {tnco_builder.display_name} by metric key instead of ID/name')
    @click.option(*assembly_name_opt.param_opts, help=f'Reference the owning Assembly by name')
    @click.option(*assembly_id_opt.param_opts, help=f'Reference the owning Assembly by ID')
    @pass_io
    def do_heal(
            tnco_client: TNCOClient,
            obj: Dict[str, Any],
            io: IOController, 
            identity: Identity,
            assembly_identity: Identity
        ):
        if identity.identifier.param_name == name_arg.param_name:
            obj[name_arg.obj_attribute] = identity.value
            obj.pop(id_opt.obj_attribute, None)
            obj.pop(metric_key_opt.obj_attribute, None)
        elif identity.identifier.param_name == metric_key_opt.param_name:
            obj[metric_key_opt.obj_attribute] = identity.value
            obj.pop(id_opt.obj_attribute, None)
            obj.pop(name_arg.obj_attribute, None)
        else:
            obj[id_opt.obj_attribute] = identity.value
            obj.pop(metric_key_opt.obj_attribute, None)
            obj.pop(name_arg.obj_attribute, None)

        if assembly_identity.identifier.param_name == assembly_name_opt.param_name:
            obj[assembly_name_opt.obj_attribute] = assembly_identity.value
            obj.pop(assembly_id_opt.obj_attribute, None)
        else:
            obj[assembly_id_opt.obj_attribute] = assembly_identity.value
            obj.pop(assembly_name_opt.obj_attribute, None)

        process_id = tnco_client.assemblies.intent_heal(obj)
        io.print(f'{accepted_process_prefix}{process_id}')

    return do_heal


heal_assembly_component = build_heal(component_tnco_builder, a_or_an='an', help_prefix_extra='(e.g. Resource)')

heal_resource = build_heal(resource_tnco_builder)
