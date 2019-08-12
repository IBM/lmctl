import click
import os
import logging
import lmctllib.commands as lmctl_commands
import lmctllib.utils.logging as lmctl_logging
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

@click.group()
@click.version_option()
def cli():
  """Lifecycle Manager Control tools"""

def main_func():

  lmctl_logging.setup_logging()

  cli.add_command(lmctl_commands.env)
  cli.add_command(lmctl_commands.project)
  cli.add_command(lmctl_commands.pkg)
  cli()

