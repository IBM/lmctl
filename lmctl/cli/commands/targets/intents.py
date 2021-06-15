import click
from typing import Dict
from lmctl.client import TNCOClient, TNCOClientHttpError, TNCOClientError
from lmctl.cli.arguments import common_output_format_handler, default_file_inputs_handler
from lmctl.cli.format import Table, Column
from .tnco_target import TNCOTarget, LmGet, LmCreate, LmUpdate, LmDelete, LmCmd, LmGen

class Intents(TNCOTarget):
    name = 'intent'
    plural = 'intents'
    display_name = 'Intent'

    @LmGen()
    @click.option('--type', 'intent_type', required=False, default='createAssembly', show_default=True, help='The type of intent to generate. Known options: createAssembly, upgradeAssembly, adoptAssembly, changeAssemblyState, healAssembly, scaleOutAssembly, scaleInAssembly')
    def genfile(self, ctx: click.Context, name: str, intent_type: str):
        intent = {
            'type': intent_type,
            'assemblyName': name,
        }
        if intent_type in ['createAssembly', 'upgradeAssembly', 'adoptAssembly']:
            intent['descriptorName'] = 'assembly::example::1.0'
            intent['properties'] = {'examplePropA': 'exampleValue'}
        if intent_type in ['createAssembly', 'upgradeAssembly', 'adoptAssembly', 'changeAssemblyState']:
            intent['intendedState'] = 'Active'
        if intent_type == 'adoptAssembly':
            intent['clusters'] = {}
            intent['resources'] = {}
        if intent_type == 'healAssembly':
            intent['brokenComponentName'] = 'resource-to-heal'
        if intent_type in ['scaleOutAssembly', 'scaleInAssembly']:
            intent['clusterName'] = 'cluster-to-scale'
        return intent
            

    @LmCreate(short_help=f'Request an intent of any type on an Assembly', 
                    help=f'''\
                        Request an intent of any type on an Assembly. \
                        \n\nYou must include the type of intent either as an "intentType" attribute in the content of "-f, file" or with the "--set intentType=<type>" option
                        \n\nThe properties of a request depend on the type of intent being performed.\
                        \n\nKnown types: createAssembly, changeAssemblyState, upgradeAssembly, deleteAssembly, healAssembly, scaleOutAssembly, scaleInAssembly, adoptAssembly
                        \n\nNote: your chosen type is not validated against this list so if a new type of intent has been added in TNCO, this command is still usable
                    ''',
                    print_result=False)
    def create(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None):
        api = tnco_client.assemblies
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-f, --file" option', ctx=ctx)
            intent_request = file_content
            intent_name = intent_request.pop('intentType', None)
            if intent_name is None:
                raise click.BadArgumentUsage(message='Content of file passed to "-f, --file" option must include "intentType" attribute', ctx=ctx)
        else:
            intent_request = set_values
            intent_name = intent_request.pop('intentType', None)
            if intent_name is None:
                raise click.BadArgumentUsage(message='Must set "intentType" attribute e.g. "--set intentType=createAssembly"', ctx=ctx)
        result = api.intent(intent_name, intent_request)
        ctl = self._get_controller()
        ctl.io.print(f'Accepted - Process: {result}')