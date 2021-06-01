import lmctl.project.types as types
import os
import yaml 
import shutil
import lmctl.utils.descriptors as descriptor_utils

# Any Packages without a Schema are deemed to be using Schema 1.0, as the idea of a Schema was only introduced in v2.1 of lmctl
SCHEMA_1_0 = '1.0'
SCHEMA_2_0 = '2.0'


class PkgMetaError(Exception):
    pass

class PkgMeta:

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
    def content_type(self):
        pass

    @property
    def resource_manager(self):
        pass

    @property
    def subpkgs(self):
        pass

    @property
    def subpkg_entries(self):
        pass

    @property
    def descriptor_name(self):
        pass

    def is_subpkg(self):
        return False

    def is_resource_content(self):
        return types.is_resource_type(self.content_type) or types.is_etsi_vnf_type(self.content_type)

    def is_assembly_content(self):
        return types.is_assembly_type(self.content_type)

    def is_type_content(self):
        return types.is_type_project_type(self.content_type)
    
    def is_etsi_vnf_content(self):
        return types.is_etsi_vnf_type(self.content_type)
    
    def is_etsi_ns_content(self):
        return types.is_etsi_ns_type(self.content_type)        

    def is_etsi_content(self):
        return types.is_etsi_ns_type(self.content_type) or types.is_etsi_vnf_type(self.content_type)

class PkgMetaBase(PkgMeta):

    def __init__(self, name, content_type, resource_manager=None, subpkg_entries=None):
        if not name:
            raise PkgMetaError('name must be defined')
        self._name = name
        if not content_type:
            raise PkgMetaError('content_type must be defined')
        self._content_type = content_type
        if not subpkg_entries:
            subpkg_entries = []
        self._subpkg_entries = subpkg_entries
        if not resource_manager:
            if self.is_resource_content():
                raise PkgMetaError('resource_manager must be defined when type is {0}'.format(types.RESOURCE_PROJECT_TYPE))
        else:
            if resource_manager not in types.SUPPORTED_RM_TYPES:
                raise PkgMetaError('resource_manager type not supported, must be one of: {0}'.format(types.SUPPORTED_RM_TYPES_GROUPED))
        self._resource_manager = resource_manager

    @property
    def name(self):
        return self._name

    @property
    def full_name(self):
        return self._name

    @property
    def content_type(self):
        return self._content_type

    @property
    def resource_manager(self):
        return self._resource_manager

    @property
    def descriptor_name(self):
        descriptor_type = descriptor_utils.ASSEMBLY_DESCRIPTOR_TYPE
        if self.is_resource_content():
            descriptor_type = descriptor_utils.RESOURCE_DESCRIPTOR_TYPE
        elif self.is_type_content():
            descriptor_type = descriptor_utils.TYPE_DESCRIPTOR_TYPE
        return descriptor_utils.DescriptorName(descriptor_type, self.full_name, self.version).name_str()

    @property
    def subpkgs(self):
        subpkgs = []
        for entry in self._subpkg_entries:
            subpkgs.append(SubPkgMeta(self, entry))
        return subpkgs

    @property
    def subpkg_entries(self):
        return self._subpkg_entries

    def to_dict(self):
        data = {
            'name': self.name,
            'type': self.content_type
        }
        if self.is_resource_content():
            data['resource-manager'] = self.resource_manager
        if len(self.subpkg_entries) > 0:
            data['contains'] = []
            for entry in self.subpkg_entries:
                data['contains'].append(entry.to_dict())
        return data


class RootPkgMeta(PkgMetaBase):

    def __init__(self, schema, name, version, content_type, resource_manager=None, subpkg_entries=None):
        super().__init__(name, content_type, resource_manager, subpkg_entries)
        if not schema:
            raise ValueError('schema must be defined')
        self._schema = schema
        if not version:
            raise ValueError('version must be defined')
        self._version = version

    @property
    def schema(self):
        return self._schema

    @property
    def version(self):
        return self._version

    def to_dict(self):
        data = {}
        data['schema'] = self.schema
        base_data = super().to_dict()
        data['name'] = base_data['name']
        del base_data['name']
        data['version'] = self.version
        for key, value in base_data.items():
            data[key] = value
        return data


