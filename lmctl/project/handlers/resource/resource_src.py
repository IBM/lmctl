from lmctl.project.validation import ValidationResult, ValidationViolation
from lmctl.project.types import ANSIBLE_RM_TYPES, BRENT_RM_TYPES, BRENT_2_1_RM_TYPES
import lmctl.project.handlers.interface as handlers_api 
import lmctl.project.handlers.ansiblerm as arm_handlers
import lmctl.project.handlers.brent as brent_handlers
import lmctl.project.handlers.brent2dot1 as brent2dot1_handlers

def determine_source_handler_delegate(config, root_path):
    if hasattr(config, 'resource_manager'):
        rm_type = config.resource_manager
        if rm_type in ANSIBLE_RM_TYPES:
            return arm_handlers.source_handler(root_path, config)
        elif rm_type in BRENT_RM_TYPES:
            return brent_handlers.source_handler(root_path, config)
        elif rm_type in BRENT_2_1_RM_TYPES:
            return brent2dot1_handlers.source_handler(root_path, config)     
        else:
            raise handlers_api.InvalidSourceTypeError('resource_manager on Resource \'{0}\' not supported: {1}'.format(config.name, rm_type))
    else:
        raise handlers_api.InvalidSourceTypeError('resource_manager not set on Resource: {0}'.format(config.name))

def determine_source_creator_delegate(config):
    if hasattr(config, 'resource_manager'):
        rm_type = config.resource_manager
        if rm_type in ANSIBLE_RM_TYPES:
            return arm_handlers.source_creator()
        elif rm_type in BRENT_RM_TYPES:
            return brent_handlers.source_creator()
        elif rm_type in BRENT_2_1_RM_TYPES:
            return brent2dot1_handlers.source_creator()
        else:
            raise handlers_api.InvalidSourceTypeError('resource_manager on Resource \'{0}\' not supported: {1}'.format(config.name, rm_type))
    else:
        raise handlers_api.InvalidSourceTypeError('resource_manager not set on Resource: {0}'.format(config.name))

class ResourceSourceCreator(handlers_api.SourceCreator):

    def __init__(self):
        super().__init__()

    def __create_file_ops_executor(self, journal, source_request):
        def file_ops_executor(file_ops):
            self._execute_file_ops(file_ops, source_request.target_path, journal)
        return file_ops_executor

    def get_params(self, source_request):
        delegate = determine_source_creator_delegate(source_request.source_config)
        return delegate.get_params(source_request)

    def _do_create_source(self, journal, source_request):
        delegate = determine_source_creator_delegate(source_request.source_config)
        delegate.create_source(journal, source_request, self.__create_file_ops_executor(journal, source_request))

class ResourceSourceHandler(handlers_api.SourceHandler):

    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)
        self.delegate = determine_source_handler_delegate(source_config, root_path)

    def validate_sources(self, journal, source_validator, validation_options):
        errors = []
        warnings = []
        descriptor_path = self.delegate.get_main_descriptor()
        source_validator.validate_descriptor(descriptor_path, errors, warnings, allow_autocorrect=validation_options.allow_autocorrect)
        delegate_result = self.delegate.validate_sources(journal, source_validator, validation_options)
        errors.extend(delegate_result.errors)
        warnings.extend(delegate_result.warnings)
        return ValidationResult(errors, warnings)

    def stage_sources(self, journal, source_stager):
        self.delegate.stage_sources(journal, source_stager)

    def build_staged_source_handler(self, staging_path):
        return ResourceStagedSourceHandler(staging_path, self.source_config, self.delegate.build_staged_source_delegate(staging_path))

    def pull_sources(self, journal, backup_tool, env_sessions, references):
        journal.event('Nothing to pull')
        return

    def list_elements(self, journal, element_type):
        return []


class ResourceStagedSourceHandler(handlers_api.StagedSourceHandler):

    def __init__(self, root_path, source_config, delegate):
        super().__init__(root_path, source_config)
        self.delegate = delegate

    def compile_sources(self, journal, source_compiler):
        self.delegate.compile_sources(journal, source_compiler)
