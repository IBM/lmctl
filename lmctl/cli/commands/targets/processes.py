import click
from typing import Dict
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

    @LmGet(output_formats=output_formats, help=f'''Get the status of an {display_name}''')
    @click.argument('ID')
    @click.option('--shallow', is_flag=True, show_default=True, help='Retreive a shallow copy of the process')
    def get(self, lm_client: TNCOClient, ctx: click.Context, id: str, shallow: bool = False):
        api = lm_client.processes
        return api.get(id, shallow=shallow)