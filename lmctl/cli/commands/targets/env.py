import click
from .target import Target
from lmctl.client import TNCOClientError
from lmctl.cli.io import IOController
from lmctl.cli.format import Table, Column, TableFormat
from lmctl.cli.arguments import common_output_format_handler, tnco_client_secret_option, tnco_pwd_option
from lmctl.cli.safety_net import safety_net
from lmctl.environment import EnvironmentGroup
from lmctl.config import ConfigError, get_config_with_path, write_config

def build_arms_string(env_group: EnvironmentGroup):
    arms = env_group.arms
    arms_str = None
    if len(arms) > 0:
        arms_str = ''
        for arm_name, arm_env in arms.items():
            if len(arms_str) > 0:
                arms_str += '\n'
            arms_str += '{0} - {1}'.format(arm_name, arm_env.address)
    return arms_str

class PingTable(Table):
    columns = [
        Column('name', header='Test Name'),
        Column('result', header='Result', accessor=lambda x: 'OK' if x.passed else 'Failed'),
        Column('error', header='Error')
    ]

class EnvironmentTable(Table):
    
    columns = [
        Column('name', header='Name'),
        Column('description', header='Description'),
        Column('tnco', header='TNCO/ALM', accessor=lambda x: x.tnco.address if x.tnco else None),
        Column('auth', header='Auth', accessor=lambda x: x.tnco.auth_mode if x.tnco else None),
        Column('arm', header='Ansible RM', accessor=build_arms_string)
    ]

output_formats = common_output_format_handler(table=EnvironmentTable())

class Environments(Target):
    name = 'env'
    plural = 'envs'
    display_name = 'Environments'

    def get(self):
        @click.command(help=f'Get LMCTL {self.display_name} from active config file')
        @output_formats.option()
        @click.argument('name', required=False)
        @click.option('--active', is_flag=True, default=False, help='Display the active environment (if set) rather than retrieving one by name')
        @click.pass_context
        def _get(ctx: click.Context, output_format: str, name: str = None, active: bool = False):
            ctl = self._get_controller()
            output_formatter = output_formats.resolve_choice(output_format)
            table_selected = isinstance(output_formatter, TableFormat)
            if name is None and active is False:
                # Get all
                result = list(ctl.config.environments.values())
            else:
                if active is True:
                    if name is not None:
                        raise click.BadArgumentUsage('Do not use "NAME" argument when using the "--active" option', ctx=ctx)
                    if ctl.config.active_environment is None:
                        raise click.BadArgumentUsage('Cannot use "--active" option when no active environment is set in config', ctx=ctx)
                    name = ctl.config.active_environment
                result = ctl.config.environments.get(name, None)
                if result is None:
                    ctl.io.print_error(f'No environment named "{name}" could be found in current config file')
                    exit(1)
            if isinstance(result, list):
                ctl.io.print(output_formatter.convert_list(result))
            else:
                ctl.io.print(output_formatter.convert_element(result))
        return _get

    def ping(self):
        @click.command(help=f'''\
                    Test connection with {self.display_name} from active config file
                    \n\nConnection is tested by making requests to a few pre-selected APIs on the configured CP4NA orchestration''')
        @click.argument('name', required=False)
        @tnco_client_secret_option()
        @tnco_pwd_option()
        @click.option('--include-template-engine', '--include-kami', 'include_template_engine', is_flag=True, help='Include tests for connection to Kami, an optional demo component')
        @click.pass_context
        def _ping(ctx: click.Context, name: str = None, pwd: str = None, client_secret: str = None, include_template_engine: bool = False):
            ctl = self._get_controller()
            env = ctl.get_environment_group(name)
            happy_exit = True
            if env.has_tnco:
                tnco_client = ctl.get_tnco_client(environment_group_name=name, input_pwd=pwd, input_client_secret=client_secret)
                ctl.io.print(f'Pinging CP4NA orchestration: {env.tnco.address}')
                tnco_ping_result = tnco_client.ping(include_template_engine=include_template_engine)
                ctl.io.print(TableFormat(table=PingTable()).convert_list(tnco_ping_result.tests))
                if tnco_ping_result.passed:
                    ctl.io.print(f'CP4NA orchestration tests passed! ✅')
                else:
                    ctl.io.print_error(f'CP4NA orchestration tests failed! ❌')
                    happy_exit = False
            else:
                ctl.io.print('No CP4NA orchestration configured (skipping)')
            if not happy_exit:
                exit(1)
        return _ping

    def use(self):
        @click.command(help=f'Change the active environment (default environment used by commands)')
        @click.argument('environment_name')
        @click.pass_context
        def _use(ctx: click.Context, environment_name: str):
            with safety_net(ConfigError):
                loaded_config, config_path = get_config_with_path()
            io = IOController.get()
            if environment_name not in loaded_config.environments:
                valid_env_names = [k for k in loaded_config.environments.keys()]
                io.print_error(f'No environment named "{environment_name}" found in config. Valid names: {valid_env_names}')
                exit(1)

            # Update
            io.print(f'Updating config at: {config_path}')
            loaded_config.active_environment = environment_name
            write_config(loaded_config, override_config_path=config_path)
        return _use
