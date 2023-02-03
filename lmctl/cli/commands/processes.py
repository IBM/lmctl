import click
from .utils import TNCOCommandBuilder, Identity, Identifier, pass_io
from .actions import get, retry, rollback, cancel
from lmctl.client import TNCOClient
from lmctl.cli.format import Column
from typing import List
from lmctl.cli.io import IOController

__all__ = (
    'get_process',
    'retry_process',
    'rollback_process',
    'cancel_process',
)

tnco_builder = TNCOCommandBuilder(
    singular='process',
    plural='processes',
    display_name='Process'
)

id_arg = Identifier(param_name='id')

default_columns = [
    Column('id', header='ID'),
    Column('startTime', header='Start Time'),
    Column('intentType', header='Intent'),
    Column('status', header='Status'),
    Column('assembly', header='Assembly', accessor=lambda x: x.get('assemblyName') + ' (' + x.get('assemblyId') + ')'),
]

@tnco_builder.make_get_command(
    identifiers=[id_arg],
    identifier_required=False,
    default_columns=default_columns,
    allow_file_input=False
)
@click.argument(id_arg.param_name, required=False)
@click.option('--deep', is_flag=True, show_default=True, help='Retreive a deep copy of the process (this can only be used when retrieving a single process by ID)')
@click.option('--assembly-id', help='Filter processes to Assembly by ID')
@click.option('--assembly-name', help='Filter processes to Assembly by Name')
@click.option('--assembly-type', help='Filter processes to Assembly by Type')
@click.option('--start-time', help='Filter processes by Start Date')
@click.option('--end-time', help='Filter processes by End Date')
@click.option('--status', 'statuses', multiple=True, help='Filter processes by Status (may provide option multiple times)')
@click.option('--intent-type', 'intent_types', multiple=True, help='Filter processes by Intent Type (may provide option multiple times)')
@click.option('--limit', type=int, help='Limit the number of processes to retrieve')
def get_process(
        tnco_client: TNCOClient, 
        identity: Identity, 
        deep: bool, 
        assembly_id: str, 
        assembly_name: str, 
        assembly_type: str, 
        start_time: str, 
        end_time: str, 
        statuses: List[str], 
        intent_types: List[str], 
        limit: int
    ):
    if identity is None and deep is True:
        raise click.UsageError(message=f'Do not use "--deep" option when retrieving multiple processes', ctx=click.get_current_context())
    api = tnco_client.processes
    if identity is not None:
        return api.get(identity.value, shallow=(deep is False))

    query_params = {}
    if assembly_id is not None:
        query_params['assemblyId'] = assembly_id
    if assembly_name is not None:
        query_params['assemblyName'] = assembly_name
    if assembly_type is not None:
        query_params['assemblyType'] = assembly_type
    if start_time is not None:
        query_params['startDateTime'] = start_time
    if end_time is not None:
        query_params['endDateTime'] = end_time
    if statuses is not None and len(statuses) > 0:
        query_params['processStatuses'] = ','.join(statuses)
    if intent_types is not None and len(intent_types) > 0:
        query_params['intentTypes'] = ','.join(intent_types)
    if limit is not None:
        query_params['limit'] = limit
    return api.query(**query_params)

accepted_process_prefix = 'Accepted -'

retry_help_suffix = f'''\
For example:
\n\nRetry process using {tnco_builder.display_name} ID: lmctl retry {tnco_builder.singular} 6ad3327e-79df-464f-af48-3283f871584d
'''

@tnco_builder.make_general_command(
    group=retry,
    short_help=f'Request an intent to retry a {tnco_builder.display_name}',
    help_prefix=f'Request an intent to retry a {tnco_builder.display_name}',
    identifiers=[id_arg],
    help_suffix=retry_help_suffix,
    pass_file_content=False,
    allow_file_input=False
)
@click.argument(id_arg.param_name,
               required=True)
@pass_io
def retry_process(
        tnco_client: TNCOClient,
        io: IOController,
        identity: Identity,
        ):

    obj = {}
    obj["processId"] = identity.value
    response = tnco_client.assemblies.intent_retry(obj)
    io.print(f'{accepted_process_prefix} Retry request for process: {identity.value}')
    return

rollback_help_suffix = f'''\
For example:
\n\nRollback process using {tnco_builder.display_name} ID: lmctl rollback {tnco_builder.singular} 6ad3327e-79df-464f-af48-3283f871584d
'''

@tnco_builder.make_general_command(
    group=rollback,
    short_help=f'Request an intent to rollback a {tnco_builder.display_name}',
    help_prefix=f'Request an intent to rollback a {tnco_builder.display_name}',
    identifiers=[id_arg],
    help_suffix=rollback_help_suffix,
    pass_file_content=False,
    allow_file_input=False
)
@click.argument(id_arg.param_name,
               required=True)
@pass_io
def rollback_process(
        tnco_client: TNCOClient,
        io: IOController,
        identity: Identity,
        ):
    obj = {}
    obj["processId"] = identity.value
    response = tnco_client.assemblies.intent_rollback(obj)
    io.print(f'{accepted_process_prefix} Rollback request for process: {identity.value}')
    return

cancel_help_suffix = f'''\
For example:
\n\nCancel process using {tnco_builder.display_name} ID: lmctl cancel {tnco_builder.singular} 6ad3327e-79df-464f-af48-3283f871584d
'''

@tnco_builder.make_general_command(
    group=cancel,
    short_help=f'Request an intent to cancel a {tnco_builder.display_name}',
    help_prefix=f'Request an intent to cancel a {tnco_builder.display_name}',
    identifiers=[id_arg],
    help_suffix=cancel_help_suffix,
    pass_file_content=False,
    allow_file_input=False
)
@click.argument(id_arg.param_name,
               required=True)
@pass_io
def cancel_process(
        tnco_client: TNCOClient,
        io: IOController,
        identity: Identity,
        ):
    obj = {}
    obj["processId"] = identity.value
    response = tnco_client.assemblies.intent_cancel(obj)
    io.print(f'{accepted_process_prefix} Cancel request for process: {identity.value}')
    return