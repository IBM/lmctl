import click
import os
import logging
import urllib3
import lmctl.cli.commands as lmctl_commands
import lmctl.utils.logging as lmctl_logging

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

@click.group()
@click.version_option()
def cli():
    """Lifecycle Manager Control tools"""

def init_cli():

    lmctl_logging.setup_logging()

    cli.add_command(lmctl_commands.deployment_group)
    cli.add_command(lmctl_commands.env_group)
    cli.add_command(lmctl_commands.lifecycledriver_group)
    cli.add_command(lmctl_commands.pkg_group)
    cli.add_command(lmctl_commands.project_group)
    cli.add_command(lmctl_commands.vimdriver_group)
    cli()
