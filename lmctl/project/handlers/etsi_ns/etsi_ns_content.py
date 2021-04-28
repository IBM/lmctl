import os
import lmctl.project.handlers.assembly as assembly_api

class EtsiNsPkgContentTree(assembly_api.AssemblyPkgContentTree):
    def __int__(self, root_path=None):
        super().__init__(root_path)

    MANIFEST_FILE = 'MRF.mf'
    FILES_DIRECTORY = 'Files'
    
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

class EtsiNsContentHandler(assembly_api.AssemblyContentHandler):
    def __init__(self, root_path, meta):
        super().__init__(root_path, meta)
            