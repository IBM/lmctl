import logging
from .exceptions import ConfigError
from .finder import ConfigFinder
from .parser import ConfigParser

logger = logging.getLogger(__name__)
   
class Ctl:
    
    def __init__(self, config):
        self.config = config
        self.environments = self.config.environments

    def environment_group_named(self, env_name):
        if env_name not in self.environments:
            raise ConfigError('No environment group with name: {0}'.format(env_name))
        return self.environments[env_name]
