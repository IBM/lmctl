import abc
import os
import shutil
from lmctl.project.source.config import RootProjectConfig
import lmctl.project.types as project_types
from datetime import datetime, timezone

PACKAGING_PARAM = 'packaging'
TGZ_PACKAGING = 'tgz'
CSAR_PACKAGING = 'csar'
TOSCA_METADATA = 'TOSCA-Metadata'
TOSCA_META_FILE = 'TOSCA.meta'
LICENSE_FILE = 'Files/Licenses/License.txt'
CHANGELOG_FILE = 'Files/Changelog.txt'
DEFINITIONS_FILE = 'Definitions/MRF.yaml'
MF_FILE='MRF.mf'

############################
# Source Creator Exceptions
############################

class SourceCreationError(Exception):
    pass

############################
# Source Creators
############################

class SourceCreationRequest:

    def __init__(self, target_path, source_config, param_values=None):
        self.target_path = target_path
        self.source_config = source_config
        self.param_values = param_values if param_values is not None else SourceCreationParamValues({})

class SourceCreationParamValues:

    def __init__(self, values, parent_values=None):
        self.values = values
        self.parent_values = parent_values

    def direct_values(self):
        return self.values.items()

    def _get_direct_value(self, key):
        return self.values.get(key, None)

    def _get_inherited_value(self, key):
        if self.parent_values is not None:
            return self.parent_values.get_value(key)
        else:
            return None

    def get_value(self, key):
        value = self._get_direct_value(key)
        if value is None:
            value = self._get_inherited_value(key)
        return value

class SourceParam:

    def __init__(self, name, required=False, default_value=None, allowed_values=None):
        self.name = name
        self.required = required
        self.default_value = default_value
        self.allowed_values = allowed_values

