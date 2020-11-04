import click
from lmctl.client import TNCOClient
from .tnco_target import TNCOTarget, LmCmd

class Cluster(TNCOTarget):
    name = 'cluster'
    plural = 'clusters'
    display_name = 'Cluster'

    @LmCmd(short_help=f'Request an intent to scale out/in a {display_name} of an Assembly', 
                    help=f'''\
                        Request an intent to scale out/in a {display_name} of an Assembly.
                        \n\nUse "--out" option to indicate a scale out request or "--in" to indicate a scale in
                        \n\nThe target Assembly may be identified by the "--assembly-name" option or the "--assembly-id" option
                        \n\nFor example:
                        \n\nScale out using Assembly name: lmctl scale cluster my-cluster-name --assembly-name my-assembly-name --out 
                        \n\nScale out using Assembly ID: lmctl scale cluster my-cluster-name --id bd83f0df-1e82-48ac-8faa-1d772e0c49cd --out 
                    ''')
    @click.argument('name')
    @click.option('--assembly-id', help='Reference the target Assembly by ID')
    @click.option('--assembly-name', help='Reference the target Assembly by ID')
    @click.option('--in', 'scale_in', is_flag=True, help=f'Scale the {display_name} in')
    @click.option('--out', 'scale_out', is_flag=True, help=f'Scale the {display_name} out')
    def scale(self, tnco_client: TNCOClient, ctx: click.Context, name: str = None, assembly_name: str = None, assembly_id: str = None, scale_in: bool = False, scale_out: bool = False):
        api = tnco_client.assemblies
        scale_req = {
            'clusterName': name
        }
        if assembly_id is not None:
            if assembly_name is not None:
                raise click.BadArgumentUsage(message='Do not use "--assembly-name" option when using "--assembly-id" option', ctx=ctx)
            scale_req['assemblyId'] = assembly_id
        elif assembly_name is not None:
            scale_req['assemblyName'] = assembly_name
        else:
            raise click.BadArgumentUsage(message=f'Must set "--assembly-id" option or "--assembly-name" option to identify the Assembly this {self.display_name} belongs to', ctx=ctx)
        if scale_in:
            if scale_out:
                raise click.BadArgumentUsage(message='Must identify the scale option by including only one of "--in" or "--out" options, not both', ctx=ctx)
            result = api.intent_scale_in(scale_req)
        elif scale_out:
            result = api.intent_scale_out(scale_req)
        else:
            raise click.BadArgumentUsage(message=f'Must set "--in" option or "--out" option to identify the type of scale operation', ctx=ctx)   
        ctl = self._get_controller()
        ctl.io.print(f'Accepted - Process: {result}')

