import oyaml as yaml
import os

class DescriptorReader: 

    def __init__(self):
        pass

    @staticmethod
    def readDictionary(descriptor_path):
        raw_descriptor = DescriptorReader.readStr(descriptor_path)
        descriptor_content = DescriptorReader.strToDictionary(raw_descriptor)
        return descriptor_content

    @staticmethod
    def strToDictionary(raw_descriptor):
        return yaml.safe_load(raw_descriptor)

    @staticmethod
    def readStr(descriptor_path):
        if os.path.exists(descriptor_path):
          with open(descriptor_path, 'rt') as f:
            return f.read()
        else:
          raise DescriptorReaderException('Could not find descriptor at path: {0}'.format(descriptor_path))

class DescriptorModel:
    
    def __init__(self, raw_descriptor):
        self.raw_descriptor = raw_descriptor
    
    def getName(self):
        if 'name' not in self.raw_descriptor:
            raise DescriptorModelException('Descriptor has no name field')
        return self.raw_descriptor['name']

    def setName(self, type, name, version):
        self.raw_descriptor['name'] = '{0}::{1}::{2}'.format(type, name, version)

    def getVersion(self):
        name = self.getName()
        name_parts = name.split('::')
        num_of_parts = len(name_parts)
        if num_of_parts < 3:
            raise DescriptorModelException('Could not determine descriptor version as name contains only {0} parts separated by "::"'.format(num_of_parts))
        return name_parts[2]


class DescriptorReaderException(Exception):
    pass

class DescriptorModelException(Exception):
    pass
