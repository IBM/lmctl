import logging
from .config import Config
from .env_parser import EnvironmentGroupParserWorker, EnvironmentGroupsParser
from .exceptions import ConfigError, ConfigParserError
from .finder import ConfigFinder, CtlConfigFinder
from .parser import ConfigParser, ConfigParserWorker
from .rewriter import ConfigRewriter
from .ctl import Ctl

logger = logging.getLogger(__name__)

global_ctl = None

def get_ctl(config_path=None):
    logger.debug('Getting Ctl object')
    global global_ctl
    if global_ctl == None:
        config_path = ConfigFinder(config_path, 'LMCONFIG').find()
        global_ctl = Ctl(ConfigParser().from_file(config_path))
    return global_ctl