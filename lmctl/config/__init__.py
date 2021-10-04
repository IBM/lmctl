import logging
from .config import Config
from .exceptions import ConfigError, ConfigParserError
from .finder import ConfigFinder, CtlConfigFinder
from .parser import ConfigParser
from .rewriter import ConfigRewriter
from .ctl import Ctl
from .constants import CONFIG_ENV_VAR
from .io import ConfigIO
from typing import Tuple
import warnings
import os

logger = logging.getLogger(__name__)

CONFIG_ENV_VAR = 'LMCONFIG'

global_config = None
global_config_path = None


def find_config_location(ignore_not_found: bool = False) -> str:
    return ConfigFinder().find(ignore_not_found=ignore_not_found)

def get_config(override_config_path: str = None) -> Config:
    logger.debug('Loading LMCTL config')
    config, _ = get_config_with_path(override_config_path=override_config_path)
    return config

def get_config_with_path(override_config_path: str = None) -> Tuple[Config, str]:
    logger.debug('Loading LMCTL config')
    config, config_file_path = ConfigIO().read_discovered_file(override_path=override_config_path)
    return config, config_file_path

def get_global_config(override_config_path: str = None) -> Config:
    global_config, global_config_path = get_global_config_with_path(override_config_path)
    return global_config

def get_global_config_with_path(override_config_path: str = None) -> Config:
    global global_config
    global global_config_path
    if override_config_path is not None and global_config_path is not None and override_config_path != global_config_path:
        raise ConfigError(f'Attempting to re-load global config using a different path: original={global_config_path}, new={override_config_path}')
    if global_config is None:
        global_config, global_config_path = get_config_with_path(override_config_path=override_config_path)
    return global_config, global_config_path

def write_config(config: Config, override_config_path: str = None) -> str:
    return ConfigIO().write_discovered_file(config, override_path=override_config_path, backup_existing=True)

### Deprecated
global_ctl = None

def get_ctl(config_path: str = None) -> Ctl:
    warnings.warn('get_ctl is deprecated, use get_config instead', DeprecationWarning)
    logger.debug('Getting Ctl object')
    global global_ctl
    if global_ctl is None:
        config = get_config(override_config_path=config_path)
        global_ctl = Ctl(config)
    return global_ctl
