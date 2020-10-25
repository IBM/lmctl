import logging
import os
from pathlib import Path
from .exceptions import ConfigError

logger = logging.getLogger(__name__)

class ConfigFinder:

    def __init__(self, potential_env_var=None):
        self.potential_env_var = potential_env_var

    def _get_default_config_path(self):
        return str(Path.home().joinpath('.lmctl').joinpath('config.yaml'))

    def find(self):
        # Env variable
        env_var_value = None
        if self.potential_env_var:
            logger.debug('Checking {0} environment variable for config path'.format(self.potential_env_var))
            env_var_value = os.environ.get(self.potential_env_var)
            logger.debug('{0} has value: {1}'.format(self.potential_env_var, env_var_value))
            if env_var_value:
                if not os.path.exists(env_var_value):
                    raise ConfigError('Config path on environment variable {0} does not exist: {1}'.format(self.potential_env_var, env_var_value))
                return env_var_value
        # Default path
        default_path = self._get_default_config_path()
        logger.debug('Checking default location for config file: {0}'.format(default_path))
        if os.path.exists(default_path):
            return default_path
        # Raise error
        error_msg = 'Config file could not be found at default location "{0}"'.format(default_path)
        if self.potential_env_var:
            error_msg += ' or from environment variable {0}'.format(self.potential_env_var)
        raise ConfigError(error_msg)

# Backwards compatibility
CtlConfigFinder = ConfigFinder