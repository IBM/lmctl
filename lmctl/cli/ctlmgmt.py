import click
import lmctl.ctl.config as ctl_config
import lmctl.environment.group as envgroups
import lmctl.cli.output as output
import logging


logger = logging.getLogger(__name__)


def get_ctl(config_path=None):
    try:
        return ctl_config.get_ctl(config_path)
    except (ctl_config.ConfigParserError, ctl_config.ConfigError) as e:
        output.printer.error('Error: Failed to load configuration - {0}'.format(str(e)))
        logger.exception(str(e))
        exit(1)

def get_environment_group(environment_group_name, config_path=None):
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
    

def create_lm_session(environment_group_name, lm_pwd=None, config_path=None):
    env_group = get_environment_group(environment_group_name, config_path)
    if not env_group.has_lm:
        output.printer.error('Error: LM environment not configured on group: {0}'.format(environment_group_name))
    lm = env_group.lm
    lm_session_config = lm.create_session_config()
    if lm.is_secure:
        if lm_pwd is not None and len(lm_pwd.strip()) > 0:
            lm_session_config.password = lm_pwd
        elif lm_session_config.password is None:
            prompt_pwd = click.prompt('Please enter password for LM user {0}'.format(lm_session_config.username), hide_input=True, default='')
            lm_session_config.password = prompt_pwd
    return lm_session_config.create()

def create_arm_session(environment_group_name, arm_name, config_path=None):
    env_group = get_environment_group(environment_group_name, config_path)
    try:
        arm_env = env_group.arm_named(arm_name)
    except envgroups.EnvironmentRuntimeError as e:
        output.printer.error(str(e))
        logger.exception(str(e))
        exit(1)
    arm_session_config = arm_env.create_session_config()
    return arm_session_config.create()

