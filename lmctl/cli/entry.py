import click
import os
import logging
import urllib3
import lmctl.cli.commands as lmctl_commands
import lmctl.utils.logging as lmctl_logging

from lmctl.cli.commands import action_groups

from .safety_net import safety_net
from .commands.super_group import SuperGroup
from .tags import SETTINGS_TAG, ACTIONS_TAG, PROJECT_TAG, DEPRECATED_TAG

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.captureWarnings(True)

@click.group(cls=SuperGroup, tag_order=[SETTINGS_TAG, ACTIONS_TAG, PROJECT_TAG, DEPRECATED_TAG], help=f'CP4NA orchestration command line tools')
@click.version_option()
def cli():
    pass


lmctl_logging.setup_logging()

cli.add_command(lmctl_commands.deployment_group, tags=[DEPRECATED_TAG])
cli.add_command(lmctl_commands.env_group, tags=[DEPRECATED_TAG])
cli.add_command(lmctl_commands.resourcedriver_group, tags=[DEPRECATED_TAG])
cli.add_command(lmctl_commands.pkg_group, tags=[PROJECT_TAG])
cli.add_command(lmctl_commands.project_group, tags=[PROJECT_TAG])
cli.add_command(lmctl_commands.key_group, tags=[DEPRECATED_TAG])
cli.add_command(lmctl_commands.lifecycledriver_group, tags=[DEPRECATED_TAG]) 
cli.add_command(lmctl_commands.vimdriver_group, tags=[DEPRECATED_TAG]) 
cli.add_command(lmctl_commands.login_cmd, tags=[SETTINGS_TAG])
cli.add_command(lmctl_commands.logdir_cmd, tags=[SETTINGS_TAG])
cli.add_command(lmctl_commands.whoami_cmd, tags=[SETTINGS_TAG])

ACTION_EXTRA_TAGS = {
    'use': [SETTINGS_TAG],
    'ping': [SETTINGS_TAG]
}

for action_group_definition in action_groups:
    action_group = action_group_definition['group']
    if action_group.name in ACTION_EXTRA_TAGS:
        tags = ACTION_EXTRA_TAGS[action_group.name]
    else:
        tags = []
    tags = tags + [ACTIONS_TAG]
    cli.add_command(action_group, aliases=action_group_definition['aliases'], tags=tags)

def init_cli():
    with safety_net():
        cli()
