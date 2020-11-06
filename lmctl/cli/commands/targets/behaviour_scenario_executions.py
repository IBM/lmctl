import click
from typing import Dict
from lmctl.client import TNCOClient, TNCOClientHttpError
from lmctl.cli.arguments import common_output_format_handler
from lmctl.cli.format import Table, Column
from .tnco_target import TNCOTarget, LmGet, LmCreate, LmUpdate, LmDelete, LmCmd
#, accessor=lambda x: x.get('scenarioSummary').get('name') if 'scenarioSummary' in x else None),
class ScenarioExecutionTable(Table):
    
    columns = [
        Column('id', header='ID'),
        Column('name', header='Execution Name'),
        Column('scenarioId', header='Scenario'),
        Column('startedAt', header='Started At'),
        Column('status', header='Status')
    ]

output_formats = common_output_format_handler(table=ScenarioExecutionTable())

class ScenarioExecutions(TNCOTarget):
    name = 'scenarioexecution'
    plural = 'scenarioexecutions'
    display_name = 'Scenario Execution'

    @LmCmd(help=f'''\
                Cancel {display_name} by ID
                ''')
    @click.argument('ID')
    def cancel(self, tnco_client: TNCOClient, ctx: click.Context, id: str = None):
        api = tnco_client.behaviour_scenario_execs
        result = api.cancel(id)
        if 'success' in result and result['success'] is False:
            ctl = self._get_controller()
            ctl.io.print_error(f'Request to cancel {display_name} "{id}" returned unsuccessful response')
            exit(1)
        else:
            return f'Cancelled: {id}'

    @LmGet(output_formats=output_formats, help=f'''\
                                            Get {display_name} by ID or all in a Behaviour Project or all of a particular Behaviour Scenario\
                                            \n\nUse ID argument to get by ID\
                                            \n\nOmit ID argument and set "--scenario" option to get all of a particular Behaviour Scenario
                                            \n\nOmit ID argument and set "--project" option to get all in a Behaviour Project''')
    @click.argument('ID', required=False)
    @click.option('--project', help=f'ID of a project to retrieve {display_name}s from')
    @click.option('--scenario', help=f'ID of a scenario to retrieve {display_name}s of')
    def get(self, tnco_client: TNCOClient, ctx: click.Context, id: str = None, project: str = None, scenario: str = None):
        api = tnco_client.behaviour_scenario_execs
        if id is not None:
            if project is not None:
                raise click.BadArgumentUsage('Do not use "ID" argument when using the "--project" option', ctx=ctx)
            if scenario is not None:
                raise click.BadArgumentUsage('Do not use "ID" argument when using the "--scenario" option', ctx=ctx)
            return api.get(id)
        elif project is not None:
            if scenario is not None:
                raise click.BadArgumentUsage('Do not use "--project" option when using the "--scenario" option', ctx=ctx)
            return api.all_in_project(project)
        elif scenario is not None:
            return api.all_of_scenario(scenario)
        else:
            raise click.BadArgumentUsage('Must set one of "ID" argument, "--project" option or "--scenario" option', ctx=ctx) 

    @LmDelete()
    @click.argument('ID', required=False)
    def delete(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, id: str = None, ignore_missing: bool = None):
        api = tnco_client.behaviour_scenario_execs
        if file_content is not None:
            if id is not None:
                raise click.BadArgumentUsage(message='Do not use "ID" argument when using "-f, --file" option', ctx=ctx)
            scenario_exec = file_content
            scenario_exec_id = scenario_exec.get('id', None)
            if scenario_exec_id is None:
                raise click.BadArgumentUsage(message='Object from file does not contain an "id" attribute', ctx=ctx)
        else:
            if id is None:
                raise click.BadArgumentUsage(message='Must set "ID" argument when no "-f, --file" option specified', ctx=ctx)
            scenario_exec_id = id
        try:
            result = api.delete(scenario_exec_id)
        except TNCOClientHttpError as e:
            if e.status_code == 404:
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    ctl.io.print(f'No {self.display_name} found with ID {scenario_exec_id} (ignoring)')
                    return
            raise
        return scenario_exec_id