import click
from lmctl.utils.logging import log_dir
from lmctl.cli.io import IOController

@click.command(short_help='Print log file location', help='Print log file location')
def logdir():
    IOController.get().print(log_dir())