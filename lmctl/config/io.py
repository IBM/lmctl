from .config import Config
from .finder import ConfigFinder
from .exceptions import ConfigError
from .env_pre_parser import EnvironmentGroupPreParser
from typing import Dict, Tuple
from lmctl.utils.dcutils.dc_to_dict import asdict
from pydantic import parse_obj_as, ValidationError
import yaml
import os
import shutil

class ConfigIO:

    def __init__(self):
        self.finder = ConfigFinder()

    def read_discovered_file(self, override_path: str = None) -> Tuple[Config, str]:
        if override_path is None:
            file_path = self.finder.find()
            return self.file_to_config(file_path), file_path
        else:
            return self.file_to_config(override_path), override_path

    def write_discovered_file(self, config: Config, override_path: str = None, backup_existing: bool = False) -> str:
        if override_path is None:
            return self.config_to_file(config, self.finder.find(), backup_existing=backup_existing)
        else:
            return self.config_to_file(config, override_path, backup_existing=backup_existing)

    def file_to_config(self, path: str) -> Config:
        config_dict = self.file_to_dict(path)
        return self.dict_to_config(config_dict)

    def file_to_dict(self, path: str) -> Dict:
        config_dict = self.__read_yaml_file(path)
        self.__pre_parse_envs(config_dict)
        return config_dict

    def config_to_file(self, config: Config, path: str, backup_existing: bool = False) -> str: 
        config_dict = self.config_to_dict(config)
        self.dict_config_to_file(config_dict, path, backup_existing=backup_existing)
        return path

    def config_to_dict(self, config: Config) -> Dict:
        as_dict = asdict(config)
        self.__strip_names(as_dict)
        return as_dict

    def dict_config_to_file(self, config_dict: Dict, path: str, backup_existing: bool = False) -> str:
        if os.path.exists(path) and backup_existing is True:
            backup_path = path + '.bak'
            shutil.copyfile(path, backup_path)
        with open(path, 'w') as f:
            f.write(yaml.safe_dump(config_dict))
        return path

    def dict_to_config(self, config_dict: Dict) -> Config:
        self.__pre_parse_envs(config_dict)
        try:
            config = parse_obj_as(Config, config_dict)
        except (TypeError, ValidationError) as e:
            raise ConfigError(f'Config error: {str(e)}') from e
        return config

    def __pre_parse_envs(self, config_dict: Dict):
        environments = config_dict.get('environments', {})
        environments = EnvironmentGroupPreParser().parse(environments)
        config_dict['environments'] = environments

    def __strip_names(self, config_dict: Dict):
        for env in config_dict.get('environments', {}).values():
            if 'name' in env:
                del env['name']

    def __read_yaml_file(self, path):
        if not os.path.exists(path):
            raise ConfigError(f'Config path does not exist: {path}')
        try:
            with open(path, 'rt') as f:
                config_dict = yaml.safe_load(f.read())
            return config_dict
        except (yaml.YAMLError, OSError) as e:
            raise ConfigError(f'Failed to load file {path}: {str(e)}') from e
