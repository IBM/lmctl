import dataclasses
import copy
from .dc_capture import attr_records_dict, is_recording_attrs
from urllib.parse import urlsplit, urlparse, urlunparse

def asdict(obj, dict_factory=dict):
    # Check we have a dataclass instance
    if not dataclasses.is_dataclass(type(obj)):
        raise TypeError('asdict() should be called on dataclass instances')
    return _asdict_loop(obj, dict_factory)

def _asdict_loop(obj, dict_factory):
    if dataclasses.is_dataclass(type(obj)):
        # Dataclass instance
        converted = []
        obj_attr_records = None
        if is_recording_attrs(obj):
            obj_attr_records = attr_records_dict(obj)
        for f in dataclasses.fields(obj):
            value = getattr(obj, f.name)
            if (obj_attr_records is None or (f.name in obj_attr_records and obj_attr_records.get(f.name).is_set)) and not is_default_or_empty(f, value, obj):
                if f.name != 'kami_address' or not is_same_address_with_default_port(getattr(obj, 'address'), value, obj):
                    value = _asdict_loop(value, dict_factory)
                    converted.append((f.name, value))
        return dict_factory(converted)
    elif isinstance(obj, tuple) and hasattr(obj, '_fields'):
        # Named tuples
        return type(obj)(*[_asdict_loop(v, dict_factory) for v in obj])
    elif isinstance(obj, (list, tuple)):
        # List/Tuple
        return type(obj)(_asdict_loop(v, dict_factory) for v in obj)
    elif isinstance(obj, dict):
        return type(obj)( (_asdict_loop(k, dict_factory), _asdict_loop(v, dict_factory)) for k, v in obj.items() )
    elif hasattr(obj, '__as_dict__'):
        return obj.__as_dict__()
    else:
        return copy.deepcopy(obj)

def is_default_or_empty(field, value, obj):
    """
    Check if the value is the default, empty
    """
    if isinstance(field, dataclasses.Field) and not value:
        return True
    if value is None:
        return True
    if value == field.default:
        return True
    return False

def is_same_address_with_default_port(address, kami_address, obj):
    """
    Checks if the `kami_address` is the same as the `address` with the default port.
    """
    parsed_address = urlparse(address)
    parsed_kami_address = urlparse(kami_address)

    if parsed_address.hostname != parsed_kami_address.hostname:
        return False

    default_port = getattr(obj, 'kami_port', None)
    if default_port is not None:
        try:
            default_port = int(default_port)
        except (ValueError, TypeError):
            default_port = None

    if default_port is None:
        return not parsed_kami_address.port
    else:
        return parsed_kami_address.port == default_port