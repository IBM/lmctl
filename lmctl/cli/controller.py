import click
import logging
from lmctl.cli.io import IOController
from lmctl.config import get_config_with_path, Config, ConfigError
from lmctl.environment import EnvironmentGroup
from .safety_net import safety_net, tnco_client_safety_net

logger = logging.getLogger(__name__)

class CLIController:
    
    def __init__(self, config: Config, config_path: str):
        self.config = config
        self.config_path = config_path
        self.io = IOController.get()

    def safety_net(self, *catchable_exceptions):
        return safety_net(*catchable_exceptions, io_controller=self.io)

    def tnco_client_safety_net(self, *extra_exceptions):
        return tnco_client_safety_net(*extra_exceptions, io_controller=self.io)

    def get_environment_group(self, environment_group_name: str = None) -> EnvironmentGroup:
        env_group = self.config.environments.get(environment_group_name, None)
        if env_group is None:
            if environment_group_name is not None:
                self.io.print_error(f'Error: No environment named: {environment_group_name}')
                exit(1)
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
    
    def get_tnco_env(self, environment_group_name: str = None, input_pwd: str = None, input_client_secret: str = None, input_token: str = None) -> 'TNCOEnvironment':
        env_group = self.get_environment_group(environment_group_name)
        if not env_group.has_tnco:
            self.io.print_error(f'Error: CP4NA orchestration environment not configured on group: {environment_group_name}')
            exit(1)
        tnco = env_group.tnco
        if tnco.is_using_cp_api_key_auth():
            self._configure_api_key_or_prompt(tnco, input_pwd)
    
        elif tnco.is_using_token_auth():
            self._configure_token_or_prompt(tnco, input_token)
    
        elif tnco.is_using_okta_client_auth():
                self._configure_client_or_prompt(tnco, input_client_secret)
        
        elif tnco.is_using_okta_user_auth():
                self._configure_client_or_prompt(tnco, input_client_secret)
                self._confgure_user_or_prompt(tnco, input_pwd)
        
        elif tnco.is_using_oauth_client_auth():
            self._configure_client_or_prompt(tnco, input_client_secret)
        
        elif tnco.is_using_oauth_user_auth():
            self._configure_client_or_prompt(tnco, input_client_secret)
            self._confgure_user_or_prompt(tnco, input_pwd)

        elif tnco.is_using_oauth_legacy_user_auth():
            self._confgure_user_or_prompt(tnco, input_pwd)

        return tnco
 
    def get_tnco_client(self, environment_group_name: str = None, input_pwd: str = None, input_client_secret: str = None, input_token: str = None) -> 'TNCOClient':
        tnco = self.get_tnco_env(environment_group_name, input_pwd, input_client_secret, input_token)
        return tnco.build_client()
    
    def _configure_token_or_prompt(self, tnco, input_token: str):
        if input_token is not None and len(input_token.strip()) > 0:
            # If token provided then use it (override the existing token from the environment)
            tnco.token = input_token
        elif tnco.token is None:
            # If no token was provided and there is no value set in the environment then prompt for it
            prompt_token = self.io.prompt(f'Please enter access token for CP4NA orchestration', hide_input=True, default='')
            tnco.token = prompt_token
    
    def _configure_api_key_or_prompt(self, tnco, input_api_key: str):
        if input_api_key is not None and len(input_api_key.strip()) > 0:
            # If api_key provided then use it (override the existing api_key from the environment)
            tnco.api_key = input_api_key
        elif tnco.api_key is None or len(tnco.api_key.strip()) == 0:
            # If no api_key was provided and there is no value set in the environment then prompt for it
            prompt_key = self.io.prompt(f'Please enter API key for CP4NA orchestration user {tnco.username}', hide_input=True, default='')
            tnco.api_key = prompt_key

    def _configure_client_or_prompt(self, tnco, input_client_secret: str):
        if input_client_secret is not None and len(input_client_secret.strip()) > 0:
            # If client secret provided then use it (override the existing secret from the environment)
            tnco.client_secret = input_client_secret
        elif tnco.client_secret is None or len(tnco.client_secret.strip()) == 0:
            # If no client secret was provided and there is no value set in the environment then prompt for it
            prompt_secret = self.io.prompt(f'Please enter secret for CP4NA orchestration client {tnco.client_id}', hide_input=True, default='')
            tnco.client_secret = prompt_secret
    
    def _confgure_user_or_prompt(self, tnco, input_pwd: str):
        if input_pwd is not None and len(input_pwd.strip()) > 0:
            # If password provided then use it (override the existing password from the environment)
            tnco.password = input_pwd
        elif tnco.password is None or len(tnco.password.strip()) == 0:
            # If no password was provided and there is no value set in the environment then prompt for it
            prompt_pwd = self.io.prompt(f'Please enter password for CP4NA orchestration user {tnco.username}', hide_input=True, default='')
            tnco.password = prompt_pwd

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
            config, config_path = get_config_with_path(override_config_path=override_config_path)
            global_controller = CLIController(config, config_path)
        except ConfigError as e:
            IOController().print_error(f'Error: Failed to load configuration - {e}')
            logger.exception(str(e))
            exit(1)
    return global_controller

def clear_global_controller():
    global global_controller
    global_controller = None