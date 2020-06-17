from .base import Mutator
import lmctl.reference as refs
import lmctl.utils.descriptors as descriptor_utils

class DescriptorStageMutator(Mutator):

    def __init__(self, source_config, config_references, journal):
        self.source_config = source_config
        self.config_references = config_references
        self.journal = journal

    def apply(self, descriptor, is_template=False):
        if not descriptor.has_name():
            if is_template:
                descriptor_name = descriptor_utils.DescriptorName(descriptor_utils.ASSEMBLY_TEMPLATE_DESCRIPTOR_TYPE, \
                    self.source_config.full_name, self.source_config.version).name_str()
            else:
                descriptor_name = self.source_config.descriptor_name
            descriptor.raw.insert(0, 'name', descriptor_name)
        self.resolve_references(descriptor)
        return descriptor

    def resolve_references(self, descriptor):
        self.__resolve_types(descriptor.raw, 'composition')
        self.__resolve_types(descriptor.raw, 'references')
    
    def __resolve_types(self, raw_descriptor, elements_key):
        if elements_key in raw_descriptor:
            element_map = raw_descriptor[elements_key]
            if isinstance(element_map, dict):
                for key, element in element_map.items():
                    if 'type' in element:
                        element_type = element['type']
                        if self.config_references.is_reference(element_type):
                            try:
                                resolved_value = self.config_references.resolve(element_type)
                                if resolved_value is not None:
                                    element['type'] = resolved_value
                            except (refs.NotResolvableError, refs.BadReferenceError) as e:
                                self.journal.event('Cannot resolve reference: {0}'.format(element_type))

class DescriptorPullMutator(Mutator):

    def __init__(self, config_references, journal):
        self.config_references = config_references
        self.journal = journal

    def apply(self, descriptor):
        descriptor.remove_name()
        self.__convert_types(descriptor.raw, 'composition')
        self.__convert_types(descriptor.raw, 'references')
        return descriptor

    def __convert_types(self, raw_descriptor, elements_key):
        if elements_key in raw_descriptor:
            element_map = raw_descriptor[elements_key]
            if isinstance(element_map, dict):
                for key, element in element_map.items():
                    if 'type' in element:
                        element_type = element['type']
                        project_for_descriptor_reference = self.config_references.build_descriptor_to_project_mapping_reference(element_type)
                        try:
                            resolved_project = self.config_references.resolve(project_for_descriptor_reference)
                            if resolved_project is not None:
                                element['type'] = self.config_references.build_descriptor_reference(resolved_project)
                        except (refs.NotResolvableError, refs.BadReferenceError) as e:
                            self.journal.event('Cannot resolve reference: {0}'.format(element_type))
