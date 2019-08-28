import os
import lmctl.files as files


class BrentPkgContentTree(files.Tree):

    def __init__(self, root_path=None):
        super().__init__(root_path)

    def gen_csar_file_path(self, resource_name):
        return self.resolve_relative_path('{0}.csar'.format(resource_name))

    @property
    def root_descriptor_file_path(self):
        return self.resolve_relative_path('resource.yml')


class BrentCsarContentTree(files.Tree):

    DEFINITIONS_DIR_NAME = 'Definitions'
    INFRASTRUCTURE_DIR_NAME = 'infrastructure'
    INFRASTRUCTURE_MANIFEST_FILE_NAME = 'infrastructure.mf'
    LM_DIR_NAME = 'lm'
    DESCRIPTOR_FILE_NAME_YML = 'resource.yml'
    LIFECYCLE_DIR_NAME = 'Lifecycle'
    LIFECYCLE_MANIFEST_FILE_NAME = 'lifecycle.mf'
    
    @property
    def definitions_path(self):
        return self.resolve_relative_path(BrentCsarContentTree.DEFINITIONS_DIR_NAME)

    @property
    def infrastructure_definitions_path(self):
        return self.resolve_relative_path(BrentCsarContentTree.DEFINITIONS_DIR_NAME, BrentCsarContentTree.INFRASTRUCTURE_DIR_NAME)

    @property
    def infrastructure_manifest_file_path(self):
        return self.resolve_relative_path(BrentCsarContentTree.DEFINITIONS_DIR_NAME, BrentCsarContentTree.INFRASTRUCTURE_DIR_NAME, BrentCsarContentTree.INFRASTRUCTURE_MANIFEST_FILE_NAME)

    @property
    def lm_definitions_path(self):
        return self.resolve_relative_path(BrentCsarContentTree.DEFINITIONS_DIR_NAME, BrentCsarContentTree.LM_DIR_NAME)

    @property
    def descriptor_file_path(self):
        return self.resolve_relative_path(BrentCsarContentTree.DEFINITIONS_DIR_NAME, BrentCsarContentTree.LM_DIR_NAME, BrentCsarContentTree.DESCRIPTOR_FILE_NAME_YML)

    @property
    def lifecycle_path(self):
        return self.resolve_relative_path(BrentCsarContentTree.LIFECYCLE_DIR_NAME)

    @property
    def lifecycle_manifest_file_path(self):
        return self.resolve_relative_path(BrentCsarContentTree.LIFECYCLE_DIR_NAME, BrentCsarContentTree.LIFECYCLE_MANIFEST_FILE_NAME)

