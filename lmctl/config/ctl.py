import logging
import warnings
from .exceptions import ConfigError

logger = logging.getLogger(__name__)
   
class Ctl:
    
    def __init__(self, config):
        warnings.warn('Ctl is deprecated, use lmctl.config.Config instead', DeprecationWarning)
        self.config = config
        self.environments = self.config.environments

    def environment_group_named(self, env_name):
        warnings.warn('Ctl is deprecated, use lmctl.config.Config instead', DeprecationWarning)
        if env_name not in self.environments:
            raise ConfigError('No environment group with name: {0}'.format(env_name))
        return self.environments[env_name]
