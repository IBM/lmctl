import yaml
from .exceptions import ConfigError
from .rewriter import ConfigRewriter
from .config import Config
from .env_pre_parser import EnvironmentGroupPreParser
from pydantic import parse_obj_as, ValidationError

class ConfigParser:

    def __read_file(self, path):
        try:
            with open(path, 'rt') as f:
                config_dict = yaml.safe_load(f.read())
            return config_dict
        except Exception as e:
            raise ConfigError('Failed to load file {0}: {1}'.format(path, str(e))) from e

    def from_file(self, config_path):
        config_dict = self.__read_file(config_path)
        if config_dict is not None:
            if 'environments' not in config_dict and len(config_dict) > 0:
                # Old style config file
                self.__rewrite_config(config_path, config_dict)
                config_dict = self.__read_file(config_path)
        return self.from_dict(config_dict)

    def from_dict(self, config_dict):
        config_dict = self.__pre_parse(config_dict)
        try:
            config = parse_obj_as(Config, config_dict)
        except (TypeError, ValidationError) as e:
            raise ConfigError('Config error: {0}'.format(str(e))) from e
        return config

    def __pre_parse(self, config_dict):
        environments = config_dict.get('environments', {})
        environments = EnvironmentGroupPreParser().parse(environments)
        config_dict['environments'] = environments
        return config_dict

    def __rewrite_config(self, config_path, config_dict):
        try:
            ConfigRewriter(config_path, config_dict).rewrite()
        except Exception as e:
            raise ConfigError('The configuration file provided ({0}) appears to be a 2.0.X file. \
            Lmctl attempted to rewrite the file with updated syntax for 2.1.X but failed with the following error: {1}'.format(config_path, str(e))) from e
          