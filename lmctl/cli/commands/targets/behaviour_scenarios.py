import click
from typing import Dict
from lmctl.client import TNCOClient, TNCOClientHttpError
from lmctl.cli.arguments import common_output_format_handler, set_param_option, default_file_inputs_handler
from lmctl.cli.format import Table, Column
from .tnco_target import TNCOTarget, LmGet, LmCreate, LmUpdate, LmDelete, LmGen, LmCmd

class ScenarioTable(Table):
    
    columns = [
        Column('id', header='ID'),
        Column('name', header='Name'),
        Column('description', header='Description')
    ]

output_formats = common_output_format_handler(table=ScenarioTable())

exec_file_inputs = default_file_inputs_handler()

class Scenarios(TNCOTarget):
    name = 'scenario'
    plural = 'scenarios'
    display_name = 'Scenario'

    @LmGen()
    def genfile(self, ctx: click.Context, name: str):
        return {
            'name': name,
            'projectId': 'assembly::example::1.0',
            'description': 'An example scenario',
            'stages': [
                {
                    'name': 'Default Stage',
                    'steps': [
                        {
                            'stepDefinitionName': 'Utilities::SleepForTime',
                            'properties': {
                                'sleepTime': '10'
                            }
                        }
                    ]
                }
            ],
            'assemblyActors': []
        }

    @LmCmd(help=f'''\
                    Execute a Behaviour Scenario (by ID)
                    ''')
    @click.argument('ID', required=False)
    @exec_file_inputs.option(var_name='scenario_file_content', help='Path to file containing a Scenario to be executed')
    @exec_file_inputs.option(var_name='exec_file_content', options=['-r', '--request-file'], help='Path to file with execution request parameters')
    @set_param_option(help='Set parameters on the execution request')
    def execute(self, tnco_client: TNCOClient, ctx: click.Context, id: str = None, set_values: Dict = None, scenario_file_content: Dict = None, exec_file_content: Dict = None):
        api = tnco_client.behaviour_scenario_execs
        if scenario_file_content is not None:
            if id is not None:
                raise click.BadArgumentUsage(message='Do not use "ID" argument when using "-f, --file" option', ctx=ctx)
            id = scenario_file_content.get('id', None)
            if id is None:
                raise click.BadArgumentUsage(message='Object from file does not contain an "id" attribute', ctx=ctx)
        elif id is None:
            raise click.BadArgumentUsage(message='Must set "ID" argument when no "-f, --file" option specified', ctx=ctx)
        if exec_file_content is not None and len(exec_file_content) > 0:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-r, --request-file" option', ctx=ctx)
            exec_request = exec_file_content
        else:
            exec_request = set_values
        execution_id = api.execute(scenario_id=id, execution_request=exec_request)
        return f'Created Scenario Execution: {execution_id}'

    @LmGet(output_formats=output_formats, help=f'''\
                                            Get {display_name} by ID or all in a Behaviour Project\
                                            \n\nUse ID argument to get by ID\
                                            \n\nOmit ID argument and set "--project" option to get all in a Behaviour Project''')
    @click.argument('ID', required=False)
    @click.option('--project', help=f'ID of a project to retrieve {display_name}s from')
    def get(self, tnco_client: TNCOClient, ctx: click.Context, id: str = None, project: str = None):
        api = tnco_client.behaviour_scenarios
        if id is not None:
            if project is not None:
                raise click.BadArgumentUsage('Do not use "ID" argument when using the "--project" option', ctx=ctx)
            return api.get(id)
        elif project is not None:
            return api.all_in_project(project)
        else:
            raise click.BadArgumentUsage('Must set either "ID" argument or "--project" option', ctx=ctx) 
        
    @LmCreate()
    def create(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, set_values: Dict = None):
        api = tnco_client.behaviour_scenarios
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-f, --file" option', ctx=ctx)
            scenario = file_content
        else:
            scenario = set_values
        result = api.create(scenario)
        return result.get('id')

    @LmUpdate()
    @click.argument('ID', required=False)
    def update(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, id: str = None, set_values: Dict = None):
        api = tnco_client.behaviour_scenarios
        if file_content is not None:
            if id is not None:
                raise click.BadArgumentUsage(message='Do not use "ID" argument when using "-f, --file" option', ctx=ctx)
            scenario = file_content
        else:
            if id is None:
                raise click.BadArgumentUsage(message='Must set "ID" argument when no "-f, --file" option specified', ctx=ctx)
            scenario = api.get(id)
            scenario.update(set_values)
        result = api.update(scenario)
        return scenario.get('id')

    @LmDelete()
    @click.argument('ID', required=False)
    def delete(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, id: str = None, ignore_missing: bool = None):
        api = tnco_client.behaviour_scenarios
        if file_content is not None:
            if id is not None:
                raise click.BadArgumentUsage(message='Do not use "ID" argument when using "-f, --file" option', ctx=ctx)
            scenario = file_content
            scenario_id = scenario.get('id', None)
            if scenario_id is None:
                raise click.BadArgumentUsage(message='Object from file does not contain an "id" attribute', ctx=ctx)
        else:
            if id is None:
                raise click.BadArgumentUsage(message='Must set "ID" argument when no "-f, --file" option specified', ctx=ctx)
            scenario_id = id
        try:
            result = api.delete(scenario_id)
        except TNCOClientHttpError as e:
            if e.status_code == 404:
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    ctl.io.print(f'No {self.display_name} found with ID {scenario_id} (ignoring)')
                    return
            raise
        return scenario_id