import dataclasses
import inspect
import functools

NOT_SET = 'NOT_SET'
ON_INIT = 'ON_INIT'
ON_SET = 'ON_SET'

@dataclasses.dataclass
class AttrRecord:
    name: str
    set_on: str = NOT_SET

    @property
    def is_set(self):
        return self.set_on != NOT_SET

def recordattrs(c = None):
    def decorator(c):
        if not dataclasses.is_dataclass(c):
            raise ValueError('Must use "recordattrs" on a dataclass')

        _wrap_init(c)
        _wrap_set(c)

        return c
    if c is not None:
        return decorator(c)
    return decorator

def _wrap_init(c):
    # Setup __init__
    existing_init = c.__init__
    def new_init(self, *args, **kwargs):
        init_arg_spec = inspect.getfullargspec(existing_init)
        expected_args = init_arg_spec.args

        # Remove self
        del expected_args[0]

        # Check which args have been provided
        attr_record = {f.name: AttrRecord(f.name) for f in dataclasses.fields(c)}
        i = 0
        while i < len(args) and i < len(expected_args):
            arg_name = expected_args[i]
            arg_value = args[i]
            if arg_name in attr_record:
                attr_record[arg_name].set_on = ON_INIT
            i+=1
        
        for k,v in kwargs.items():
            if k in attr_record:
                attr_record[k].set_on = ON_INIT


        existing_init(self, *args, **kwargs)

        # Set attr record after init
        # This prevents calls to setattr in __init__ from marking an attribute as set_on=ON_SET
        # Also, the __init__ of Pydantic dataclasses may result in the __attr_record__ being removed if we set this earlier.
        setattr(self, '__attr_record__', attr_record)


    # Wrapping
    functools.update_wrapper(new_init, existing_init)
    new_init.__signature__ = inspect.signature(existing_init)
    c.__init__ = new_init

def _wrap_set(cls):
    existing_set_attr = cls.__setattr__
    def new_set_attr(self, name, value):
        if hasattr(self, '__attr_record__') and name not in ['__attr_record__', '__record_on_set__']:
                attr_record = getattr(self, '__attr_record__')
                if name in attr_record:
                    attr_record[name].set_on = ON_SET
        existing_set_attr(self, name, value)
    
    # Wrapping
    functools.update_wrapper(new_set_attr, existing_set_attr)
    new_set_attr.__signature__ = inspect.signature(existing_set_attr)
    cls.__setattr__ = new_set_attr

def is_recording_attrs(inst):
    return hasattr(inst, '__attr_record__')

def attr_records(inst):
    if not is_recording_attrs(inst):
        raise TypeError('must be called with a dataclass decorated with @recordattrs')
    record = getattr(inst, '__attr_record__')
    fields = dataclasses.fields(inst)
    return tuple(record.get(f.name) for f in fields if f.name in record) 

def attr_records_dict(inst):
    return {a.name:a for a in attr_records(inst)}