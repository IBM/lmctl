import logging
import os
import yaml
import lmctllib.environment.model as env_model

logger = logging.getLogger(__name__)

class Config:
    """
    Handles loading an LMCONFIG file, either from a path or environment variable
    """
    def __init__(self, path):
        self.path = path
        self.environments = {}
        if not self.path:
            logger.debug('No path to config file provided, checking LMCONFIG environment variable')
            self.path=os.environ.get('LMCONFIG')
            logger.debug('LMCONFIG set to: {0}'.format(self.path))

        logger.debug('Loading config from file: '+str(self.path))
        if not self.path:
            logger.error('No config file location provided')
            exit(1)

        if os.path.isfile(self.path):
            self.__loadConfig()
        else:
            logger.error('Config file does not exist at: {0}'.format(self.path))
            exit(1)

    def __loadConfig(self):
        if os.path.exists(self.path):
            with open(self.path, 'rt') as f:
                self.config = yaml.safe_load(f.read())
                logger.debug(self.config)
        else:
            logger.error('Config file does not exist at: {0}'.format(self.path))
            exit(1)
        
        for env_name in self.config:
            parser = env_model.EnvironmentParser(env_name, self.config[env_name])
            env = parser.parse()
            self.environments[env_name] = env

    def getEnv(self, env_name):
        """Retrieves a named environment from the current configuration"""
        if env_name not in self.environments:
            raise ValueError('No environment with name {0}'.format(env_name))
        return self.environments[env_name]

    def getConfiguredEnv(self, env_name, prompt_func):
        """Retrieves a named environment from the current configuration, ensuring it is fully configured for use (requests for any additional input needed)"""
        env = self.getEnv(env_name)
        if env.lm.requiresAuthentication():
            if env.lm.password is None: 
                if prompt_func:
                    value = prompt_func('password for LM user {0}'.format(env.lm.username), True)
                    env.lm.password = value
                else:
                    raise ValueError('No password set for LM user {0}')
        return env

global_config = None

def getConfig(config_path=None):
    logger.debug('Getting Config object')
    global global_config
    if global_config == None:
        global_config = Config(config_path)
    return global_config
