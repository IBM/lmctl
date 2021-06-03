import click
import logging
from lmctl.cli.io import IOController
from lmctl.config import get_global_config, Config, ConfigError
from lmctl.environment import EnvironmentGroup
from .safety_net import safety_net, tnco_client_safety_net

logger = logging.getLogger(__name__)

class CLIController:
    
    def __init__(self, config: Config):
        self.config = config
        self.io = IOController.get()

    def safety_net(self, *catchable_exceptions):
        return safety_net(*catchable_exceptions, io_controller=self.io)

    def tnco_client_safety_net(self):
        return tnco_client_safety_net(io_controller=self.io)

    def get_environment_group(self, environment_group_name: str = None) -> EnvironmentGroup:
        env_group = self.config.environments.get(environment_group_name, None)
        if env_group is None:
            env_group = self.get_active_environment()
        if env_group is None:
            self.io.print_error(f'Error: Environment name not provided and there is no "active_environment" group set in config. ' +
                                    'Check command --help for ways to provide"-e/--environment" or environment argument. ' + 
                                    'Alternatively, add "active_environment" to lmctl config with the name of the environment (from the same config) you would like to use as the default')
            exit(1)
        return env_group

    def get_active_environment(self) -> EnvironmentGroup:
        if self.config.active_environment is not None:
            env_group = self.config.environments.get(self.config.active_environment, None)
            if env_group is None:
                self.io.print_error(f'Error: "active_environment" group set to "{self.config.active_environment}" but there is no environment with that name found in config')
                exit(1)
            else:
                return env_group
        return None
 
    def get_tnco_client(self, environment_group_name: str = None, input_pwd: str = None, input_client_secret: str = None, input_token: str = None) -> 'TNCOClient':
        env_group = self.get_environment_group(environment_group_name)
        if not env_group.has_tnco:
            self.io.print_error(f'Error: TNCO (ALM) environment not configured on group: {environment_group_name}')
            exit(1)
        tnco = env_group.tnco
        if tnco.secure:
            if tnco.is_using_zen_auth:
                if tnco.username is not None:
                    if input_pwd is not None and len(input_pwd.strip()) > 0:
                        tnco.api_key = input_pwd
                    elif tnco.api_key is None:
                        prompt_pwd = self.io.prompt(f'Please enter API key for TNCO (ALM) user {tnco.username}', hide_input=True, default='')
                        tnco.api_key = prompt_pwd
            elif tnco.is_using_token_auth:
                if input_token is not None and len(input_token.strip()) > 0:
                    tnco.token = input_token
                elif tnco.token is None:
                    prompt_token = self.io.prompt(f'Please enter token for TNCO (ALM)', hide_input=True, default='')
                    tnco.token = prompt_token
            else:
                if tnco.client_id is not None:
                    if tnco.client_secret is None:
                        if input_client_secret is not None and len(input_client_secret.strip()) > 0:
                            tnco.client_secret = input_client_secret
                        elif tnco.client_secret is None:
                            prompt_secret = self.io.prompt(f'Please enter secret for TNCO (ALM) client {tnco.client_id}', hide_input=True, default='')
                            tnco.client_secret = prompt_secret
                if tnco.username is not None:
                    if input_pwd is not None and len(input_pwd.strip()) > 0:
                        tnco.password = input_pwd
                    elif tnco.password is None:
                        prompt_pwd = self.io.prompt(f'Please enter password for TNCO (ALM) user {tnco.username}', hide_input=True, default='')
                        tnco.password = prompt_pwd
        return tnco.build_client()

    def create_arm_session(self, arm_name: str, environment_group_name: str = None):
        env_group = self.get_environment_group(environment_group_name)
        arm_env = env_group.arms.get(arm_name, None)
        if arm_env is None:
            self.io.print_error(f'No ARM named \'{arm_name}\' on group: {environment_group_name}')
            exit(1)
        arm_session_config = arm_env.create_session_config()
        return arm_session_config.create()

global_controller = None

def get_global_controller(override_config_path: str = None) -> CLIController:
    global global_controller
    if global_controller is None:
        try:
            global_controller = CLIController(get_global_config(override_config_path=override_config_path))
        except ConfigError as e:
            IOController().print_error(f'Error: Failed to load configuration - {e}')
            logger.exception(str(e))
            exit(1)
    return global_controller
