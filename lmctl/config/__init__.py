import logging
from .config import Config
from .env_parser import EnvironmentGroupParserWorker, EnvironmentGroupsParser
from .exceptions import ConfigError, ConfigParserError
from .finder import ConfigFinder, CtlConfigFinder
from .parser import ConfigParser, ConfigParserWorker
from .rewriter import ConfigRewriter
from .ctl import Ctl
import warnings
from typing import Tuple
import os

logger = logging.getLogger(__name__)

CONFIG_ENV_VAR = 'LMCONFIG'

global_config = None
global_config_path = None

def get_config(override_config_path: str = None) -> Tuple[Config, str]:
    logger.debug('Loading LMCTL config')
    if override_config_path is not None:
        if not os.path.exists(override_config_path):
            raise ConfigError(f'Provided config path does not exist: {override_config_path}')
        config_path = override_config_path
    else:
        config_path = ConfigFinder(potential_env_var=CONFIG_ENV_VAR).find()
    return ConfigParser().from_file(config_path), config_path

def get_global_config(override_config_path: str = None) -> Config:
    global global_config
    global global_config_path
    if override_config_path is not None and global_config_path is not None:
        raise ConfigError(f'Attempting to re-load global config using a different path: original={global_config_path}, new={override_config_path}')
    if global_config is None:
        global_config, global_config_path = get_config(override_config_path=override_config_path)
    return global_config

### Deprecated
global_ctl = None

def get_ctl(config_path: str= None) -> Ctl:
    warnings.warn('get_ctl is deprecated, use get_config instead', DeprecationWarning)
    logger.debug('Getting Ctl object')
    global global_ctl
    if global_ctl is None:
        if config_path is not None:
            if not os.path.exists(config_path):
                raise ConfigError(f'Provided config path does not exist: {config_path}')
        else:
            config_path = ConfigFinder(CONFIG_ENV_VAR).find()
        global_ctl = Ctl(ConfigParser().from_file(config_path))
    return global_ctl