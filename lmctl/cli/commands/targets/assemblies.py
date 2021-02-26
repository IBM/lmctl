import click
from typing import Dict
from lmctl.client import TNCOClient, TNCOClientHttpError, TNCOClientError
from lmctl.cli.arguments import common_output_format_handler, default_file_inputs_handler, set_param_option
from lmctl.cli.format import Table, Column
from .tnco_target import TNCOTarget, LmGet, LmCreate, LmUpdate, LmDelete, LmGen, LmCmd

class AssemblyTable(Table):
    
    columns = [
        Column('id', header='ID'),
        Column('name', header='Name'),
        Column('descriptorName', header='Descriptor Name'),
        Column('state', header='State')
    ]

output_formats = common_output_format_handler(table=AssemblyTable())
file_inputs = default_file_inputs_handler()

class Assemblies(TNCOTarget):
    name = 'assembly'
    plural = 'assemblies'
    display_name = 'Assembly'

    @LmGen()
    def genfile(self, ctx: click.Context, name: str):
        return {
            'name': name,
            'descriptorName': 'assembly::example::1.0',
            'intendedState': 'Active',
            'properties': {
                'examplePropA': 'exampleValue'
            }
        }

    @LmGet(output_formats=output_formats, help=f'''\
                                            Get an {display_name} by ID or name. Alternatively, get a list of most recent or by partial name match\
                                            \n\nUse NAME argument to get by name\
                                            \n\nOmit NAME argument and use --topN option to get recent\
                                            \n\nOmit NAME argument and use --name-contains option to get by partial name match''')
    @click.argument('name', required=False)
    @click.option('--id', help='Get by ID')
    @click.option('--name-contains', help='Partial name search string')
    @click.option('--topN', is_flag=True, help=f'Get {display_name} instances that have recently changed')
    def get(self, tnco_client: TNCOClient, ctx: click.Context, id: str = None, name: str = None, name_contains: str = None, topn: bool = False):
        api = tnco_client.assemblies
        if name is not None:
            if id is not None:
                raise click.BadArgumentUsage('Do not use "NAME" argument when using the "--id" option', ctx=ctx)
            if name_contains is not None:
                raise click.BadArgumentUsage('Do not use "NAME" argument when using the "--name-contains" option', ctx=ctx)
            if topn is True:
                raise click.BadArgumentUsage('Do not use "NAME" argument when using the "--topN" option', ctx=ctx)
            return api.get_by_name(name)
        elif id is not None:
            if name_contains is not None:
                raise click.BadArgumentUsage('Do not use "--id" option when using the "--name-contains" option', ctx=ctx)
            if topn is True:
                raise click.BadArgumentUsage('Do not use "--id" option when using the "--topN" option', ctx=ctx)
            return api.get(id)
        elif name_contains is not None:
            if topn is True:
                raise click.BadArgumentUsage('Do not use "--name-contains" option when using the "--topN" option', ctx=ctx)
            return api.all_with_name_containing(name_contains).get('assemblies', [])
        elif topn is True:
            return api.get_topN()
        else:
            raise click.BadArgumentUsage('Must set either "NAME" argument or "--id" option or "--name-contains" option or "--topN" option', ctx=ctx)

    @LmCreate(short_help=f'Request an intent to create an {display_name}', 
                    help=f'''\
                        Request an intent to create an {display_name}. The request can include the following parameters (either with --set or in a file with -f):
                        \n\nassemblyName - A unique name by which this {display_name} will be known externally. This cannot contain spaces, consecutive underscores or start with a numeric character.\
                        \n\ndescriptorName - The descriptor name from which this {display_name} will be created\
                        \n\nintendedState - The final intended state that the {display_name} should be brought into
                        \n\nproperties - An optional map of name and value pairs supplied to the new {display_name}
                    ''',
                    print_result=False)
    @set_param_option(options=['--prop'], var_name='prop_values', help='Directly set a property passed to the request')
    def create(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None, prop_values: Dict = None):
        api = tnco_client.assemblies
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-f, --file" option', ctx=ctx)
            if prop_values is not None and len(prop_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--prop" option when using "-f, --file" option', ctx=ctx)
            assembly_req = file_content
        else:
            assembly_req = set_values
            if assembly_req is None:
                assembly_req = {}
            if 'properties' not in assembly_req or type(assembly_req['properties']) != dict:
                assembly_req['properties'] = {}
            if prop_values is not None:
                assembly_req['properties'].update(prop_values)
        result = api.intent_create(assembly_req)
        ctl = self._get_controller()
        ctl.io.print(f'Accepted - Process: {result}')

    @LmUpdate(short_help=f'Request an intent to upgrade an {display_name}', 
                    help=f'''\
                        Request an intent to upgrade an {display_name} ({display_name} must be in the Active state to proceed). The request can include the following properties:
                        \n\n\tdescriptorName - The descriptor name from which this {display_name} will be updated to\
                        \n\n\tproperties - An optional map of name and string value properties that is supplied to the new {display_name}\
                        \n\nThe target {display_name} to be upgrade may be identified by the "NAME" argument or the "--id" option or by including "assemblyId"/"assemblyName" in the contents of the "-f, --file" option, if set 
                        \n\nFor example:
                        \n\nUpgrade {display_name} using file: lmctl update assembly -f my-request.yaml
                        \n\nUpgrade {display_name} by name: lmctl update assembly my-assembly-name --set descriptorName=assembly::my-service::2.0
                        \n\nUpgrade {display_name} by ID: lmctl update assembly --id bd83f0df-1e82-48ac-8faa-1d772e0c49cd --set descriptorName=assembly::my-service::2.0
                    ''',
                    print_result=False)
    @click.argument('name', required=False)
    @click.option('--id', help='Reference the target Assembly by ID instead of name')
    @set_param_option(options=['--prop'], var_name='prop_values', help='Directly set a property passed to the request')
    def update(self, tnco_client: TNCOClient, ctx: click.Context, name: str = None, id: str = None, file_content: Dict = None, set_values: Dict = None, prop_values: Dict = None):
        api = tnco_client.assemblies
        # Build request
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-f, --file" option', ctx=ctx)
            if prop_values is not None and len(prop_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--prop" option when using "-f, --file" option', ctx=ctx)
            assembly_req = file_content
        else:
            assembly_req = set_values
            if assembly_req is None:
                assembly_req = {}
            if 'properties' not in assembly_req or type(assembly_req['properties']) != dict:
                assembly_req['properties'] = {}
            if prop_values is not None:
                assembly_req['properties'].update(prop_values)
        assembly_req = self._resolve_assembly_identity_crisis(ctx, request_content=assembly_req, name=name, id=id)
        result = api.intent_upgrade(assembly_req)
        ctl = self._get_controller()
        ctl.io.print(f'Accepted - Process: {result}')

    @LmDelete(short_help=f'Request an intent to delete an {display_name}', 
                    help=f'''\
                        Request an intent to delete an {display_name}.
                        \n\nThe target {display_name} to be deleted may be identified by the "NAME" argument or the "--id" option or by including "assemblyId"/"assemblyName" in the contents of the "-f, --file" option, if set 
                        \n\nFor example:
                        \n\nDelete {display_name} using file: lmctl delete assembly -f my-request.yaml
                        \n\nDelete {display_name} by name: lmctl delete assembly my-assembly-name
                        \n\nDelete {display_name} by ID: lmctl delete assembly --id bd83f0df-1e82-48ac-8faa-1d772e0c49cd
                    ''',
                    print_result=False)
    @click.argument('name', required=False)
    @click.option('--id', help=f'Reference the target {display_name} by ID instead of name')
    def delete(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, name: str = None, id: str = None, ignore_missing: bool = None):
        api = tnco_client.assemblies
        assembly_req_content = self._resolve_assembly_identity_crisis(ctx, request_content=file_content, name=name, id=id)
        delete_req = {
            'assemblyId': assembly_req_content.get('assemblyId', None),
            'assemblyName': assembly_req_content.get('assemblyName', None)
        }
        try:
            result = api.intent_delete(delete_req)
        except TNCOClientHttpError as e:
            if e.status_code == 400 and ('Cannot find assembly instance with name' in e.detail_message or 'Cannot find assembly instance with id' in e.detail_message):
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    ctl.io.print(f'{e.detail_message} (ignoring)')
                    return
            raise
        ctl = self._get_controller()
        ctl.io.print(f'Accepted - Process: {result}')

    @LmCmd(short_help=f'Request an intent to change state of an {display_name}', 
                    help=f'''\
                        Request an intent to change state of an {display_name}.
                        \n\nThe target {display_name} may be identified by the "NAME" argument or the "--id" option or by including "assemblyId"/"assemblyName" in the contents of the "-f, --file" option, if set 
                        \n\nFor example:
                        \n\nChange state using file: lmctl changestate assembly -f my-request.yaml
                        \n\nChange state by name: lmctl changestate assembly my-assembly-name --intended-state Inactive
                        \n\nChange state by ID: lmctl changestate assembly --id bd83f0df-1e82-48ac-8faa-1d772e0c49cd --intended-state Inactive
                    ''')
    @click.argument('name', required=False)
    @click.option('--id', help=f'Reference the target {display_name} by ID instead of name')
    @click.option('--intended-state', '--state', help='Intended state to change to, if not included in "-f, --file" option')
    @file_inputs.option()
    def changestate(self, tnco_client: TNCOClient, ctx: click.Context, name: str = None, id: str = None, file_content: Dict = None, intended_state: str = None):
        api = tnco_client.assemblies
        assembly_req_content = self._resolve_assembly_identity_crisis(ctx, request_content=file_content, name=name, id=id)
        if 'intendedState' in assembly_req_content:
            if intended_state is not None and intended_state != assembly_req_content['intendedState']:
                included_state = assembly_req_content['intendedState']
                raise click.BadArgumentUsage(message=f'Request includes "intendedState" value of "{included_state}" but you have set the "--intended-state, --state" option value to a different value of "{intended_state}" - use one or the other', ctx=ctx)
        elif intended_state is not None:
            assembly_req_content['intendedState'] = intended_state
        else:
            raise click.BadArgumentUsage(message=f'Must set "--intended-state, --state" option or include "intendedState" attribute in content of file passed to "-f, --file" option to change Assembly state', ctx=ctx)
        change_state_req = {
            'assemblyId': assembly_req_content.get('assemblyId', None),
            'assemblyName': assembly_req_content.get('assemblyName', None),
            'intendedState': assembly_req_content.get('intendedState')
        }
        result = api.intent_change_state(change_state_req)
        ctl = self._get_controller()
        ctl.io.print(f'Accepted - Process: {result}')

    @LmCmd(short_help=f'Request an intent to adopt an {display_name}', 
                    help=f'''\
                        Request an intent to adopt an {display_name}. The request can include the following properties:
                        \n\nassemblyName - A unique name by which this {display_name} will be known externally. This cannot contain spaces, consecutive underscores or start with a numeric character.\
                        \n\ndescriptorName - The descriptor name from which this {display_name} will be created\
                        \n\nintendedState - The final intended state that the {display_name} should be brought into
                        \n\nproperties - An optional map of name and string value properties that is supplied to the new {display_name}
                        \n\nclusters - An optional map of cluster sizes, if the descriptor includes clusters\
                        \n\nresources - Associated topology for each resource instance
                    ''')
    def adopt(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None):
        api = tnco_client.assemblies
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-f, --file" option', ctx=ctx)
            assembly_req = file_content
        else:
            assembly_req = set_values
        result = api.intent_adopt(assembly_req)
        ctl = self._get_controller()
        ctl.io.print(f'Accepted - Process: {result}')

    def _resolve_assembly_identity_crisis(self, ctx: click.Context, request_content: Dict = None, name: str = None, id: str = None):
        if request_content is None:
            request_content = {}
        if name is not None and id is not None:
            raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "--id" option', ctx=ctx)
        elif name is not None:
            if 'assemblyName' not in request_content:
                request_content['assemblyName'] = name
            elif request_content['assemblyName'] != name:
                included_name = request_content['assemblyName']
                raise click.BadArgumentUsage(message=f'Request includes "assemblyName" value of "{included_name}" but you have set the "NAME" argument value to a different value of "{name}" - use one or the other', ctx=ctx)
        elif id is not None:
            if 'assemblyId' not in request_content:
                request_content['assemblyId'] = id
            elif request_content['assemblyId'] != id:
                included_id = request_content['assemblyId']
                raise click.BadArgumentUsage(message=f'Request includes "assemblyId" value of "{included_id}" but you have set the "--id" option value to a different value of "{id}" - use one or the other', ctx=ctx)
        return request_content
        