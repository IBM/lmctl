import ruamel.yaml as ryaml
import os
from collections import OrderedDict

ASSEMBLY_DESCRIPTOR_TYPE = 'assembly'
RESOURCE_DESCRIPTOR_TYPE = 'resource'
ASSEMBLY_TEMPLATE_DESCRIPTOR_TYPE = 'assembly-template'
TYPE_DESCRIPTOR_TYPE = 'type'

yaml = ryaml.YAML()
yaml.default_flow_style = False

class DescriptorParsingError(Exception):
    pass


class DescriptorParser:

    def __init__(self):
        pass

    def read_from_file(self, descriptor_path):
        yml_str = self.__read_yml_str_from_file(descriptor_path)
        return self.read_from_str(yml_str)

    def read_from_file_with_raw(self, descriptor_path):
        yml_str = self.__read_yml_str_from_file(descriptor_path)
        return (self.read_from_str(yml_str), yml_str)

    def read_from_str(self, descriptor_yml_str):
        yml_dict = self.__convert_str_to_dict(descriptor_yml_str)
        if yml_dict is None:
            yml_dict = self.__convert_str_to_dict('description: ')
        return Descriptor(yml_dict)

    def __convert_str_to_dict(self, descriptor_yml_str):
        try:
            yml_dict = yaml.load(descriptor_yml_str)
        except ryaml.YAMLError as e:
            raise DescriptorParsingError(str(e)) from e
        return yml_dict

    def __read_yml_str_from_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'rt') as f:
                return f.read()
        else:
            raise DescriptorReaderException('Could not find descriptor at path: {0}'.format(file_path))

    def write_to_file(self, descriptor, descriptor_path):
        descriptor.sort()
        with open(descriptor_path, 'w') as descriptor_file:
            yaml.dump(descriptor.raw, descriptor_file)

    def write_to_str(self, descriptor):
        descriptor.sort()
        stringio = ryaml.compat.StringIO()
        yaml.dump(descriptor.raw, stringio)
        return stringio.getvalue()


def descriptor_named(descriptor_type, name, version):
    full_name = '{0}::{1}::{2}'.format(descriptor_type, name, version)
    return full_name


def assembly_descriptor_named(name, version):
    full_name = '{0}::{1}::{2}'.format(ASSEMBLY_DESCRIPTOR_TYPE, name, version)
    return full_name


class DescriptorName:

    def __init__(self, descriptor_type, name, version):
        self.descriptor_type = descriptor_type
        self.name = name
        self.version = version

    def name_str(self):
        return '{0}::{1}::{2}'.format(self.descriptor_type, self.name, self.version)

