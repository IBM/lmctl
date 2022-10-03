import click
import logging

from .actions import get, use, ping, delete
from .utils import pass_io, Identifier
from lmctl.cli.controller import get_global_controller, CLIController
from lmctl.cli.tags import SETTINGS_TAG
from lmctl.cli.arguments import output_format_option, TNCOClientSecretOption, TNCOPwdOption, TNCOTokenOption, ignore_missing_option
from lmctl.cli.format import Column, OutputFormat, TableFormat, Table
from lmctl.environment import EnvironmentGroup
from lmctl.config import get_config_with_path, write_config

__all__ = (
    'get_env',
)

singular = 'env'
plural = 'envs'
display_name = 'Environment'

name_arg = Identifier(
    param_name='name'
)
active_opt = Identifier(
    param_name='active',
    param_opts = ['--active']
)

default_columns = [
    Column('name', header='Name', accessor=lambda x: f'{x.name} (active)' if hasattr(x, 'active') and x.active == True else x.name),
    Column('description', header='Description'),
    Column('cp4na', header='CP4NA', accessor=lambda x: x.tnco.address if x.tnco else None),
    Column('auth', header='Auth Type', accessor=lambda x: x.tnco.auth_mode if x.tnco else None),
]

ping_table = Table(columns=[
        Column('name', header='Test Name'),
        Column('result', header='Result', accessor=lambda x: 'OK' if x.passed else 'Failed'),
        Column('error', header='Error')
    ])

@get.command(singular, aliases=[plural], tags=[SETTINGS_TAG], help=f'Get an {display_name} from active LMCTL config file')
@click.argument(name_arg.param_name, required=False)
@click.option(*active_opt.param_opts, is_flag=True, default=False, show_default=True, help='Display the active environment (if set) rather than retrieving one by name')
@output_format_option(default_columns=default_columns)
def get_env(
        output_format: OutputFormat,
        name: str,
        active: bool
    ):
    if name is not None and active is True:
        raise click.UsageError(f'Cannot not use "{name_arg.get_cli_display_name()}" argument when using the "{active_opt.get_cli_display_name()}" option', ctx=click.get_current_context())

    ctl = get_global_controller()
    table_selected = isinstance(output_format, TableFormat)

    if name is None and active is False:
        # Get all
        result = [e for e in ctl.config.environments.values()]
    else:
        if active is True:
            if ctl.config.active_environment is None:
                raise click.UsageError(f'Cannot use "{active_opt.get_cli_display_name()}" option when no active environment is set in config', ctx=click.get_current_context())
            name = ctl.config.active_environment
        
        result = ctl.config.environments.get(name, None)
        if result is None:
            ctl.io.print_error(f'No environment named "{name}" could be found in current config file')
            exit(1)

    if isinstance(result, list):
        # Decorate with active
        if ctl.config.active_environment is not None:
            for env in result:
                if env.name == ctl.config.active_environment:
                    env.active = True
        ctl.io.print(output_format.convert_list(result))
    else:
        # Decorate with active
        if result and ctl.config.active_environment == result.name:
            result.active = True
        ctl.io.print(output_format.convert_element(result))

class PingEnvironmentCommand(click.Command):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.params.append(click.Argument([name_arg.param_name], required=False))
        self.params.append(TNCOClientSecretOption())
        self.params.append(TNCOPwdOption())
        self.params.append(TNCOTokenOption())

        self.behaviour = self.callback
        self.callback = self._callback
    
    def _callback(self, 
                    *args, 
                    name: str = None,
                    **kwargs):
        ctl = get_global_controller()
        environment = ctl.get_environment_group(name)
        result = self.behaviour(*args, ctl=ctl, environment=environment, **kwargs)

@ping.command(singular, cls=PingEnvironmentCommand, aliases=[plural], tags=[SETTINGS_TAG], 
        short_help=f'Test connection with an {display_name} from active LMCTL config file',
        help=f'''\
            Test connection with an {display_name} from active LMCTL config file
            \n\nConnection is tested by making requests to a few pre-selected APIs on the configured CP4NA orchestration'''
        )
@click.option('--include-template-engine', '--include-kami', 'include_template_engine', 
                is_flag=True, default=False, show_default=True, help='Include tests for connection to Kami, an optional demo component')
def ping_env(ctl: CLIController, environment: EnvironmentGroup, pwd: str, client_secret: str, token: str, include_template_engine: bool):
    happy_exit = True
    if environment.has_tnco:
        tnco_client = ctl.get_tnco_client(environment_group_name=environment.name, input_pwd=pwd, input_client_secret=client_secret, input_token=token)
        ctl.io.print(f'Pinging CP4NA orchestration: {environment.name} ({environment.tnco.address})')
        tnco_ping_result = tnco_client.ping(include_template_engine=include_template_engine)
        ctl.io.print(TableFormat(table=ping_table).convert_list(tnco_ping_result.tests))
        if tnco_ping_result.passed:
            ctl.io.print(f'CP4NA orchestration tests passed! ✅')
        else:
            ctl.io.print_error(f'CP4NA orchestration tests failed! ❌')
            happy_exit = False
    else:
        ctl.io.print('No CP4NA orchestration configured (skipping)')
    if not happy_exit:
        exit(1)

