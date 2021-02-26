import click
from typing import Dict, List
from lmctl.client import TNCOClient, TNCOClientHttpError
from lmctl.cli.arguments import common_output_format_handler, default_output_format_handler
from lmctl.cli.format import Table, Column, TableFormat
from .tnco_target import TNCOTarget, LmGet, LmCreate, LmUpdate, LmDelete, LmGen

class ResourceManagerTable(Table):
    
    columns = [
        Column('name', header='Name'),
        Column('type', header='Type'),
        Column('url', header='URL')
    ]

class ResourceManagerOnboardingReportTable(Table):
    columns = [
        Column('name', header='Name'),
        Column('operation', header='Operation'),
        Column('success', header='Success'),
        Column('reason', header='Failure Reason'),
    ]

output_formats = common_output_format_handler(table=ResourceManagerTable())
onboarding_report_formats = common_output_format_handler(table=ResourceManagerOnboardingReportTable())

class ResourceManagers(TNCOTarget):
    name = 'resourcemanager'
    plural = 'resourcemanagers'
    display_name = 'Resource Manager'

    @LmGen()
    def genfile(self, ctx: click.Context, name: str):
        return {
            'name': name,
            'type': name, 
            'url': 'https://my-rm.example.com/api/resource-manager'
        }

    @LmGet(output_formats=output_formats, help=f'''\
                                            Get all {display_name}s or get by name\
                                            \n\nUse NAME argument to get by name\
                                            \n\nOmit NAME argument to get all''')
    @click.argument('name', required=False)
    def get(self, tnco_client: TNCOClient, ctx: click.Context, name: str = None):
        api = tnco_client.resource_managers
        if name is not None:
            return api.get(name)
        else:
            return api.all() 

    def _report_dict_to_list(self, orig: Dict) -> List:
        new_list = []
        ctl = self._get_controller()
        for k,v in orig.items():
            new_item = v
            new_item['name'] = k
            new_list.append(new_item)
        return new_list
   
    @LmCreate()
    @onboarding_report_formats.option()
    @click.option('--print-report', is_flag=True)
    def create(self, tnco_client: TNCOClient, 
                        ctx: click.Context, 
                        output_format: str, 
                        file_content: Dict = None, 
                        set_values: Dict = None,
                        print_report: bool = False):
        api = tnco_client.resource_managers
        output_formatter = onboarding_report_formats.resolve_choice(output_format)
        if file_content is not None:
            if set_values is not None and len(set_values) > 0:
                raise click.BadArgumentUsage(message='Do not use "--set" option when using "-f, --file" option', ctx=ctx)
            resource_manager = file_content
        else:
            resource_manager = set_values
        onboarding_report = api.create(resource_manager)
        if print_report:
            ctl = self._get_controller()
            if isinstance(output_formatter, TableFormat):
                # Print DL/Resources as two different tables
                name = resource_manager.get('name')
                operation = onboarding_report.get('resourceManagerOperation')
                ctl.io.print(f'Resource Manager Onboarding Report: {name}')
                ctl.io.print(f'Operation: {operation}')
                ctl.io.print(f'\nDeployment Locations:')
                ctl.io.print(output_formatter.convert_list(self._report_dict_to_list(onboarding_report.get('deploymentLocations', {}))))
                ctl.io.print(f'\nResources:')
                ctl.io.print(output_formatter.convert_list(self._report_dict_to_list(onboarding_report.get('resourceTypes', {}))))
            else:
                ctl.io.print(output_formatter.convert_element(onboarding_report))
        else:
            return resource_manager.get('name')

    @LmUpdate()
    @click.argument('name', required=False)
    @onboarding_report_formats.option()
    @click.option('--print-report', is_flag=True)
    def update(self, tnco_client: TNCOClient, 
                        ctx: click.Context,
                        output_format: str,
                        file_content: Dict = None, 
                        name: str = None, 
                        set_values: Dict = None,
                        print_report: bool = False):
        api = tnco_client.resource_managers
        output_formatter = onboarding_report_formats.resolve_choice(output_format)
        if file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            resource_manager = file_content
        else:
            if name is None:
                raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
            resource_manager = api.get(name)
            resource_manager.update(set_values)
        onboarding_report = api.update(resource_manager)
        if print_report:
            ctl = self._get_controller()
            if isinstance(output_formatter, TableFormat):
                # Print DL/Resources as two different tables
                name = resource_manager.get('name')
                operation = onboarding_report.get('resourceManagerOperation')
                ctl.io.print(f'Resource Manager Onboarding Report: {name}')
                ctl.io.print(f'Operation: {operation}')
                ctl.io.print(f'\nDeployment Locations:')
                ctl.io.print(output_formatter.convert_list(self._report_dict_to_list(onboarding_report.get('deploymentLocations', {}))))
                ctl.io.print(f'\nResources:')
                ctl.io.print(output_formatter.convert_list(self._report_dict_to_list(onboarding_report.get('resourceTypes', {}))))
            else:
                ctl.io.print(output_formatter.convert_element(onboarding_report))
        else:
            return resource_manager.get('name')

    @LmDelete()
    @click.argument('name', required=False)
    def delete(self, tnco_client: TNCOClient, ctx: click.Context, file_content: Dict = None, name: str = None, ignore_missing: bool = None):
        api = tnco_client.resource_managers
        if file_content is not None:
            if name is not None:
                raise click.BadArgumentUsage(message='Do not use "NAME" argument when using "-f, --file" option', ctx=ctx)
            resource_manager = file_content
            resource_manager_name = resource_manager.get('name', None)
            if resource_manager_name is None:
                raise click.BadArgumentUsage(message='Object from file does not contain a "name" attribute', ctx=ctx)
        else:
            if name is None:
                raise click.BadArgumentUsage(message='Must set "NAME" argument when no "-f, --file" option specified', ctx=ctx)
            resource_manager_name = name
        try:
            result = api.delete(resource_manager_name)
        except TNCOClientHttpError as e:
            if e.status_code == 404:
                # Not found
                if ignore_missing:
                    ctl = self._get_controller()
                    ctl.io.print(f'No {self.display_name} found with name {resource_manager_name} (ignoring)')
                    return
            raise
        return resource_manager_name