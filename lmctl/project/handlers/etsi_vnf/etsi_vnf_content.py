import os
import zipfile
import shutil
import lmctl.project.handlers.resource as resource_api
import lmctl.project.handlers.brent as brent_api
import lmctl.project.validation as project_validation
from lmctl.project.validation import ValidationResult, ValidationViolation
from lmctl.project.handlers.brent.brent_autocorrect import BrentCorrectableValidation
from lmctl.project.handlers.brent.brent_content import BrentResourcePackageContentTree
import lmctl.utils.descriptors as descriptor_utils
import lmctl.drivers.lm.base as lm_drivers
class EtsiVnfPkgContentTree(brent_api.BrentPkgContentTree):
    def __int__(self, root_path=None):
        super().__init__(root_path)

    MANIFEST_FILE = 'MRF.mf'
    FILES_DIRECTORY = 'Files'
    DEFINITIONS_DIR = 'Definitions'
    LM_DIRECTORY = 'lm'

    @property
    def manifest_file_path(self):
        mf_path = self.resolve_relative_path(EtsiVnfPkgContentTree.MANIFEST_FILE)
        if os.path.exists(mf_path):
            return mf_path

    @property
    def files_dir_path(self):
        files_path = self.resolve_relative_path(EtsiVnfPkgContentTree.FILES_DIRECTORY)
        if os.path.exists(files_path):
            return files_path

    @property
    def definitions_descriptor_file_path(self):
        descriptor_file = self.resolve_relative_path(EtsiVnfPkgContentTree.DEFINITIONS_DIR, EtsiVnfPkgContentTree.LM_DIRECTORY, EtsiVnfPkgContentTree.RESOURCE_YAML_FILE)  
        if os.path.exists(descriptor_file):
            return descriptor_file

    @property
    def definitions_dir_path(self):
        definitions_dir = self.resolve_relative_path(EtsiVnfPkgContentTree.DEFINITIONS_DIR)
        if os.path.exists(definitions_dir):
            return definitions_dir

    def gen_resource_package_file_path(self, resource_name):
        return self.resolve_relative_path('Files/{0}.zip'.format(resource_name))
        
class EtsiVnfContentHandler(resource_api.ResourceContentHandler):
    def __init__(self, root_path, meta):          
        super().__init__(root_path, meta)

    def validate_content(self, journal, env_sessions, validation_options):
        errors = []
        warnings = []
        self.tree = EtsiVnfPkgContentTree(self.root_path)
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

    def push_content(self, journal, env_sessions):
        raise NotImplementedError('This method (push_content) is not implemented')
