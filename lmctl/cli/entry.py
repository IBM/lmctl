import click
import os
import logging
import urllib3
import lmctl.cli.commands as lmctl_commands
import lmctl.utils.logging as lmctl_logging
from .safety_net import safety_net
from .cmd_tags import TagFormattedGroup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.captureWarnings(True)


@click.group(cls=TagFormattedGroup, help=f'CP4NA orchestration command line tools')
@click.version_option()
def cli():
    pass


lmctl_logging.setup_logging()

cli.add_command(lmctl_commands.deployment_group)
cli.add_command(lmctl_commands.env_group)
cli.add_command(lmctl_commands.resourcedriver_group)
cli.add_command(lmctl_commands.pkg_group)
cli.add_command(lmctl_commands.project_group)
cli.add_command(lmctl_commands.key_group)    
cli.add_command(lmctl_commands.lifecycledriver_group) 
cli.add_command(lmctl_commands.vimdriver_group) 
cli.add_command(lmctl_commands.login_cmd) 
cli.add_command(lmctl_commands.logdir_cmd)

for action in lmctl_commands.action_types:
    cli.add_command(action(targets=lmctl_commands.target_instances))

def init_cli():
    with safety_net():
        cli()
