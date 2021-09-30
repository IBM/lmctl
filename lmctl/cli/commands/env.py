import click
import sys
import logging
import lmctl.cli.ctlmgmt as ctlmgmt
from lmctl.cli.controller import get_global_controller
from lmctl.cli.format import determine_format_class, TableFormat
from lmctl.cli.cmd_tags import deprecated_tag

logger = logging.getLogger(__name__)

######################################################
# env command line functions
######################################################

@deprecated_tag
@click.group(short_help='Use "get env"', help='deprecated in v3.0: Commands for inspecting available CP4NA orchestration environments')
def env():
    logger.debug('Environments')


@env.command(help='List available CP4NA orchestration environments')
@click.option('--config', default=None, help='path to lmctl configuration file, if empty then the LMCONFIG environment variable will be used instead')
@click.option('-f', '--format', 'output_format', default='table', help='format of output [table, yaml, json]')
def list(config, output_format):
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
