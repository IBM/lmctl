import logging
import os
from pathlib import Path
from .exceptions import ConfigError
from .constants import CONFIG_ENV_VAR

logger = logging.getLogger(__name__)

class ConfigFinder:

    def __init__(self, potential_env_var=CONFIG_ENV_VAR):
        self.potential_env_var = potential_env_var

    def get_default_config_path(self):
        return str(Path.home().joinpath('.lmctl').joinpath('config.yaml'))

    def find(self, ignore_not_found: bool = False):
        # Env variable
        env_var_value = None
        if self.potential_env_var:
            logger.debug(f'Checking {self.potential_env_var} environment variable for config path')
            env_var_value = os.environ.get(self.potential_env_var)
            logger.debug(f'{self.potential_env_var} has value: {env_var_value}')
            if env_var_value:
                if not os.path.exists(env_var_value) and not ignore_not_found:
                    raise ConfigError(f'Config path on environment variable {self.potential_env_var} does not exist: {env_var_value}')
                return env_var_value
        # Default path
        default_path = self.get_default_config_path()
        logger.debug(f'Checking default location for config file: {default_path}')
        if ignore_not_found or os.path.exists(default_path):
            return default_path
        # Raise error
        error_msg = f'Config file could not be found at default location "{default_path}"'
        if self.potential_env_var:
            error_msg += f' or from environment variable {self.potential_env_var}'
        raise ConfigError(error_msg)

# Backwards compatibility
CtlConfigFinder = ConfigFinder