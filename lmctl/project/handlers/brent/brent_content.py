import os
import zipfile
import shutil
import lmctl.files as files
import lmctl.project.handlers.interface as handlers_api
import lmctl.project.validation as project_validation
import lmctl.utils.descriptors as descriptor_utils
import lmctl.drivers.lm.base as lm_drivers
from .brent_autocorrect import BrentCorrectableValidation

class BrentPkgContentTree(files.Tree):

    RESOURCE_YAML_FILE = 'resource.yaml'

    def __init__(self, root_path=None):
        super().__init__(root_path)

    def gen_resource_package_file_path(self, resource_name):
        return self.resolve_relative_path('{0}.zip'.format(resource_name))

    @property
    def root_descriptor_file_path(self):
        return self.resolve_relative_path(BrentPkgContentTree.RESOURCE_YAML_FILE)


class BrentResourcePackageContentTree(files.Tree):

    DEFINITIONS_DIR_NAME = 'Definitions'
    INFRASTRUCTURE_DIR_NAME = 'infrastructure'
    LM_DIR_NAME = 'lm'
    DESCRIPTOR_FILE_NAME_YML = 'resource.yaml'
    LIFECYCLE_DIR_NAME = 'Lifecycle'
    INFRASTRUCTURE_MANIFEST_FILE_NAME = 'infrastructure.mf'
    LIFECYCLE_MANIFEST_FILE_NAME = 'lifecycle.mf'

    @property
    def definitions_path(self):
        return self.resolve_relative_path(BrentResourcePackageContentTree.DEFINITIONS_DIR_NAME)

    @property
    def infrastructure_definitions_path(self):
        return self.resolve_relative_path(BrentResourcePackageContentTree.DEFINITIONS_DIR_NAME, BrentResourcePackageContentTree.INFRASTRUCTURE_DIR_NAME)

    @property
    def lm_definitions_path(self):
        return self.resolve_relative_path(BrentResourcePackageContentTree.DEFINITIONS_DIR_NAME, BrentResourcePackageContentTree.LM_DIR_NAME)

    @property
    def descriptor_file_path(self):
        return self.resolve_relative_path(BrentResourcePackageContentTree.DEFINITIONS_DIR_NAME, BrentResourcePackageContentTree.LM_DIR_NAME, BrentResourcePackageContentTree.DESCRIPTOR_FILE_NAME_YML)

    @property
    def lifecycle_path(self):
        return self.resolve_relative_path(BrentResourcePackageContentTree.LIFECYCLE_DIR_NAME)

    @property
    def infrastructure_manifest_file_path(self):
        return self.resolve_relative_path(BrentResourcePackageContentTree.DEFINITIONS_DIR_NAME, BrentResourcePackageContentTree.INFRASTRUCTURE_DIR_NAME, BrentResourcePackageContentTree.INFRASTRUCTURE_MANIFEST_FILE_NAME)

    @property
    def lifecycle_manifest_file_path(self):
        return self.resolve_relative_path(BrentResourcePackageContentTree.LIFECYCLE_DIR_NAME, BrentResourcePackageContentTree.LIFECYCLE_MANIFEST_FILE_NAME)


class BrentContentHandlerDelegate(handlers_api.ResourceContentHandlerDelegate):

    def __init__(self, root_path, meta):
        super().__init__(root_path, meta)
        self.tree = BrentPkgContentTree(self.root_path)

    def validate_content(self, journal, env_sessions, validation_options):
        errors = []
        warnings = []
        self.__validate_descriptor(journal, errors, warnings)
        self.__validate_res_pkg(journal, validation_options, errors, warnings)
        return project_validation.ValidationResult(errors, warnings)

    def __validate_descriptor(self, journal, errors, warnings):
        descriptor_path = self.tree.root_descriptor_file_path
        if not os.path.exists(descriptor_path):
            msg = 'No descriptor found at: {0}'.format(descriptor_path)
            journal.error_event(msg)
            errors.append(project_validation.ValidationViolation(msg))

    def __validate_res_pkg(self, journal, validation_options, errors, warnings):
        journal.stage('Checking Resource package exists for {0}'.format(self.meta.name))
        res_pkg_path = self.tree.gen_resource_package_file_path(self.meta.full_name)
        if not os.path.exists(res_pkg_path):
            msg = 'No Resource package found at: {0}'.format(res_pkg_path)
            journal.error_event(msg)
            errors.append(project_validation.ValidationViolation(msg))
        else:
            extraction_path = os.path.join(os.path.dirname(res_pkg_path), 'tmp-extract')
            os.makedirs(extraction_path)
            with zipfile.ZipFile(res_pkg_path, "r") as res_pkg:
                res_pkg.extractall(extraction_path)
            try:
                tree = BrentResourcePackageContentTree(extraction_path)
                BrentCorrectableValidation().validate_and_autocorrect(journal, validation_options, errors, warnings, tree.descriptor_file_path, \
                tree.infrastructure_definitions_path, tree.infrastructure_manifest_file_path, tree.lifecycle_path, \
                    tree.lifecycle_manifest_file_path)
                with zipfile.ZipFile(res_pkg_path, "w") as res_pkg:
                    res_pkg_content_tree = BrentResourcePackageContentTree()
                    included_items = [
                        {'path': tree.definitions_path, 'alias': res_pkg_content_tree.definitions_path},
                        {'path': tree.lifecycle_path, 'alias': res_pkg_content_tree.lifecycle_path}
                    ]
                    for included_item in included_items:
                        self.__add_directory(journal, res_pkg, included_item)
            finally:
                if os.path.exists(extraction_path):
                    shutil.rmtree(extraction_path)

    def __add_directory(self, journal, res_pkg, included_item):
        path = included_item['path']
        res_pkg.write(path, arcname=included_item['alias'])
        rootlen = len(path) + 1
        for root, dirs, files in os.walk(path):
            for dirname in dirs:
                full_path = os.path.join(root, dirname)
                res_pkg.write(full_path, arcname=os.path.join(included_item['alias'], full_path[rootlen:]))
            for filename in files:
                full_path = os.path.join(root, filename)
                res_pkg.write(full_path, arcname=os.path.join(included_item['alias'], full_path[rootlen:]))

    def __clear_existing_descriptor(self, journal, env_sessions):
        lm_session = env_sessions.lm
        descriptor_path = self.tree.root_descriptor_file_path
        descriptor = descriptor_utils.DescriptorParser().read_from_file(descriptor_path)
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
        self.__push_res_pkg(journal, env_sessions, descriptor_name)

    def __push_res_pkg(self, journal, env_sessions, descriptor_name):
        lm_session = env_sessions.lm
        pkg_driver = lm_session.resource_pkg_driver
        journal.event('Removing any existing Resource package named {0} (version: {1}) from Brent: {2} ({3})'.format(descriptor_name, self.meta.version, lm_session.env.name, lm_session.env.address))
        try:
            pkg_driver.delete_package(descriptor_name)
        except lm_drivers.NotFoundException:
            journal.event('No package named {0} found'.format(descriptor_name))
        res_pkg_path = self.tree.gen_resource_package_file_path(self.meta.full_name)
        journal.event('Pushing {0} (version: {1}) Resource package to Brent: {2} ({3})'.format(self.meta.full_name, self.meta.version, lm_session.env.name, lm_session.env.address))
        pkg_driver.onboard_package(res_pkg_path)
        env_sessions.mark_brent_updated()
