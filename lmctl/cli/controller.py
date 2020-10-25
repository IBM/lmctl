import click
import logging
from lmctl.cli.io import IOController
from lmctl.config import get_global_config, Config, ConfigError
from lmctl.environment import EnvironmentGroup, EnvironmentRuntimeError
from .safety_net import safety_net, lm_client_safety_net

logger = logging.getLogger(__name__)

class CLIController:
    
    def __init__(self, config: Config):
        self.config = config
        self.io = IOController.get()

    def safety_net(self, *catchable_exceptions):
        return safety_net(*catchable_exceptions, io_controller=self.io)

    def lm_client_safety_net(self):
        return lm_client_safety_net(io_controller=self.io)

    def get_environment_group_named(self, environment_group_name: str) -> EnvironmentGroup:
        env_group = self.config.environments.get(environment_group_name, None)
        if env_group is None:
            self.io.print_error(f'No environment group with name: {environment_group_name}')
            exit(1)
        return env_group

    def get_lm_client(self, environment_group_name: str, input_pwd: str = None, input_client_secret: str = None) -> 'LmClient':
        env_group = self.get_environment_group_named(environment_group_name)
        if not env_group.has_lm:
            self.io.print_error(f'Error: LM environment not configured on group: {environment_group_name}')
            exit(1)
        lm = env_group.lm
        if lm.is_secure:
            if lm.username is not None:
                if input_pwd is not None and len(input_pwd.strip()) > 0:
                    lm.password = input_pwd
                elif lm.password is None:
                    prompt_pwd = self.io.prompt(f'Please enter password for LM user {lm.username}', hide_input=True, default='')
                    lm.password = prompt_pwd
            if lm.client_id is not None:
                if lm.client_secret is None:
                    if input_client_secret is not None and len(input_client_secret.strip()) > 0:
                        lm.client_secret = input_client_secret
                    elif lm.client_secret is None:
                        prompt_secret = self.io.prompt(f'Please enter secret for LM client {lm.client_id}', hide_input=True, default='')
                        lm.client_secret = prompt_secret
        return lm.build_client()

    def create_arm_session(self, environment_group_name: str, arm_name: str):
        env_group = self.get_environment_group_named(environment_group_name)
        with self.safety_net(EnvironmentRuntimeError):
            arm_env = env_group.arm_named(arm_name)
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
