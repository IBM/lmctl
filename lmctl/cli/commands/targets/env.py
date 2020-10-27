import click
from .target import Target
from lmctl.cli.format import Table, Column, TableFormat
from lmctl.cli.arguments import common_output_format_handler
from lmctl.environment import EnvironmentGroup

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

class EnvironmentTable(Table):
    
    columns = [
        Column('name', header='Name'),
        Column('description', header='Description'),
        Column('lm', header='TNCO/ALM', accessor=lambda x: x.lm.address if x.lm else None),
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
        @click.pass_context
        def _get(ctx: click.Context, output_format: str, name: str = None):
            ctl = self._get_controller()
            output_formatter = output_formats.resolve_choice(output_format)
            table_selected = isinstance(output_formatter, TableFormat)
            if name is not None:
                if table_selected:
                    env = ctl.config.environments.get(name, None)
                else:
                    env = ctl.config.raw_environments.get(name, None)
                if env is None:
                    ctl.io.print_error(f'No environment named "{name}" could be found in current config file')
                    exit(1)
                result = env
            else:
                if table_selected:
                    result = list(ctl.config.environments.values())
                else:
                    result = ctl.config.raw_environments
            if isinstance(result, list):
                ctl.io.print(output_formatter.convert_list(result))
            else:
                ctl.io.print(output_formatter.convert_element(result))
        return _get
