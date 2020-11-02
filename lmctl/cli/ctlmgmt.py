import click
import lmctl.ctl.config as ctl_config
import lmctl.environment.group as envgroups
import lmctl.cli.output as output
import logging
import warnings
from .controller import get_global_controller


logger = logging.getLogger(__name__)


def get_ctl(config_path=None):
    warnings.warn('get_ctl is deprecated, use get_global_controller from lmctl.cli.controller instead', DeprecationWarning)
    try:
        return ctl_config.get_ctl(config_path)
    except (ctl_config.ConfigParserError, ctl_config.ConfigError) as e:
        output.printer.error('Error: Failed to load configuration - {0}'.format(str(e)))
        logger.exception(str(e))
        exit(1)

def get_environment_group(environment_group_name, config_path=None):
    warnings.warn('get_environment_group is deprecated, use get_global_controller from lmctl.cli.controller then use get_environment_group_named', DeprecationWarning)
    try:
        ctl = get_ctl(config_path)
    except (ctl_config.ConfigParserError, ctl_config.ConfigError) as e:
        output.printer.error('Error: Failed to load configuration - {0}'.format(str(e)))
        logger.exception(str(e))
        exit(1)
    try:
        return ctl.environment_group_named(environment_group_name)
    except ctl_config.ConfigError as e:
        output.printer.error('Error: {0}'.format(str(e)))
        logger.exception(str(e))
        exit(1)

def create_lm_session(environment_group_name, lm_pwd=None, config_path=None, lm_client_secret=None):
    warnings.warn('create_lm_session is deprecated as the LmSession class is deprecated, replaced with a new TNCOClient. Use get_global_controller from lmctl.cli.controller then use build_client', DeprecationWarning)
    env_group = get_environment_group(environment_group_name, config_path)
    if not env_group.has_lm:
        output.printer.error('Error: LM environment not configured on group: {0}'.format(environment_group_name))
    lm = env_group.lm
    lm_session_config = lm.create_session_config()
    if lm.is_secure:
        if lm_session_config.username is not None:
            if lm_pwd is not None and len(lm_pwd.strip()) > 0:
                lm_session_config.password = lm_pwd
            elif lm_session_config.password is None:
                prompt_pwd = click.prompt('Please enter password for LM user {0}'.format(lm_session_config.username), hide_input=True, default='')
                lm_session_config.password = prompt_pwd
        if lm_session_config.client_id is not None:
            if lm_session_config.client_secret is None:
                prompt_pwd = click.prompt('Please enter secret for LM client {0}'.format(lm_session_config.client_id), hide_input=True, default='')
                lm_session_config.client_secret = prompt_pwd
    return lm_session_config.create()

def create_arm_session(environment_group_name, arm_name, config_path=None):
    warnings.warn('create_arm_session is deprecated. Use get_global_controller from lmctl.cli.controller then use create_arm_session', DeprecationWarning)
    env_group = get_environment_group(environment_group_name, config_path)
    try:
        arm_env = env_group.arm_named(arm_name)
    except envgroups.EnvironmentRuntimeError as e:
        output.printer.error(str(e))
        logger.exception(str(e))
        exit(1)
    arm_session_config = arm_env.create_session_config()
    return arm_session_config.create()

