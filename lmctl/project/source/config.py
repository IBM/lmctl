import lmctl.project.types as types 
import os
import yaml
import shutil 
import lmctl.utils.descriptors as descriptor_utils

# Any Projects without a Schema are deemed to be using Schema 1.0, as the idea of a Schema was only introduced in v2.1 of lmctl
SCHEMA_1_0 = '1.0'
SCHEMA_2_0 = '2.0'

class ProjectConfigError(Exception):
    pass


class ProjectConfigParser:

    @staticmethod
    def from_dict(config_dict, schema_lenient=False):
        return ProjectConfigParserWorker(config_dict, schema_lenient).parse()


class ProjectConfig:

    def __init__(self):
        pass

    @property
    def name(self):
        pass

    @property
    def full_name(self):
        pass

    @property
    def schema(self):
        pass

    @property
    def project_type(self):
        pass

    @property
    def resource_manager(self):
        pass

    @property
    def subprojects(self):
        pass

    @property
    def subproject_entries(self):
        pass

    @property
    def descriptor_name(self):
        pass

    def is_subproject(self):
        return False

    def is_resource_project(self):
        return types.is_resource_type(self.project_type)

    def is_assembly_project(self):
        return types.is_assembly_type(self.project_type)

    def is_type_project(self):
        return types.is_type_project_type(self.project_type)

    def is_etsi_vnf_project(self):
        return types.is_etsi_vnf_type(self.project_type)

    def is_etsi_ns_project(self):
        return types.is_etsi_ns_type(self.project_type)

class ProjectConfigBase(ProjectConfig):

    def __init__(self, name, project_type, resource_manager=None, subproject_entries=None):
        if not name:
            raise ProjectConfigError('name must be defined')
        self._name = name
        if not project_type:
            raise ProjectConfigError('project_type must be defined')
        if not types.is_assembly_type(project_type) and not types.is_resource_type(project_type) and not types.is_type_project_type(project_type) and not types.is_etsi_vnf_type(project_type) and not types.is_etsi_ns_type(project_type):
            raise ProjectConfigError('Project type must be one of: {0}'.format([types.ASSEMBLY_PROJECT_TYPE, types.RESOURCE_PROJECT_TYPE, types.TYPE_PROJECT_TYPE, types.ETSI_NS_PROJECT_TYPE, types.ETSI_VNF_PROJECT_TYPE]))
        self._project_type = project_type
        if not subproject_entries:
            subproject_entries = []
        self._subproject_entries = subproject_entries
        if not resource_manager:
            if project_type in [types.RESOURCE_PROJECT_TYPE, types.ETSI_VNF_PROJECT_TYPE]:
                raise ProjectConfigError('resource_manager must be defined when type is {0}'.format(project_type))
        else:
            if resource_manager not in types.SUPPORTED_RM_TYPES:
                raise ProjectConfigError('resource_manager type not supported, must be one of: {0}'.format(types.SUPPORTED_RM_TYPES_GROUPED))
        if types.is_etsi_vnf_type(project_type) and resource_manager not in types.BRENT_RM_TYPES:
            raise ProjectConfigError('resource_manager type not supported, FOR ETSI_VNF projects resource_manager must be one of: {0}'.format(types.BRENT_RM_TYPES))
        self._resource_manager = resource_manager

    @property
    def name(self):
        return self._name

    @property
    def full_name(self):
        return self._name

    @property
    def project_type(self):
        return self._project_type

    @property
    def resource_manager(self):
        return self._resource_manager

    @property
    def descriptor_name(self):
        descriptor_type = descriptor_utils.ASSEMBLY_DESCRIPTOR_TYPE
        if self.is_resource_project() or self.is_etsi_vnf_project():
            descriptor_type = descriptor_utils.RESOURCE_DESCRIPTOR_TYPE
        elif self.is_type_project():
            descriptor_type = descriptor_utils.TYPE_DESCRIPTOR_TYPE
        return descriptor_utils.DescriptorName(descriptor_type, self.full_name, self.version).name_str()

    @property
    def subprojects(self):
        subprojects = []
        for entry in self._subproject_entries:
            subprojects.append(SubprojectConfig(self, entry))
        return subprojects

    @property
    def subproject_entries(self):
        return self._subproject_entries

    def to_dict(self):
        data = {
            'name': self.name,
            'type': self.project_type
        }
        if self.is_resource_project() or self.is_etsi_vnf_project():
            data['resource-manager'] = self.resource_manager
        if len(self.subproject_entries) > 0:
            data['contains'] = []
            for entry in self.subproject_entries:
                data['contains'].append(entry.to_dict())
        return data


class RootProjectConfig(ProjectConfigBase):

    def __init__(self, schema, name, version, project_type, resource_manager=None, subproject_entries=None, packaging=None):
        super().__init__(name, project_type, resource_manager, subproject_entries)
        if not schema:
            raise ValueError('schema must be defined')
        self._schema = schema
        if not version:
            raise ValueError('version must be defined')
        self._version = version
        if not packaging:
            packaging = 'tgz'
        self._packaging = packaging

    @property
    def schema(self):
        return self._schema

    @property
    def version(self):
        return self._version

    @property
    def packaging(self):
        return self._packaging

    def to_dict(self):
        data = {}
        data['schema'] = self.schema
        base_data = super().to_dict()
        data['name'] = base_data['name']
        del base_data['name']
        data['version'] = self.version
        data['packaging'] = self.packaging
        for key, value in base_data.items():
            data[key] = value
        return data


