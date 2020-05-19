from lmctl.project.types import ANSIBLE_RM_TYPES, BRENT_RM_TYPES, BRENT_2_1_RM_TYPES
from lmctl.project.validation import ValidationResult, ValidationViolation
import lmctl.project.handlers.interface as handlers_api 
import lmctl.project.handlers.ansiblerm as arm_handlers
import lmctl.project.handlers.brent as brent_handlers
import lmctl.project.handlers.brent2dot1 as brent2dot1_handlers
import lmctl.project.testing as project_testing 

def determine_content_delegate(meta, root_path):
    if hasattr(meta, 'resource_manager'):
        rm_type = meta.resource_manager
        if rm_type in ANSIBLE_RM_TYPES:
            return arm_handlers.content_handler(root_path, meta)
        elif rm_type in BRENT_RM_TYPES:
            return brent_handlers.content_handler(root_path, meta)    
        elif rm_type in BRENT_2_1_RM_TYPES:
            return brent2dot1_handlers.content_handler(root_path, meta)
        else:
            raise handlers_api.InvalidContentTypeError('resource_manager on Resource \'{0}\' not supported: {1}'.format(meta.name, rm_type))
    else:
        raise handlers_api.InvalidContentTypeError('resource_manager not set on Resource: {0}'.format(meta.name))

class ResourceContentHandler(handlers_api.PkgContentHandler):

    def __init__(self, root_path, meta):
        super().__init__(root_path, meta)
        self.delegate = determine_content_delegate(meta, root_path)

    def validate_content(self, journal, env_sessions, validation_options):
        errors = []
        warnings = []
        delegate_result = self.delegate.validate_content(journal, env_sessions, validation_options)
        errors.extend(delegate_result.errors)
        warnings.extend(delegate_result.warnings)
        return ValidationResult(errors, warnings)

    def push_content(self, journal, env_sessions):
        self.delegate.push_content(journal, env_sessions)

    def execute_tests(self, journal, env_sessions, selected_tests):
        journal.event('No tests to execute')
        return project_testing.TestSuiteExecutionReport([])
