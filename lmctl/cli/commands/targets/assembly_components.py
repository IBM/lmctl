import click
from lmctl.client import TNCOClient
from .tnco_target import TNCOTarget, LmCmd

class AssemblyComponentMixin:

    def request_heal(self, tnco_client: TNCOClient, ctx: click.Context, name: str = None, id: str = None, metric_key: str = None, assembly_name: str = None, assembly_id: str = None):
        api = tnco_client.assemblies
        request = {}
        if assembly_id is not None:
            if assembly_name is not None:
                raise click.BadArgumentUsage(message='Do not use "--assembly-name" option when using "--assembly-id" option', ctx=ctx)
            request['assemblyId'] = assembly_id
        elif assembly_name is not None:
            request['assemblyName'] = assembly_name
        else:
            raise click.BadArgumentUsage(message=f'Must set "--assembly-id" option or "--assembly-name" option to identify the Assembly this {self.display_name} belongs to', ctx=ctx)
        if name is not None:
            if id is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "--id" option', ctx=ctx)
            if metric_key is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "--metric-key" option', ctx=ctx)
            request['brokenComponentName'] = name
        elif id is not None:
            if metric_key is not None:
                raise click.BadArgumentUsage(message='Do not use "--id" option when using "--metric-key" option', ctx=ctx)
            request['brokenComponentId'] = id
        elif metric_key is not None:
            request['brokenComponentMetricKey'] = metric_key
        else:
            raise click.BadArgumentUsage(message=f'Must set "NAME" argument or "--id" option or "--metric-key" to identify the {self.display_name} to be healed', ctx=ctx)   
        result = api.intent_heal(request)
        ctl = self._get_controller()
        ctl.io.print(f'Accepted - Process: {result}')

class AssemblyComponents(AssemblyComponentMixin, TNCOTarget):
    name = 'assemblycomponent'
    plural = 'assemblycomponents'
    display_name = 'Assembly Component'

    @LmCmd(short_help=f'Request an intent to heal an {display_name} (e.g. Resource)', 
                    help=f'''\
                        Request an intent to heal an {display_name}
                        \n\nThe target {display_name} may be identified by the "NAME" argument or the "--id" option or "--metric-key" option.
                        \n\nThe target Assembly may be identified by the "--name" option or the "--id" option
                        \n\nFor example:
                        \n\nHeal using {display_name} name: lmctl heal {name} my-component --assembly-name my-assembly-name 
                        \n\nHeal using {display_name} ID: lmctl heal {name} --id 6ad3327e-79df-464f-af48-3283f871584d --assembly-name my-assembly-name 
                        \n\nHeal using {display_name} metric key: lmctl heal {name} --metric-key 5fd27c1e-403c-402b-a033-fef0940974d5 --assembly-name my-assembly-name 
                        \n\nHeal using {display_name} name and Assembly ID: lmctl heal {name} my-component --assembly-id 7f528478-8180-442d-9a3f-c4e5869c9617
                    ''')
    @click.argument('name', required=False)
    @click.option('--id', help='Reference the target component by ID')
    @click.option('--metric-key', help='Reference the target component by metric key')
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
