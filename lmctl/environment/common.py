import abc
from typing import Union

class Environment(abc.ABC):

    @abc.abstractproperty
    def address(self):
        pass
    
    @abc.abstractmethod
    def create_session_config(self):
        pass

class EnvironmentRuntimeError(Exception):
    pass

class EnvironmentConfigError(Exception):
    pass

def value_or_default(value, default=None, allow_empty=False):
    if value is None:
        return default
    if type(value) is str:
        if not allow_empty:
            if len(value.strip()) == 0:
                return default
    return value

def get_value_or_default(config_dict, key, default=None, **kwargs):
    if key not in config_dict:
        return default
    value = config_dict[key]
    return value_or_default(value, default, **kwargs)

def build_address(host: str, 
                  protocol: str = 'https',
                  port: Union[str, int] = None, 
                  path: str = None):
    port = str(port).strip() if port is not None else None
    protocol = protocol.strip().lower() if protocol is not None else None
    if protocol is None or len(protocol) == 0:
        protocol = 'https'
    path = path.strip() if path is not None else None
    address = protocol
    if not address.endswith('://'):
        address += '://'
    address += host
    if port is not None and len(port) > 0:
        address += f':{port}'
    if path is not None and len(path) > 0:
        if not address.endswith('/'):
            address += '/'
        address += path
    if address.endswith('/'):
        address[:-1]
    return address