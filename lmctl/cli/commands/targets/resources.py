import click
from lmctl.client import TNCOClient
from .tnco_target import TNCOTarget, LmCmd
from .assembly_components import AssemblyComponentMixin, AssemblyComponents

class Resource(TNCOTarget, AssemblyComponentMixin):
    name = 'resource'
    plural = 'resources'
    display_name = 'Resource'

    @LmCmd(short_help=f'Request an intent to heal a {display_name} (same as {AssemblyComponents.name})', 
                    help=f'''\
                        Request an intent to heal a {display_name}
                        \n\nThe target {display_name} may be identified by the "NAME" argument or the "--id" option or "--metric-key" option.
                        \n\nThe target Assembly may be identified by the "--assembly-name" option or the "--assembly-id" option
                        \n\nFor example:
                        \n\nHeal using {display_name} name: lmctl heal {name} my-resource --assembly-name my-assembly-name 
                        \n\nHeal using {display_name} ID: lmctl heal {name} --id 6ad3327e-79df-464f-af48-3283f871584d --assembly-name my-assembly-name 
                        \n\nHeal using {display_name} metric key: lmctl heal {name} --metric-key 5fd27c1e-403c-402b-a033-fef0940974d5 --assembly-name my-assembly-name 
                        \n\nHeal using {display_name} name and Assembly ID: lmctl heal {name} my-resource --assembly-id 7f528478-8180-442d-9a3f-c4e5869c9617
                    ''')
    @click.argument('name', required=False)
    @click.option('--id', help='Reference the target resource by ID')
    @click.option('--metric-key', help='Reference the target resource by metric key')
    @click.option('--assembly-id', help='Reference the target Assembly by ID')
    @click.option('--assembly-name', help='Reference the target Assembly by ID')
    def heal(self, tnco_client: TNCOClient, ctx: click.Context, name: str = None, id: str = None, metric_key: str = None, assembly_name: str = None, assembly_id: str = None):
        return self.request_heal(
            tnco_client=tnco_client, 
            ctx=ctx, name=name, 
            id=id, 
            metric_key=metric_key, 
            assembly_name=assembly_name, 
            assembly_id=assembly_id
        )