class SourceCreator(abc.ABC):

    def __init__(self):
        pass

    def _validate_expected_params(self, journal, source_request):
        params = self.get_params(source_request)
        params.append(SourceParam(PACKAGING_PARAM, required=False, default_value=TGZ_PACKAGING, allowed_values=[TGZ_PACKAGING, CSAR_PACKAGING]))
        mandatory_params = {}
        optional_params = {}
        for param in params:
            if param.required:
                mandatory_params[param.name] = param
        self._set_defaults(source_request, params)
        self._check_mandatory_params(journal, source_request, mandatory_params)
        self._check_allowed_values(journal, source_request, params)
        self._check_unexpected_params(journal, source_request, params)
        
    def _check_mandatory_params(self, journal, source_request, mandatory_params):
        for param_name, param in mandatory_params.items():
            value = source_request.param_values.get_value(param_name)
            if value is None:
                raise SourceCreationError('Request to create sources for \'{0}\' is missing required param: {1}'.format(source_request.source_config.name, param_name))
    
    def _check_allowed_values(self, journal, source_request, params):
        for param in params:
            if param.allowed_values != None:
                value = source_request.param_values.get_value(param.name)
                if value is not None:
                    if value not in param.allowed_values:
                        raise SourceCreationError('Unexpected value \'{0}\' provided to param \'{1}\' on request for \'{2}\', must be one of: {3}'.format(value, param.name, source_request.source_config.name, param.allowed_values))

    def _check_unexpected_params(self, journal, source_request, params):
        allowed_params = []
        for param in params:
            allowed_params.append(param.name)
        for param_name, _ in source_request.param_values.direct_values():
            if param_name not in allowed_params:
                raise SourceCreationError('Unexpected param \'{0}\' provided to request for \'{1}\'. Supported params {2}'.format(param_name, source_request.source_config.name, allowed_params))

    def _set_defaults(self, source_request, params):
        for param in params:
            if not param.required and param.default_value is not None:
                value = source_request.param_values.get_value(param.name)
                if value is None:
                    source_request.param_values.values[param.name] = param.default_value

    def _execute_file_ops(self, file_ops, path, journal):
        for file_op in file_ops:
            file_op.execute(path, journal)

    def get_params(self, source_request):
        return []

    def create_source(self, journal, source_request):
        self._validate_expected_params(journal, source_request)
        self._do_create_common_source(journal, source_request)
        self._do_create_source(journal, source_request)
        if(self.__is_etsi_vnf_project(source_request.source_config.project_type)):
            self._do_create_etsi_vnf_manifest(journal, source_request)
        if(self.__is_etsi_ns_project(source_request.source_config.project_type)):
            self._do_create_etsi_ns_manifest(journal, source_request)


    @abc.abstractmethod
    def _do_create_source(self, journal, source_request):
        pass

    def _do_create_common_source(self, journal, source_request):
        file_ops = []
        #Only create for the root project
        if isinstance(source_request.source_config, RootProjectConfig):
            packaging_type = source_request.param_values.get_value(PACKAGING_PARAM)
            if packaging_type == CSAR_PACKAGING:
                file_ops.append(CreateDirectoryOp(TOSCA_METADATA, EXISTING_IGNORE))
                meta_content = 'TOSCA-Meta-File-Version: 1.0'
                meta_content += '\nCSAR-Version: 1.1'
                meta_content += '\nCreated-by: Author Here'
                meta_content += '\nEntry-Definitions: Definitions'
                if(self.__is_etsi_project(source_request.source_config.project_type)):
                    meta_content += '/MRF.yaml'
                    meta_content += '\nETSI-Entry-Manifest: MRF.mf'
                    meta_content += '\nETSI-Entry-Licenses: '+LICENSE_FILE
                    meta_content += '\nETSI-Entry-Change-Log: '+CHANGELOG_FILE
                    if source_request.source_config.project_type == project_types.ETSI_NS_PROJECT_TYPE:
                        meta_content += '\nTNCO-Descriptor: Definitions/assembly.yml'
                    elif source_request.source_config.project_type == project_types.ETSI_VNF_PROJECT_TYPE:
                        meta_content += '\nTNCO-Descriptor: Definitions/lm/resource.yaml'                    
                    file_ops.append(CreateFileOp(LICENSE_FILE, content='# License', on_existing=EXISTING_IGNORE))
                    file_ops.append(CreateFileOp(CHANGELOG_FILE, content='# Changelog', on_existing=EXISTING_IGNORE))
                    file_ops.append(CreateFileOp(DEFINITIONS_FILE, content='tosca_definitions_version: tosca_simple_yaml_1_2', on_existing=EXISTING_IGNORE))                    
                file_ops.append(CreateFileOp(os.path.join(TOSCA_METADATA, TOSCA_META_FILE), meta_content, EXISTING_IGNORE))
        self._execute_file_ops(file_ops, source_request.target_path, journal)

    
    def _do_create_etsi_vnf_manifest(self, journal, source_request):
        file_ops = []
        d = datetime.now(timezone.utc)
        manifest_content = 'metadata:\n'
        manifest_content += 'vnfd_id: TBC\n'
        manifest_content += 'vnf_provider_id: IBM\n'
        manifest_content += 'vnf_product_name: TNC-O\n'
        manifest_content += 'vnf_release_date_time: '+d.isoformat()+'\n'
        manifest_content += 'vnf_software_version: 1.0\n'
        manifest_content += 'vnf_package_version: 1.0\n'
        manifest_content += 'vnfm_info: etsivnfm:v3.3.1\n'
        manifest_content += 'compatible_specification_versions: 3.1.1\n'
        file_ops.append(CreateFileOp(MF_FILE, manifest_content, on_existing=EXISTING_IGNORE))
        self._execute_file_ops(file_ops, source_request.target_path, journal)

    def _do_create_etsi_ns_manifest(self, journal, source_request):
        file_ops = []
        d = datetime.now(timezone.utc)        
        manifest_content = 'metadata:\n'
        manifest_content += 'nsd_designer: IBM\n'
        manifest_content += 'nsd_invariant_id: TBC\n'
        manifest_content += 'nsd_name: TBC\n'
        manifest_content += 'nsd_release_date_time: '+d.isoformat()+'\n'
        manifest_content += 'nsd_file_structure_version: 1.0\n'
        manifest_content += 'compatible_specification_versions: 3.1.1\n'
        file_ops.append(CreateFileOp(MF_FILE, manifest_content, on_existing=EXISTING_IGNORE))
        self._execute_file_ops(file_ops, source_request.target_path, journal)

    def __is_etsi_project(self, project_type):
        if project_type is None:
            return False
        return project_type in [project_types.ETSI_NS_PROJECT_TYPE, project_types.ETSI_VNF_PROJECT_TYPE]

    def __is_etsi_ns_project(self, project_type):
        if project_type is None:
            return False
        return project_type in [project_types.ETSI_NS_PROJECT_TYPE]

    def __is_etsi_vnf_project(self, project_type):
        if project_type is None:
            return False
        return project_type in [project_types.ETSI_VNF_PROJECT_TYPE]

class ResourceSourceCreatorDelegate(abc.ABC):

    def __init__(self):
        pass

    def get_params(self, source_request):
        return []
    
    @abc.abstractmethod
    def create_source(self, journal, source_request, file_ops_executor):
        pass

EXISTING_FAIL = 'fail'
EXISTING_OVERWRITE = 'overwrite'
EXISTING_IGNORE = 'ignore'

