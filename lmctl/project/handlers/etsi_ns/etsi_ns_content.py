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
    
    def gen_full_csar_package_file_path(self, resource_name, resource_version):
        if os.path.exists(self.relative_path('_lmctl/build/{0}-{1}.csar'.format(resource_name, resource_version))):
            return self.relative_path('_lmctl/build/{0}-{1}.csar'.format(resource_name, resource_version))        

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
        lm_session = env_sessions.lm
        descriptor_path = self.tree.descriptor_definitions_file_path
        descriptor, descriptor_yml_str = descriptors.DescriptorParser().read_from_file_with_raw(descriptor_path)
        descriptor_name = descriptor.get_name()
        self.__push_res_pkg(journal, env_sessions, descriptor_name)


    def __push_res_pkg(self, journal, env_sessions, descriptor_name):
        lm_session = env_sessions.lm
        pkg_driver = lm_session.pkg_mgmt_driver
        journal.event('Removing any existing ETSI_NS assembly package named {0} (version: {1}) from TNC-O: {2} ({3})'.format(descriptor_name, self.meta.version, lm_session.env.name, lm_session.env.address))
        try:
            pkg_driver.delete_nsd_package(descriptor_name)
        except lm_drivers.NotFoundException:
            journal.event('No package named {0} found'.format(descriptor_name))
        res_pkg_path = self.tree.gen_full_csar_package_file_path(self.meta.full_name, self.meta.version)
        journal.event('Pushing {0} (version: {1}) Resource package to TNC-O: {2} ({3})'.format(self.meta.full_name, self.meta.version, lm_session.env.name, lm_session.env.address))
        pkg_driver.onboard_nsd_package(descriptor_name, res_pkg_path)
        env_sessions.mark_brent_updated()