class SubPkgMeta(PkgMetaBase):

    def __init__(self, parent_meta, entry):
        super().__init__(entry.name, entry.content_type, entry.resource_manager, entry.subpkg_entries)
        self.parent_meta = parent_meta
        self.entry = entry

    @property
    def schema(self):
        return self.parent_meta.schema

    @property
    def version(self):
        return self.parent_meta.version

    @property
    def full_name(self):
        if self.entry.full_name_override:
            return self.entry.full_name_override
        return '{0}-{1}'.format(self.entry.name, self.parent_meta.full_name)

    @property
    def directory(self):
        return self.entry.directory

    def is_subpkg(self):
        return True


class SubPkgEntry(PkgMetaBase):

    def __init__(self, name, directory, content_type, resource_manager=None, subpkg_entries=None, full_name_override=None):
        super().__init__(name, content_type, resource_manager, subpkg_entries)
        if not directory:
            raise ValueError('directory must be defined')
        self.directory = directory
        self.full_name_override = full_name_override

    def to_dict(self):
        data = super().to_dict()
        data['directory'] = self.directory
        return data


class PkgMetaBaseBuilder:

    def __init__(self):
        self._name = None
        self._content_type = None
        self._subpkg_entries = []
        self._resource_manager = None

    def name(self, name):
        self._name = name
        return self

    def content_type(self, content_type):
        self._content_type = content_type
        return self

    def subpkg_entry_builder(self):
        subpkg_entry_builder = SubPkgEntryBuilder()
        self._subpkg_entries.append(subpkg_entry_builder)
        return subpkg_entry_builder

    def resource_manager(self, resource_manager):
        self._resource_manager = resource_manager
        return self

    def _build_subpkg_entries(self):
        entries = []
        for builder in self._subpkg_entries:
            entries.append(builder.build())
        return entries


class RootPkgMetaBuilder(PkgMetaBaseBuilder):

    def __init__(self):
        super().__init__()
        self._schema = None
        self.__version = None

    def schema(self, schema):
        self._schema = schema
        return self

    def version(self, version):
        self._version = version
        return self

    def build(self):
        name = self._name
        content_type = self._content_type
        resource_manager = self._resource_manager
        subpkg_entries = self._build_subpkg_entries()
        return RootPkgMeta(self._schema, name, self._version, content_type, resource_manager, subpkg_entries)


class SubPkgEntryBuilder(PkgMetaBaseBuilder):

    def __init__(self):
        super().__init__()
        self._directory = None

    def directory(self, directory):
        self._directory = directory
        return self

    def build(self):
        name = self._name
        content_type = self._content_type
        resource_manager = self._resource_manager
        subpkg_entries = self._build_subpkg_entries()
        return SubPkgEntry(name, self._directory, content_type, resource_manager, subpkg_entries)


class PkgMetaParser:

    @staticmethod
    def from_dict(meta_dict):
        return PkgMetaParserWorker(meta_dict).parse()


