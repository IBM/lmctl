import click
from typing import Dict, List
from lmctl.client import TNCOClient, TNCOClientHttpError
from lmctl.cli.arguments import common_output_format_handler
from lmctl.cli.format import Table, Column
from .tnco_target import TNCOTarget, LmGet

class ProcessTable(Table):

    columns = [
        Column('startTime', header='Start Time'),
        Column('intentType', header='Intent'),
        Column('status', header='Status'),
        Column('assembly', header='Assembly', accessor=lambda x: x.get('assemblyName') + ' (' + x.get('assemblyId') + ')'),
    ]

output_formats = common_output_format_handler(table=ProcessTable())

class Processes(TNCOTarget):
    name = 'process'
    plural = 'processes'
    display_name = 'Assembly Process'

    @LmGet(output_formats=output_formats, short_help=f'''Get the status of an {display_name}''',
        help=f'''\
            Get the status of an {display_name}.
            \n\nA single Process can be retrieved by the "ID" argument or retrieve multiple Processes with a combination of filter options: 
            --assembly-id, --assembly-name, --assembly-type, --start-time, --end-time, --status, --intent-type, --limit
            ''')
    @click.argument('ID', required=False)
    @click.option('--deep', is_flag=True, show_default=True, help='Retreive a deep copy of the process (this can only be used when retrieving a single process by ID)')
    @click.option('--assembly-id', help='Filter processes to Assembly by ID')
    @click.option('--assembly-name', help='Filter processes to Assembly by Name')
    @click.option('--assembly-type', help='Filter processes to Assembly by Type')
    @click.option('--start-time', help='Filter processes by Start Date')
    @click.option('--end-time', help='Filter processes by End Date')
    @click.option('--status', multiple=True, help='Filter processes by Status (may provide option multiple times)')
    @click.option('--intent-type', multiple=True, help='Filter processes by Intent Type (may provide option multiple times)')
    @click.option('--limit', type=int, help='Limit the number of processes to retrieve')
    def get(self, 
                tnco_client: TNCOClient, 
                ctx: click.Context, 
                id: str, 
                deep: bool = False,
                assembly_id: str = None,
                assembly_name: str = None,
                assembly_type: str = None,
                start_time: str = None,
                end_time: str = None,
                status: List[str] = None,
                intent_type: List[str] = None,
                limit: int = None
            ):
        api = tnco_client.processes
        if id is not None:
            self._check_var_not_set_with_id(ctx, '--assembly-id', assembly_id)
            self._check_var_not_set_with_id(ctx, '--assembly-name', assembly_name)
            self._check_var_not_set_with_id(ctx, '--assembly-type', assembly_type)
            self._check_var_not_set_with_id(ctx, '--start-time', start_time)
            self._check_var_not_set_with_id(ctx, '--end-time', end_time)
            self._check_var_not_set_with_id(ctx, '--status', status, check_empty_list=True)
            self._check_var_not_set_with_id(ctx, '--intent-type', intent_type, check_empty_list=True)
            self._check_var_not_set_with_id(ctx, '--limit', limit)
            return api.get(id, shallow=(deep is False))
        else:
            if deep:
                raise click.BadArgumentUsage(message=f'Do not use "--deep" option when retrieving multiple processes', ctx=ctx)
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
            if status is not None and len(status) > 0:
                query_params['processStatuses'] = ','.join(status)
            if intent_type is not None and len(intent_type) > 0:
                query_params['intentTypes'] = ','.join(intent_type)
            if limit is not None:
                query_params['limit'] = limit
            return api.query(**query_params)
            
    def _check_var_not_set_with_id(self, ctx, var_name, var, check_empty_list=False):
        if var is not None:
            if check_empty_list and isinstance(var, (list,tuple)) and len(var) == 0:
                # Empty Lists are ok
                return
            raise click.BadArgumentUsage(message=f'Do not use "{var_name}" option when using "ID" argument', ctx=ctx)
            