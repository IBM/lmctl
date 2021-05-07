import os
import lmctl.project.handlers.resource as resource_api
import lmctl.project.handlers.brent as brent_api


class EtsiVnfPkgContentTree(brent_api.BrentPkgContentTree):
    def __int__(self, root_path=None):
        super().__init__(root_path)

    MANIFEST_FILE = 'MRF.mf'
    FILES_DIRECTORY = 'Files'
    DEFINITIONS_DIR = 'Definitions'
    
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
    def definitions_dir_path(self):
        definitions_dir = self.resolve_relative_path(EtsiVnfPkgContentTree.DEFINITIONS_DIR)
        if os.path.exists(definitions_dir):
            return definitions_dir

    def gen_resource_package_file_path(self, resource_name):
        return self.resolve_relative_path('Files/{0}.zip'.format(resource_name))

class EtsiVnfContentHandler(resource_api.ResourceContentHandler):
    def __init__(self, root_path, meta):          
        super().__init__(root_path, meta)
            