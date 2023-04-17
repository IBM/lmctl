import click
import logging
from .utils import TNCOCommandBuilder, Identity, Identifier, pass_io
from lmctl.cli.io import IOController
from lmctl.client import TNCOClient
from lmctl.cli.format import Column, OutputFormat, TableFormat
from lmctl.cli.arguments import output_format_option
from typing import Dict, Any, Type, List

logger = logging.getLogger(__name__)


__all__ = (
    'generate_resource_manager',
    'create_resource_manager',
    'update_resource_manager',
    'delete_resource_manager',
    'get_resource_manager',
)

tnco_builder = TNCOCommandBuilder(
    singular='resourcemanager',
    plural='resourcemanagers',
    display_name='Resource Manager'
)

name = Identifier.arg_and_attr('name')

default_columns = [
    Column('name', header='Name'),
    Column('type', header='Type'),
    Column('url', header='URL')
]

default_report_columns = [
        Column('name', header='Name'),
        Column('operation', header='Operation'),
        Column('success', header='Success'),
        Column('reason', header='Failure Reason'),
    ]

@tnco_builder.make_generate_command()
def generate_resource_manager():
    return {
            'name': 'example',
            'type': 'example', 
            'url': 'https://my-rm.example.com/api/resource-manager'
        }

def report_dict_to_list(orig: Dict) -> List:
    new_list = []
    for k,v in orig.items():
        new_item = v
        new_item['name'] = k
        new_list.append(new_item)
    return new_list

@tnco_builder.make_create_command(print_result=False, hidden=True)
@output_format_option(default_columns=default_report_columns)
@click.option('--print-report', default=False, 
                                show_default=True, 
                                is_flag=True, 
                                help='''\
                                    Print the onboarding report returned by the request, 
                                    which describes the Resource Types and Deployment Locations registered by this Resource Manager''')
@pass_io
def create_resource_manager(tnco_client: TNCOClient, obj: Dict[str, Any], io: IOController, print_report: bool, output_format: OutputFormat):
    onboarding_report = tnco_client.resource_managers.create(obj)
    name = obj.get('name')
    if print_report:
        if isinstance(output_format, TableFormat):
            # Print DL/Resources as two different tables
            operation = onboarding_report.get('resourceManagerOperation')
            io.print(f'Resource Manager Onboarding Report: {name}')
            io.print(f'Operation: {operation}')
            io.print(f'\nDeployment Locations:')
            io.print(output_format.convert_list(report_dict_to_list(onboarding_report.get('deploymentLocations', {}))))
            io.print(f'\nResources:')
            io.print(output_format.convert_list(report_dict_to_list(onboarding_report.get('resourceTypes', {}))))
        else:
            io.print(output_format.convert_element(onboarding_report))
    else:
        io.print(f'Created: {name}')

@tnco_builder.make_update_command(identifiers=[name], print_result=False, hidden=True)
@click.argument(name.param_name, required=False)
@output_format_option(default_columns=default_report_columns)
@click.option('--print-report', default=False, 
                                show_default=True, 
                                is_flag=True, 
                                help='''\
                                    Print the onboarding report returned by the request, 
                                    which describes the Resource Types and Deployment Locations registered by this Resource Manager''')
@pass_io
def update_resource_manager(tnco_client: TNCOClient, identity: Identity, obj: Dict[str, Any], patchable: bool, io: IOController, print_report: bool, output_format: OutputFormat):
    name = identity.value
    if patchable:
        patch_values = obj
        obj = tnco_client.resource_managers.get(name)
        obj.update(patch_values)
    else:
        obj['name'] = name
    onboarding_report = tnco_client.resource_managers.update(obj)
    if print_report:
        if isinstance(output_format, TableFormat):
            # Print DL/Resources as two different tables
            operation = onboarding_report.get('resourceManagerOperation')
            io.print(f'Resource Manager Onboarding Report: {name}')
            io.print(f'Operation: {operation}')
            io.print(f'\nDeployment Locations:')
            io.print(output_format.convert_list(report_dict_to_list(onboarding_report.get('deploymentLocations', {}))))
            io.print(f'\nResources:')
            io.print(output_format.convert_list(report_dict_to_list(onboarding_report.get('resourceTypes', {}))))
        else:
            io.print(output_format.convert_element(onboarding_report))
    else:
        io.print(f'Updated: {name}')

@tnco_builder.make_get_command(
    identifiers=[name],
    identifier_required=False,
    default_columns=default_columns, 
    hidden=True
)
@click.argument(name.param_name, required=False)
def get_resource_manager(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.resource_managers
    if identity is None:
        return api.all()
    else:
        resource_manager_name = identity.value
        return api.get(resource_manager_name)

@tnco_builder.make_delete_command(identifiers=[name], hidden=True)
@click.argument(name.param_name, required=False)
def delete_resource_manager(tnco_client: TNCOClient, identity: Identity):
    api = tnco_client.resource_managers
    resource_manager_name = identity.value
    api.delete(resource_manager_name)
    return resource_manager_name
