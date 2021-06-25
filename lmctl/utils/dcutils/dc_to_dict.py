import dataclasses
import copy
from .dc_capture import attr_records_dict, is_recording_attrs

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
            if obj_attr_records is None or (f.name in obj_attr_records and obj_attr_records.get(f.name).is_set):
                value = _asdict_loop(getattr(obj, f.name), dict_factory)
                converted.append( (f.name, value) )
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