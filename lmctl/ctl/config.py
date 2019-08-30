import logging
import os
import yaml
import shutil 
from .common import ConfigError
from .environments import EnvironmentGroupsParser
from lmctl.environment.group import EnvironmentGroup

logger = logging.getLogger(__name__)

class ConfigParserError(ConfigError):
    pass

class ConfigRewriter:

    def __init__(self, path, config):
        self.path = path
        self.config = config

    def rewrite(self):
        new_config = {}
        if type(self.config) is not dict:
            raise ConfigError('Configuration should be a dictionary')
        environments = self.config
        if type(environments) is dict:
            for env_group_name, env_group_config in environments.items():
                environments[env_group_name] = self.__reconfigure_environment_group(env_group_config)
        new_config['environments'] = environments
        if os.path.exists(self.path):
            backup_file_name = '{0}.bak'.format(os.path.basename(self.path))
            backup_path = os.path.join(os.path.dirname(self.path), backup_file_name)
            shutil.copyfile(self.path, backup_path)
            os.remove(self.path)
        with open(self.path, 'w') as writer:
            writer.write('## Lmctl has updated this file with the latest schema changes. A backup of your existing config file has been placed in the same directory with a .bak extension\n')
            yaml.safe_dump(new_config, writer, default_flow_style=False, sort_keys=False)
        return new_config

    def __reconfigure_environment_group(self, env_group_config):
        if 'alm' in env_group_config:
            env_group_config['alm'] = self.__reconfigure_lm(env_group_config['alm'])
        if 'arm' in env_group_config:
            arms = env_group_config['arm']
            if type(arms) is dict:
                for arm_name, arm_config in arms.items():
                    arms[arm_name] = self.__reconfigure_arm(arm_config)
                env_group_config['arm'] = arms
        return env_group_config

    def __reconfigure_lm(self, lm_config):
        if lm_config is None:
            return lm_config
        new_lm_config = {}
        for key, value in lm_config.items():
            if key == 'ip_address':
                key = 'host'
            elif key == 'auth_address':
                key = 'auth_host'
            elif key == 'secure_port':
                key = 'protocol'
                value = 'https'
                if lm_config['secure_port'] is False:
                    value = 'http'
            new_lm_config[key] = value
        if 'secure' not in new_lm_config:
            if 'username' not in new_lm_config:
                new_lm_config['secure'] = False
            else:
                new_lm_config['secure'] = True
        return new_lm_config

    def __reconfigure_arm(self, arm_config):
        if arm_config is None:
            return arm_config
        new_arm_config = {}
        for key,value in arm_config.items():
            if key == 'ip_address':
                key = 'host'
            elif key == 'secure_port':
                key = 'protocol'
                value = 'https'
                if arm_config['secure_port'] is False:
                    value = 'http'
            if key != 'onboarding_addr':
                new_arm_config[key] = value
        return new_arm_config

class ConfigParser:

    def __init__(self):
        pass

    def __read_file(self, path):
        try:
            with open(path, 'rt') as f:
                config_dict = yaml.safe_load(f.read())
            return config_dict
        except Exception as e:
            raise ConfigParserWorker('Failed to load file {0}: {1}'.format(path, str(e))) from e

    def from_file(self, config_path):
        config_dict = self.__read_file(config_path)
        if config_dict is not None:
            if 'environments' not in config_dict and len(config_dict) > 0:
                # Old style config file
                self.__rewrite_config(config_path, config_dict)
                config_dict = self.__read_file(config_path)
        return ConfigParserWorker(config_dict).parse()
    
    def __rewrite_config(self, config_path, config_dict):
        try:
            ConfigRewriter(config_path, config_dict).rewrite()
        except Exception as e:
            raise ConfigParserError('The configuration file provided ({0}) appears to be a 2.0.X file. \
            Lmctl attempted to rewrite the file with updated syntax for 2.1.X but failed with the following error: {1}'.format(config_path, str(e))) from e
          

class ConfigParserWorker:

    def __init__(self, config_dict):
        self.config_dict = config_dict

    def parse(self):
        env_groups = {}
        environments = self.config_dict.get('environments', {})
        environments = EnvironmentGroupsParser.from_dict(environments)
        return Config(environments)
        

class Config:

    def __init__(self, environments=None):
        if environments is None:
            environments = {}
        self.environments = environments

class CtlConfigFinder:

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
            
class Ctl:
    
    def __init__(self, config):
        self.config = config
        self.environments = self.config.environments

    def environment_group_named(self, env_name):
        if env_name not in self.environments:
            raise ConfigError('No environment group with name: {0}'.format(env_name))
        return self.environments[env_name]



global_ctl = None

def get_ctl(config_path=None):
    logger.debug('Getting Ctl object')
    global global_ctl
    if global_ctl == None:
        config_path = CtlConfigFinder(config_path, 'LMCONFIG').find()
        global_ctl = Ctl(ConfigParser().from_file(config_path))
    return global_ctl