class Descriptor:
    
    ORDERED_KEYS = ['name', 'description', 'properties', 'private-properties', 'infrastructure', 'lifecycle', 'default-driver', 'composition', 'references', 'relationships', 'operations']
    ORDERED_LIFECYCLE = ['Create', 'Install', 'Configure', 'Reconfigure', 'Start', 'Stop', 'Uninstall', 'Delete']

    def __init__(self, raw_descriptor, is_2_dot_1=False):
        self.raw = raw_descriptor
        self.is_2_dot_1 = is_2_dot_1

    def get_name(self):
        if 'name' not in self.raw:
            raise DescriptorModelException('Descriptor has no name field')
        return self.raw['name']

    def set_name(self, descriptor_type, name, version):
        new_value = descriptor_named(descriptor_type, name, version)
        if 'name' in self.raw:
            self.raw['name'] = new_value
        else:
            self.raw.insert(0, 'name', new_value)

    def remove_name(self):
        if 'name' in self.raw:
            del self.raw['name']

    def has_name(self):
        return 'name' in self.raw

    def get_split_name(self):
        name = self.get_name()
        split_name = name.split('::')
        length = len(split_name)
        descriptor_type = None
        descriptor_name = None
        descriptor_version = None
        if length > 0:
            descriptor_type = split_name[0]
        if length > 1:
            descriptor_name = split_name[1]
        if length > 2:
            descriptor_version = split_name[2]
        return (descriptor_type, descriptor_name, descriptor_version)

    def get_version(self):
        name = self.get_name()
        name_parts = name.split('::')
        num_of_parts = len(name_parts)
        if num_of_parts < 3:
            raise DescriptorModelException('Could not determine descriptor version as name contains only {0} parts separated by "::"'.format(num_of_parts))
        return name_parts[2]

    @property
    def description(self):
        return self.raw.get('description', None)

    @description.setter
    def description(self, desc):
        self.raw['description'] = desc

    @property
    def properties(self):
        if 'properties' not in self.raw:
            self.raw['properties'] = {}
        return self.raw['properties']

    @property
    def lifecycle(self):
        if 'lifecycle' not in self.raw:
            self.raw['lifecycle'] = {}
        return self.raw['lifecycle']

    @lifecycle.setter
    def lifecycle(self, lifecycle):
        self.raw['lifecycle'] = lifecycle

    @property
    def infrastructure(self):
        if 'infrastructure' not in self.raw:
            self.raw['infrastructure'] = {}
        return self.raw['infrastructure']

    @property
    def default_driver(self):
        if 'default-driver' not in self.raw:
            self.raw['default-driver'] = {}
        return self.raw['default-driver']

    @property
    def queries(self):
        if 'queries' not in self.raw:
            self.raw['queries'] = {}
        return self.raw['queries']

    def insert_default_driver(self, driver_name, infrastructure_types=None):
        self.default_driver[driver_name] = {}
        if infrastructure_types is not None:
            if self.is_2_dot_1:
                self.default_driver[driver_name]['infrastructure-type'] = infrastructure_types
            else:
                self.default_driver[driver_name]['selector'] = {}
                self.default_driver[driver_name]['selector']['infrastructure-type'] = infrastructure_types

    def insert_infrastructure_discover(self, type_name, file_name, template_type=None):
        if type_name not in self.infrastructure:
            self.infrastructure[type_name] = {}
        if 'discover' not in self.infrastructure[type_name]:
            self.infrastructure[type_name]['discover'] = {}
        self.infrastructure[type_name]['discover']['file'] = file_name
        if template_type is not None:
            self.infrastructure[type_name]['discover']['template-type'] = template_type       

    def insert_infrastructure_template(self, type_name, file_name, template_type=None):
        if type_name not in self.infrastructure:
            self.infrastructure[type_name] = {}
        if 'template' not in self.infrastructure[type_name]:
            self.infrastructure[type_name]['template'] = {}
        self.infrastructure[type_name]['template']['file'] = file_name
        if template_type is not None:
            self.infrastructure[type_name]['template']['template-type'] = template_type       

    def _sort_lifecycle(self):
        old_lifecycle = self.lifecycle
        new_lifecycle = OrderedDict()
        for key in Descriptor.ORDERED_LIFECYCLE:
            if key in old_lifecycle:
                new_lifecycle[key] = old_lifecycle[key]
        for key in old_lifecycle.keys():
            if key not in Descriptor.ORDERED_LIFECYCLE:
                new_lifecycle[key] = old_lifecycle[key]
        self.raw['lifecycle'] = dict(new_lifecycle)

    def insert_lifecycle(self, lifecycle_name, properties=None, drivers=None):
        new_lifecycle_obj = {}
        if properties is not None:
            new_lifecycle_obj['properties'] = properties
        if drivers is not None:
            new_lifecycle_obj['drivers'] = drivers
        self.lifecycle[lifecycle_name] = new_lifecycle_obj
        self._sort_lifecycle()

    def add_property(self, name, description=None, ptype='string', required=None, default=None, read_only=None, value=None):
        properties = self.properties
        if name in properties:
            raise ValueError('Property {0} has already been defined'.format(name))
        properties[name] = {}
        if description is not None:
            properties[name]['description'] = description
        if ptype is not None:
            properties[name]['type'] = ptype
        if required is not None:
            properties[name]['required'] = required
        if default is not None:
            properties[name]['default'] = default
        if read_only is not None:
            properties[name]['read-only'] = read_only
        if value is not None:
            properties[name]['value'] = value

    def sort(self):
        new_raw = OrderedDict()
        for key in Descriptor.ORDERED_KEYS:
            if key in self.raw:
                new_raw[key] = self.raw[key]
        for key in self.raw.keys():
            if key not in Descriptor.ORDERED_KEYS:
                new_raw[key] = self.raw[key]
        self.raw = dict(new_raw)


class DescriptorReaderException(Exception):
    pass


class DescriptorModelException(Exception):
    pass
