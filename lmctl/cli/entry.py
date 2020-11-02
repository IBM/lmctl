import click
import os
import logging
import urllib3
import lmctl.cli.commands as lmctl_commands
import lmctl.utils.logging as lmctl_logging
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.captureWarnings(True)

@click.group(help='TNCO (ALM) command line tools')
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

for action in lmctl_commands.actions:
    cli.add_command(action(targets=lmctl_commands.targets))

def init_cli():
    cli()
