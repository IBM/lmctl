import lmctl.reference as refs

ROOT = '$lmctl'
SEPARATOR = ':/'

DESCRIPTOR_NAME = 'descriptor_name'
CONTAINS = 'contains'

DESCRIPTOR_MAPPINGS = 'descriptor_mappings'
PROJECT = 'project'

class ConfigReferences(refs.ReferenceMachine):

    def __init__(self, config):
        super().__init__(ROOT, SEPARATOR)
        self.config = config
        self.resolution_map = self.__build_config_resolution_map(self.config)

    def resolve(self, reference):
        return super().resolve(reference, self.resolution_map)

    def __build_config_resolution_map(self, config):
        resolution_map = {}
        self.__add_to_config_resolution_map(config, resolution_map)
        descriptor_mappings = {}
        self.__add_descriptor_mappings(config, descriptor_mappings)
        resolution_map[DESCRIPTOR_MAPPINGS] = descriptor_mappings
        return resolution_map

    def __add_to_config_resolution_map(self, config, current_map):
        current_map[DESCRIPTOR_NAME] = config.descriptor_name
        current_map[CONTAINS] = {}
        for subproject_config in config.subprojects:
            sub_map = {}
            current_map[CONTAINS][subproject_config.name] = sub_map
            self.__add_to_config_resolution_map(subproject_config, sub_map)

    def __add_descriptor_mappings(self, config, descriptor_mappings):
        descriptor_mappings[config.descriptor_name] = { PROJECT: config }
        for subproject_config in config.subprojects:
            self.__add_descriptor_mappings(subproject_config, descriptor_mappings)

    def build_descriptor_to_project_mapping_reference(self, descriptor_name):
        builder = self.builder()
        builder.add(DESCRIPTOR_MAPPINGS).add(descriptor_name).add(PROJECT)
        return builder.get()

    def build_descriptor_reference(self, project_config):
        builder = self.builder()
        if not project_config.is_subproject():
            builder.add(DESCRIPTOR_NAME)
        else:
            builder.add(project_config.name).add(DESCRIPTOR_NAME)
            current_config = project_config.parent_project
            while current_config is not None:
                builder.add_before(CONTAINS)
                if current_config.is_subproject():
                    builder.add_before(current_config.name)
                    current_config = current_config.parent_project
                else:
                    current_config = None
        return builder.get()