from ruamel.yaml import YAML
import os

ASSEMBLY_DESCRIPTOR_TYPE = 'assembly'
RESOURCE_DESCRIPTOR_TYPE = 'resource'

yaml = YAML()
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
        except yaml.YAMLError as e:
            raise DescriptorParsingError(str(e)) from e
        return yml_dict

    def __read_yml_str_from_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'rt') as f:
                return f.read()
        else:
            raise DescriptorReaderException('Could not find descriptor at path: {0}'.format(file_path))

    def write_to_file(self, descriptor, descriptor_path):
        with open(descriptor_path, 'w') as descriptor_file:
            yaml.dump(descriptor.raw, descriptor_file)


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

    def __init__(self, raw_descriptor):
        self.raw = raw_descriptor

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


class DescriptorReaderException(Exception):
    pass


class DescriptorModelException(Exception):
    pass