@use.command(singular, aliases=[plural], tags=[SETTINGS_TAG], help=f'Change the active environment (default environment used by commands)')
@click.argument(name_arg.param_name, required=True)
def use_env(name: str):
    loaded_config, config_path = get_config_with_path()
    ctl = get_global_controller()
    if name not in loaded_config.environments:
        valid_env_names = [k for k in loaded_config.environments.keys()]
        ctl.io.print_error(f'No environment named "{name}" found in config. Valid names: {valid_env_names}')
        exit(1)

    # Update
    ctl.io.print(f'Updating config at: {config_path}')
    loaded_config.active_environment = name
    write_config(loaded_config, override_config_path=config_path)

@delete.command(singular, aliases=[plural], help=f'Remove an environment from active LMCTL config file')
@click.argument(name_arg.param_name, required=False)
@click.option(*active_opt.param_opts, is_flag=True, default=False, show_default=True, help='Remove the active environment (if set)')
@ignore_missing_option()
def delete_env(name: str, active: bool, ignore_missing: bool):
    if name is not None and active is True:
        raise click.UsageError(f'Cannot not use "{name_arg.get_cli_display_name()}" argument when using the "{active_opt.get_cli_display_name()}" option', ctx=click.get_current_context())

    ctl = get_global_controller()
    if name is None and active is False:
        raise click.UsageError(f'Must specify "{name_arg.get_cli_display_name()}" argument or "{active_opt.get_cli_display_name()}" option', ctx=click.get_current_context())

    if active is True:
        if ctl.config.active_environment is None:
            if ignore_missing:
                ctl.io.print(f'(Ignored) No active environment')
                exit(0)
            else:
                raise click.UsageError(f'Cannot use "{active_opt.get_cli_display_name()}" option when no active environment is set in config', ctx=click.get_current_context())
        else:
            name = ctl.config.active_environment
 
    removed_env = ctl.config.environments.pop(name, None)
    if removed_env is None:
        if ignore_missing:
            ctl.io.print(f'(Ignored) No environment named "{name}" could be found in current config file')
            exit(0)
        else:
            ctl.io.print_error(f'No environment named "{name}" could be found in current config file')
            exit(1)
    else:
        ctl.io.print(f'Removed environment: {removed_env.name}')
        # Dont forget to unset the active environment if currently set to the environment being removed
        if ctl.config.active_environment == removed_env.name:
            ctl.config.active_environment = None
            ctl.io.print(f'Clearing {removed_env.name} as the active environment (run "lmctl use env" to make another environment active)')
        ctl.io.print(f'Updating config at: {ctl.config_path}')
        write_config(ctl.config, override_config_path=ctl.config_path)    


######### Deprecated

import sys
import lmctl.cli.ctlmgmt as ctlmgmt
from lmctl.cli.controller import get_global_controller
from lmctl.cli.format import determine_format_class, TableFormat

logger = logging.getLogger(__name__)

######################################################
# env command line functions
######################################################

@click.group(short_help='Use "get env"', hidden=True, help='deprecated in v3.0: Commands for inspecting available CP4NA orchestration environments')
def env():
    logger.debug('Environments')


@env.command('list', help='List available CP4NA orchestration environments')
@click.option('--config', default=None, help='path to lmctl configuration file, if empty then the LMCONFIG environment variable will be used instead')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def list_envs(config, output_format):
    """List available environments"""
    ctl = get_global_controller(override_config_path=config)
    environments = []
    if ctl.config.environments is not None:
        environments = __parse_envs_to_list(ctl.config.environments)
    formatter_class = determine_format_class(output_format)
    if formatter_class is TableFormat:
        formatter = formatter_class(env_headers, env_row_processor)
    else:
        formatter = formatter_class()
    result = formatter.convert_list(environments)
    click.echo(result)


def __parse_envs_to_list(environments):
    env_list = []
    for group_name, group in environments.items():
        env = {'name': group_name, 'description': group.description}
        if group.has_lm:
            env['lm'] = group.tnco.address
        else:
            env['lm'] = 'N/A'
        arms = group.arms
        if len(arms) > 0:
            arms_str = ''
            for arm_name, arm_env in arms.items():
                if len(arms_str) > 0:
                    arms_str += '\n'
                arms_str += '{0} - {1}'.format(arm_name, arm_env.address)
        else:
            arms_str = 'N/A'
        env['arms'] = arms_str
        env_list.append(env)
    return env_list


env_headers = ['name', 'description', 'lm', 'arms']


def env_row_processor(env):
    table_row = []
    table_row.append(env['name'])
    table_row.append(env['description'])
    table_row.append(env['lm'])
    table_row.append(env['arms'])
    return table_row