class SubprojectConfig(ProjectConfigBase):

    def __init__(self, parent_project, entry):
        super().__init__(entry.name, entry.project_type, entry.resource_manager, entry.subproject_entries)
        self.parent_project = parent_project
        self.entry = entry

    @property
    def schema(self):
        return self.parent_project.schema

    @property
    def version(self):
        return self.parent_project.version

    @property
    def directory(self):
        return self.entry.directory

    @property
    def full_name(self):
        return '{0}-{1}'.format(self.entry.name, self.parent_project.full_name)

    def is_subproject(self):
        return True


class SubprojectEntry(ProjectConfigBase):

    def __init__(self, name, directory, project_type, resource_manager=None, subproject_entries=None):
        super().__init__(name, project_type, resource_manager, subproject_entries)
        if not directory:
            raise ProjectConfigError('directory must be defined')
        self.directory = directory

    def to_dict(self):
        data = super().to_dict()
        data['directory'] = self.directory
        return data


class ProjectConfigParserWorker:
    """
    Handles reading a raw dictionary contents of a project file into Project objects
    """

    def __init__(self, config_dict, schema_lenient=False):
        if not config_dict:
            raise ProjectConfigError('config_dict must be defined')
        self.config_dict = config_dict
        self.schema_lenient = schema_lenient

    def parse(self):
        self.schema = self.__read_schema()
        self.packaging = self.__read_packaging()
        self.project_name = self.__read_project_name(self.config_dict)
        self.project_type = self.__read_project_type(self.config_dict)
        self.project_version = self.__read_project_version(self.config_dict)
        resource_manager = None
        subprojects = self.__read_subprojects(self.config_dict)
        if types.is_resource_type(self.project_type) or types.is_etsi_vnf_type(self.project_type):
            resource_manager = self.__read_resource_manager(self.config_dict)
        return RootProjectConfig(self.schema, self.project_name, self.project_version, self.project_type, resource_manager, subprojects, packaging=self.packaging)

    def __read_schema(self):
        if 'schema' not in self.config_dict:
            if self.schema_lenient is True:
                return SCHEMA_1_0
            else:
                return None
        return self.config_dict['schema']

    def __read_packaging(self):
        return self.config_dict.get('packaging', None)

    def __read_project_name(self, config_dict):
        return config_dict.get('name', None)

    def __read_project_version(self, config_dict):
        return config_dict.get('version', None)

    def __read_resource_manager(self, config_dict):
        return config_dict.get('resource-manager', None)

    def __read_project_type(self, config_dict):
        if 'type' not in config_dict:
            return types.ASSEMBLY_PROJECT_TYPE
        project_type = config_dict['type']
        return project_type

    def __read_subprojects(self, config_dict):
        subprojects = []
        if 'contains' in config_dict:
            for raw_subproject in config_dict['contains']:
                subprojects.append(self.__read_subproject_entry(raw_subproject))
        return subprojects

    def __read_subproject_entry(self, raw_subproject_entry):
        sub_name = self.__read_project_name(raw_subproject_entry)
        directory = raw_subproject_entry.get('directory', sub_name)
        project_type = self.__read_project_type(raw_subproject_entry)
        resource_manager = self.__read_resource_manager(raw_subproject_entry)
        subprojects = self.__read_subprojects(raw_subproject_entry)
        return SubprojectEntry(sub_name, directory, project_type, resource_manager, subprojects)


class ProjectParsingException(Exception):
    pass


class ProjectConfigRewriter:

    def __init__(self, path, config, version=None):
        self.path = path
        self.config = config
        if not version:
            version = '1.0'
        self.version = version

    def rewrite(self):
        new_config = {}
        if type(self.config) is not dict:
            raise ProjectConfigError('Configuration should be a dictionary')
        new_config = self.config.copy()
        new_config = self.__add_schema_and_version(new_config)
        new_config = self.__rewrite_vnfcs_as_subprojects(new_config)
        if os.path.exists(self.path):
            backup_file_name = '{0}.bak'.format(os.path.basename(self.path))
            backup_path = os.path.join(os.path.dirname(self.path), backup_file_name)
            shutil.copyfile(self.path, backup_path)
        os.remove(self.path)
        with open(self.path, 'w') as writer:
            writer.write('## Lmctl has updated this file with the latest schema changes. A backup of your existing project file has been placed in the same directory with a .bak extension\n')
            yaml.safe_dump(new_config, writer, default_flow_style=False, sort_keys=False)
        return new_config

    def __add_schema_and_version(self, config):
        new_config = {}
        if 'schema' not in config:
            new_config['schema'] = SCHEMA_2_0
        else:
            new_config['schema'] = config['schema']
        for key, value in config.items():
            if key != 'schema':
                new_config[key] = value        
        if 'version' not in config:
            new_config['version'] = self.version
        return new_config

    def __rewrite_vnfcs_as_subprojects(self, config):
        if 'vnfcs' in config:
            vnfcs = config['vnfcs']
            new_contains = []
            if 'definitions' in vnfcs:
                for def_id, definition in vnfcs['definitions'].items():
                    directory = def_id
                    if 'directory' in definition:
                        directory = definition['directory']
                    new_contains.append({
                        'name': def_id,
                        'type': types.RESOURCE_PROJECT_TYPE, 
                        'directory': directory,
                        'resource-manager': types.ANSIBLE_RM_TYPES[0]
                    })
            if 'contains' in config:
                if type(contains) is list:
                    config['contains'].extend(new_contains)
                else:
                    raise ValueError('\'contains\' should be a list')
            else:
                config['contains'] = new_contains
            del config['vnfcs']
        return config
            