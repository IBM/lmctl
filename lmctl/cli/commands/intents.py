import click
from .assemblies import accepted_process_prefix
from .actions import create
from .utils import TNCOCommandBuilder, pass_io, shallow_merge_objs
from lmctl.client import TNCOClient
from lmctl.cli.arguments import set_param_option
from lmctl.cli.io import IOController
from typing import Dict, Any

__all__ = (
    'generate_intent',
    'create_intent',
)

tnco_builder = TNCOCommandBuilder(
    singular='intent',
    plural='intents',
    display_name='Intent'
)

@tnco_builder.make_generate_command()
@click.option('--type', 'intent_type', required=False, default='createAssembly', show_default=True, help='The type of intent to generate. Known options: createAssembly, upgradeAssembly, adoptAssembly, changeAssemblyState, healAssembly, scaleOutAssembly, scaleInAssembly')
def generate_intent(intent_type: str):
    intent = {
        'type': intent_type,
        'assemblyName': 'example',
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

@tnco_builder.make_general_command(
    group=create,
    short_help=f'Request an intent of any type on an Assembly',
    help=f'''\
        Request an intent of any type on an Assembly. \
        \n\nYou must include the type of intent either as an "intentType" attribute in the content of "-f, file" or with the "--set intentType=<type>" option
        \n\nThe properties of a request depend on the type of intent being performed.\
        \n\nKnown types: createAssembly, changeAssemblyState, upgradeAssembly, deleteAssembly, healAssembly, scaleOutAssembly, scaleInAssembly, adoptAssembly
        \n\nNote: your chosen type is not validated against this list so if a new type of intent has been added in CP4NA, this command is still usable
    ''',
    pass_file_content=True
)
@set_param_option()
@pass_io
def create_intent(tnco_client: TNCOClient, io: IOController, obj: Dict[str, Any], set_values: Dict[str, Any]):
    intent_request = shallow_merge_objs(obj, set_values)
    intent_name = intent_request.pop('intentType', None)
    if intent_name is None:
        raise click.UsageError(message='Must include "intentType" in contents of "-f, --file" or with "--set intentType=<type>"', ctx=click.get_current_context())
    process_id = tnco_client.assemblies.intent(intent_name, intent_request)
    io.print(f'{accepted_process_prefix}{process_id}')
