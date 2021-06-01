import os
import lmctl.project.handlers.assembly as assembly_api
from lmctl.project.validation import ValidationResult, ValidationViolation
import lmctl.utils.descriptors as descriptors
import lmctl.drivers.lm.base as lm_drivers


class EtsiNsPkgContentTree(assembly_api.AssemblyPkgContentTree):
    def __int__(self, root_path=None):
        super().__init__(root_path)

    MANIFEST_FILE = 'MRF.mf'
    FILES_DIRECTORY = 'Files'
    DEFINITIONS_DIR = 'Definitions'
    
    @property
    def manifest_file_path(self):
        mf_path = self.resolve_relative_path(EtsiNsPkgContentTree.MANIFEST_FILE)
        if os.path.exists(mf_path):
            return mf_path

    @property
    def files_dir_path(self):
        files_path = self.resolve_relative_path(EtsiNsPkgContentTree.FILES_DIRECTORY)
        if os.path.exists(files_path):
            return files_path

    @property
    def definitions_dir_path(self):
        definitions_dir = self.resolve_relative_path(EtsiNsPkgContentTree.DEFINITIONS_DIR)
        if os.path.exists(definitions_dir):
            return definitions_dir

    @property
    def test_config_dir_path(self):
        return self.resolve_relative_path(assembly_api.AssemblyPkgContentTree.BEHAVIOUR_TESTS_DIR_NAME)            

    @property
    def descriptor_definitions_file_path(self):
        return self.resolve_relative_path(EtsiNsPkgContentTree.DEFINITIONS_DIR, EtsiNsPkgContentTree.DESCRIPTOR_FILE_YML)     

class EtsiNsContentHandler(assembly_api.AssemblyContentHandler):
    def __init__(self, root_path, meta):
        super().__init__(root_path, meta)
        self.tree = EtsiNsPkgContentTree(self.root_path)

    def validate_content(self, journal, env_sessions, validation_options):
        errors = []
        warnings = []        
        self.__validate_descriptor(journal, errors, warnings)
        return ValidationResult(errors, warnings)

    def __validate_descriptor(self, journal, errors, warnings):
        journal.stage('Validating ETSI_NS assembly descriptor for {0}'.format(self.meta.name))
        descriptor_path = self.tree.descriptor_definitions_file_path
        if not os.path.exists(descriptor_path):
            msg = 'No descriptor found at: {0}'.format(descriptor_path)
            journal.error_event(msg)
            errors.append(ValidationViolation(msg))        


    def push_content(self, journal, env_sessions):
        raise NotImplementedError('This method (push_content) is not implemented')