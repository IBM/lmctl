import yaml
from .exceptions import ConfigError, ConfigParserError
from .rewriter import ConfigRewriter
from .config import Config
from .env_parser import EnvironmentGroupsParser

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
        raw_environments = self.config_dict.get('environments', {})
        environments = EnvironmentGroupsParser.from_dict(raw_environments)
        return Config(environments, raw_environments=raw_environments)