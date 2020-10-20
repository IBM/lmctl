import logging
import os
from .exceptions import ConfigError

logger = logging.getLogger(__name__)

class ConfigFinder:

    def __init__(self, potential_path=None, potential_env_var=None):
        self.potential_path = potential_path
        self.potential_env_var = potential_env_var
        if not self.potential_path and not self.potential_env_var:
            raise ConfigError('Must specify at least one of potential_path and/or potential_env_var')

    def find(self):
        if self.potential_path:
            if not os.path.exists(self.potential_path):
                raise ConfigError('Path provided to load control config does not exist: {0}'.format(self.potential_path))
            return self.potential_path
        else:
            logger.debug('Config file path not provided, checking {0} environment variable'.format(self.potential_env_var))
            env_var_value = os.environ.get(self.potential_env_var)
            logger.debug('{0} has value: {1}'.format(self.potential_env_var, env_var_value))
            if not env_var_value:
                raise ConfigError('Config environment variable {0} is not set'.format(self.potential_env_var))
            if not os.path.exists(env_var_value):
                raise ConfigError('Config environment variable {0} path does not exist: {1}'.format(self.potential_env_var, env_var_value))
            return env_var_value

# Backwards compatibility
CtlConfigFinder = ConfigFinder