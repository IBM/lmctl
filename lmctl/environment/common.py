import abc

class Environment(abc.ABC):

    @abc.abstractmethod
    def address(self):
        pass
    
    @abc.abstractmethod
    def create_session_config(self):
        pass

class EnvironmentRuntimeError(Exception):
    pass

class EnvironmentConfigError(Exception):
    pass

def value_or_default(value, default=None, **kwargs):
    if value is None:
        return default
    if type(value) is str:
        allow_empty = bool(kwargs.get('allow_empty', False))
        if not allow_empty:
            if len(value.strip()) == 0:
                return default
    return value

def get_value_or_default(config_dict, key, default=None, **kwargs):
    if key not in config_dict:
        return default
    value = config_dict[key]
    return value_or_default(value, default, **kwargs)