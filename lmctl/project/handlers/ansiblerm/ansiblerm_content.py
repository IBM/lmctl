import os
import lmctl.files as files
import lmctl.utils.descriptors as descriptors
import lmctl.drivers.lm.base as lm_drivers
import lmctl.project.validation as validation 
import lmctl.project.handlers.interface as handlers_api

class AnsibleRmPkgContentTree(files.Tree):

    def __init__(self, root_path=None):
        super().__init__(root_path)

    def gen_csar_file_path(self, resource_name):
        return self.resolve_relative_path('{0}.csar'.format(resource_name))

    def gen_root_descriptor_file_path(self, resource_name):
        return self.resolve_relative_path('{0}.yml'.format(resource_name))


class AnsibleRmCsarContentTree(files.Tree):

    DESCRIPTOR_DIR_NAME = 'descriptor'
    LIFECYCLE_DIR_NAME = 'lifecycle'
    META_INF_DIR_NAME = 'Meta-Inf'
    TESTS_DIR_NAME = 'tests'
    MANIFEST_FILE_NAME = 'manifest.MF'

    def __init__(self, root_path=None):
        super().__init__(root_path)

    @property
    def descriptor_path(self):
        return self.resolve_relative_path(AnsibleRmCsarContentTree.DESCRIPTOR_DIR_NAME)

    def gen_descriptor_file_path(self, resource_name):
        return self.resolve_relative_path(AnsibleRmCsarContentTree.DESCRIPTOR_DIR_NAME, '{0}.yml'.format(resource_name))

    @property
    def lifecycle_path(self):
        return self.resolve_relative_path(AnsibleRmCsarContentTree.LIFECYCLE_DIR_NAME)

    @property
    def meta_inf_path(self):
        return self.resolve_relative_path(AnsibleRmCsarContentTree.META_INF_DIR_NAME)

    @property
    def meta_inf_manifest_file_path(self):
        return self.resolve_relative_path(AnsibleRmCsarContentTree.META_INF_DIR_NAME, AnsibleRmCsarContentTree.MANIFEST_FILE_NAME)

    @property
    def tests_path(self):
        return self.resolve_relative_path(AnsibleRmCsarContentTree.TESTS_DIR_NAME)



class AnsibleRmContentHandlerDelegate(handlers_api.ResourceContentHandlerDelegate):

    def __init__(self, root_path, meta):
        super().__init__(root_path, meta)
        self.tree = AnsibleRmPkgContentTree(self.root_path)

    def validate_content(self, journal, env_sessions, validation_options):
        errors = []
        warnings = []
        self.__validate_descriptor(journal, errors, warnings)
        self.__validate_csar(journal, errors, warnings)
        return validation.ValidationResult(errors, warnings)

    def __validate_descriptor(self, journal, errors, warnings):
        descriptor_path = self.tree.gen_root_descriptor_file_path(self.meta.full_name)
        if not os.path.exists(descriptor_path):
            msg = 'No descriptor found at: {0}'.format(descriptor_path)
            journal.error_event(msg)
            errors.append(validation.ValidationViolation(msg))

    def __validate_csar(self, journal, errors, warnings):
        journal.stage('Checking CSAR exists for {0}'.format(self.meta.name))
        csar_path = self.tree.gen_csar_file_path(self.meta.full_name)
        if not os.path.exists(csar_path):
            msg = 'No CSAR found at: {0}'.format(csar_path)
            journal.error_event(msg)
            errors.append(validation.ValidationViolation(msg))

    def __clear_existing_descriptor(self, journal, env_sessions):
        lm_session = env_sessions.lm
        descriptor_path = self.tree.gen_root_descriptor_file_path(self.meta.full_name)
        descriptor = descriptors.DescriptorParser().read_from_file(descriptor_path)
        descriptor_name = descriptor.get_name()
        descriptor_version = descriptor.get_version()
        journal.event('Removing descriptor {0} from CP4NA orchestration ({1})'.format(descriptor_name, lm_session.env.address))
        descriptor_driver = lm_session.descriptor_driver
        try:
            descriptor_driver.delete_descriptor(descriptor_name)
            env_sessions.mark_lm_updated()
        except lm_drivers.NotFoundException:
            journal.event('Descriptor {0} not found'.format(descriptor_name))
        return descriptor_name, descriptor_version

    def push_content(self, journal, env_sessions):
        descriptor_name, descriptor_version = self.__clear_existing_descriptor(journal, env_sessions)
        self.__push_csar(journal, env_sessions, descriptor_version)

    def __push_csar(self, journal, env_sessions, descriptor_version):
        lm_session = env_sessions.lm
        arm_session = env_sessions.arm
        csar_path = self.tree.gen_csar_file_path(self.meta.full_name)
        journal.event('Pushing {0} (version: {1}) CSAR to ansible-rm: {2} ({3})'.format(self.meta.full_name, descriptor_version, arm_session.env.name, arm_session.env.address))
        driver = arm_session.arm_driver
        driver.onboard_type(self.meta.full_name, descriptor_version, csar_path)
        env_sessions.mark_arm_updated()

