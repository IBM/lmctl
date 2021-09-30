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

def get_environment_group(environment_group_name: str = None, config_path=None):
    warnings.warn('get_environment_group is deprecated, use get_global_controller from lmctl.cli.controller then use get_environment_group_named', DeprecationWarning)
    try:
        ctl = get_ctl(config_path)
    except (ctl_config.ConfigParserError, ctl_config.ConfigError) as e:
        output.printer.error('Error: Failed to load configuration - {0}'.format(str(e)))
        logger.exception(str(e))
        exit(1)
    env_group = ctl.config.environments.get(environment_group_name, None)
    if env_group is None:
        if environment_group_name is not None:
            output.printer.error(f'Error: No environment named: {environment_group_name}')
            exit(1)
        env_group = get_active_environment(ctl)
    if env_group is None:
        output.printer.error(f'Error: Environment name not provided and there is no "active_environment" group set in config. ' +
                                'Check command --help for ways to provide"-e/--environment" or environment argument. ' + 
                                'Alternatively, add "active_environment" to lmctl config with the name of the environment (from the same config) you would like to use as the default')
        exit(1)
    return env_group

def get_active_environment(ctl):
    if ctl.config.active_environment is not None:
        env_group = ctl.config.environments.get(ctl.config.active_environment, None)
        if env_group is None:
            output.printer.error(f'Error: "active_environment" group set to "{ctl.config.active_environment}" but there is no environment with that name found in config')
            exit(1)
        else:
            return env_group
    return None

def create_lm_session(environment_group_name = None, lm_pwd=None, config_path=None, lm_client_secret=None, lm_token=None):
    warnings.warn('create_lm_session is deprecated as the LmSession class is deprecated, replaced with a new TNCOClient. Use get_global_controller from lmctl.cli.controller then use build_client', DeprecationWarning)
    env_group = get_environment_group(environment_group_name, config_path)
    if not env_group.has_lm:
        output.printer.error('Error: CP4NA orchestration environment not configured on group: {0}'.format(environment_group_name))
    lm = env_group.tnco
    lm_session_config = lm.create_session_config()
    if lm.secure:
        if lm_session_config.is_using_zen_auth:
            if lm_session_config.username is not None:
                if lm_pwd is not None and len(lm_pwd.strip()) > 0:
                    lm_session_config.api_key = lm_pwd
                elif lm_session_config.api_key is None:
                    prompt_pwd = click.prompt(f'Please enter API key for LM user {lm_session_config.username}', hide_input=True, default='')
                    lm_session_config.api_key = prompt_pwd
        elif lm_session_config.is_using_token_auth:
            if lm_token is not None and len(lm_token.strip()) > 0:
                lm_session_config.token = lm_token
            elif lm_session_config.token is None:
                prompt_token = click.prompt(f'Please enter token for CP4NA orchestration', hide_input=True, default='')
                lm_session_config.token = prompt_token
        else:
            if lm_session_config.username is not None:
                if lm_pwd is not None and len(lm_pwd.strip()) > 0:
                    lm_session_config.password = lm_pwd
                elif lm_session_config.password is None:
                    prompt_pwd = click.prompt('Please enter password for CP4NA orchestration user {0}'.format(lm_session_config.username), hide_input=True, default='')
                    lm_session_config.password = prompt_pwd
            if lm_session_config.client_id is not None:
                if lm_session_config.client_secret is None:
                    prompt_pwd = click.prompt('Please enter secret for CP4NA orchestration client {0}'.format(lm_session_config.client_id), hide_input=True, default='')
                    lm_session_config.client_secret = prompt_pwd
    return lm_session_config.create()

def create_arm_session(arm_name, environment_group_name=None, config_path=None):
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