class PkgMetaParserWorker:
    """
    Handles reading a raw dictionary contents of a pkg meta file
    """

    def __init__(self, meta_dict):
        if not meta_dict:
            raise ValueError('config_dict must be defined')
        self.meta_dict = meta_dict

    def parse(self):
        self.schema = self.__read_schema()
        self.content_name = self.__read_content_name(self.meta_dict)
        self.content_type = self.__read_content_type(self.meta_dict)
        self.content_version = self.__read_content_version(self.meta_dict)
        resource_manager = None
        subcontent = self.__read_subcontents(self.meta_dict)
        if self.content_type in [types.RESOURCE_PROJECT_TYPE, types.ETSI_VNF_PROJECT_TYPE]:
            resource_manager = self.__read_resource_manager(self.meta_dict)
        return RootPkgMeta(self.schema, self.content_name, self.content_version, self.content_type, resource_manager, subcontent)

    def __read_schema(self):
        return self.meta_dict.get('schema', None)

    def __read_content_name(self, meta_dict):
        return meta_dict.get('name', None)

    def __read_content_version(self, meta_dict):
        return meta_dict.get('version', None)

    def __read_resource_manager(self, meta_dict):
        return meta_dict.get('resource-manager', None)

    def __read_content_type(self, meta_dict):
        if 'type' not in meta_dict:
            return types.ASSEMBLY_PROJECT_TYPE
        content_type = meta_dict['type']
        expected_types = [types.ASSEMBLY_PROJECT_TYPE, types.RESOURCE_PROJECT_TYPE, types.NS_PROJECT_TYPE, types.VNF_PROJECT_TYPE, types.TYPE_PROJECT_TYPE, types.ETSI_VNF_PROJECT_TYPE, types.ETSI_NS_PROJECT_TYPE]
        if content_type not in expected_types:
            raise PkgMetaParsingException('Pkg type must be one of: {0}'.format(expected_types))
        return content_type

    def __read_subcontents(self, meta_dict):
        subcontents = []
        if 'contains' in meta_dict:
            for raw_subcontent in meta_dict['contains']:
                subcontents.append(self.__read_subcontent_entry(raw_subcontent))
        return subcontents

    def __read_subcontent_entry(self, raw_subcontent_entry):
        sub_name = self.__read_content_name(raw_subcontent_entry)
        directory = raw_subcontent_entry.get('directory', sub_name)
        content_type = self.__read_content_type(raw_subcontent_entry)
        full_name_override = raw_subcontent_entry.get('full-name-override', None)
        resource_manager = self.__read_resource_manager(raw_subcontent_entry)
        subcontent = self.__read_subcontents(raw_subcontent_entry)
        return SubPkgEntry(sub_name, directory, content_type, resource_manager, subcontent, full_name_override)


class PkgMetaParsingException(Exception):
    pass


class PkgMetaRewriter:

    def __init__(self, path, new_path, meta, version=None):
        self.path = path
        self.new_path = new_path
        self.meta = meta
        if not version:
            version = '1.0'
        self.version = version

    def rewrite(self):
        new_meta = {}
        if type(self.meta) is not dict:
            raise ValueError('Meta should be a dictionary')
        new_meta = self.meta.copy()
        new_meta = self.__add_schema_and_version(new_meta)
        new_meta = self.__rewrite_vnfcs_as_subprojects(new_meta)
        if os.path.exists(self.path):
            backup_file_name = '{0}.bak'.format(os.path.basename(self.path))
            backup_path = os.path.join(os.path.dirname(self.path), backup_file_name)
            shutil.copyfile(self.path, backup_path)
            os.remove(self.path)
        if os.path.exists(self.new_path):
            os.remove(self.new_path)
        with open(self.new_path, 'w') as writer:
            yaml.safe_dump(new_meta, writer, default_flow_style=False, sort_keys=False)
        return new_meta

    def __add_schema_and_version(self, meta):
        new_meta = {}
        if 'schema' not in meta:
            new_meta['schema'] = SCHEMA_2_0
        else:
            new_meta['schema'] = meta['schema']
        for key, value in meta.items():
            if key != 'schema':
                new_meta[key] = value        
        if 'version' not in meta:
            new_meta['version'] = self.version
        return new_meta

    def __rewrite_vnfcs_as_subprojects(self, meta):
        if 'vnfcs' in meta:
            vnfcs = meta['vnfcs']
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
                        'resource-manager': types.ANSIBLE_RM_TYPES[0],
                        'full-name-override': def_id
                    })
            if 'contains' in meta:
                if type(meta['contains']) is list:
                    meta['contains'].extend(new_contains)
                else:
                    raise ValueError('\'contains\' should be a list')
            else:
                meta['contains'] = new_contains
            del meta['vnfcs']
        return meta
            