class CreateFileOp:

    def __init__(self, relative_file_path, content=None, on_existing=EXISTING_FAIL):
        self.relative_file_path = relative_file_path
        self.content = content
        self.on_existing = on_existing

    def execute(self, path, journal):
        full_path = os.path.join(path, self.relative_file_path)
        if os.path.exists(full_path):
            if self.on_existing == EXISTING_FAIL:
                raise SourceCreationError('File already exists: {0}'.format(full_path))
            elif self.on_existing == EXISTING_IGNORE:
                journal.event('Not creating file as it already exists: {0}'.format(full_path))
                return
            else:
                journal.event('Replacing file: {0}'.format(full_path))
                os.remove(full_path)
        else:
            journal.event('Creating file: {0}'.format(full_path))
        dir_name = os.path.dirname(full_path)
        os.makedirs(dir_name, exist_ok=True)
        with open(full_path, 'w') as writer:
            writer.write(self.content)


class CreateDirectoryOp:

    def __init__(self, relative_dir_path, on_existing=EXISTING_FAIL):
        self.relative_dir_path = relative_dir_path
        self.on_existing = on_existing

    def execute(self, path, journal):
        full_path = os.path.join(path, self.relative_dir_path)
        if os.path.exists(full_path):
            if self.on_existing == EXISTING_FAIL:
                raise SourceCreationError('Directory already exists: {0}'.format(full_path))
            elif self.on_existing == EXISTING_IGNORE:
                journal.event('Not creating directory as it already exists: {0}'.format(full_path))
                return
            else:
                journal.event('Replacing directory (and all contents): {0}'.format(full_path))
                shutil.rmtree(full_path)
        else:
            journal.event('Creating directory: {0}'.format(full_path))
        os.makedirs(full_path)


############################
# Source Handler Exceptions
############################

class SourceHandlerError(Exception):
    pass

class InvalidSourceError(SourceHandlerError):
    pass

class InvalidSourceTypeError(SourceHandlerError):
    pass

class PullSourceError(SourceHandlerError):
    pass


############################
# Source Handlers Options
############################

class SourceValidationOptions:
    def __init__(self, allow_autocorrect=False):
        self.allow_autocorrect = allow_autocorrect

############################
# Source Handlers
############################

class SourceHandler(abc.ABC):

    def __init__(self, root_path, source_config):
        self.root_path = root_path
        self.source_config = source_config

    @abc.abstractmethod
    def validate_sources(self, journal, source_validator, validation_options):
        pass

    @abc.abstractmethod
    def stage_sources(self, journal, source_stager):
        pass

    @abc.abstractmethod
    def build_staged_source_handler(self, staging_path):
        pass

    @abc.abstractmethod
    def pull_sources(self, journal, backup_tool, env_sessions, references):
        pass

    @abc.abstractmethod
    def list_elements(self, journal, element_type):
        pass

ELEMENT_TYPE_TESTS = 'tests'

class StagedSourceHandler(abc.ABC):

    def __init__(self, root_path, source_config):
        self.root_path = root_path
        self.source_config = source_config

    @abc.abstractmethod
    def compile_sources(self, journal, source_compiler):
        pass


class ResourceSourceHandlerDelegate(abc.ABC):

    def __init__(self, root_path, source_config):
        if root_path is None:
            raise ValueError('root_path must be provided for a source handler delegate')
        self.root_path = root_path
        self.source_config = source_config

    @abc.abstractmethod
    def validate_sources(self, journal, source_validator, validation_options):
        pass

    @abc.abstractmethod
    def stage_sources(self, journal, source_stager):
        pass

    @abc.abstractmethod
    def build_staged_source_delegate(self, staging_path):
        pass

    @abc.abstractmethod
    def get_main_descriptor(self):
        pass


class ResourceStagedSourceHandlerDelegate(abc.ABC):

    def __init__(self, root_path, source_config):
        if root_path is None:
            raise ValueError('root_path must be provided for a source handler delegate')
        self.root_path = root_path
        self.source_config = source_config

    @abc.abstractmethod
    def compile_sources(self, journal, source_compiler):
        pass

############################
# Content Exceptions
############################

class ContentHandlerError(Exception):
    pass

class InvalidContentTypeError(ContentHandlerError):
    pass

############################
# Content Handlers Options
############################

class ContentValidationOptions:
    def __init__(self, allow_autocorrect=False):
        self.allow_autocorrect = allow_autocorrect

############################
# Content Handlers
############################

class PkgContentHandler(abc.ABC):

    def __init__(self, root_path, meta):
        self.root_path = root_path
        self.meta = meta

    @abc.abstractmethod
    def validate_content(self, journal, env_sessions, validation_options):
        pass

    @abc.abstractmethod
    def push_content(self, journal, env_sessions):
        pass

    @abc.abstractmethod
    def execute_tests(self, journal, env_sessions, selected_tests):
        pass


class ResourceContentHandlerDelegate(abc.ABC):

    def __init__(self, root_path, meta):
        if root_path is None:
            raise ValueError('root_path must be provided for a source handler delegate')
        self.root_path = root_path
        self.meta = meta

    @abc.abstractmethod
    def validate_content(self, journal, env_sessions, validation_options):
        pass

    @abc.abstractmethod
    def push_content(self, journal, env_sessions):
        pass
