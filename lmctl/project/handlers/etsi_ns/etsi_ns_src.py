import os, json
import lmctl.project.handlers.assembly as assembly_api
import lmctl.utils.descriptors as descriptors
import lmctl.files as files
from .etsi_ns_content import EtsiNsPkgContentTree

class EtsiNsSourceHandler(assembly_api.AssemblySourceHandler):
    def __init__(self, root_path, source_config):        
        super().__init__(root_path, source_config)
        self.tree = EtsiNsSourceTree(self.root_path)        

    def stage_sources(self, journal, source_stager):
        super().stage_sources(journal, source_stager)
        staging_tree = EtsiNsSourceTree()
        project_manifest_name = self.__stage_etsi_files(journal, source_stager, staging_tree)

    def __stage_etsi_files(self, journal, source_stager, staging_tree):
        manifest_path = self.tree.manifest_file_path
        journal.stage('Staging Manifest file for {0} at {1}'.format(self.source_config.name, manifest_path))
        source_stager.stage_file(manifest_path, staging_tree.manifest_file_path)
        files_dir = self.tree.files_dir_path
        journal.stage('Staging Files Directory for {0} at {1}'.format(self.source_config.name, files_dir))
        source_stager.stage_tree(files_dir, staging_tree.files_dir_path)


    def build_staged_source_handler(self, staging_path):
        return EtsiStagedSourceHandler(staging_path, self.source_config)

class EtsiNsSourceCreator(assembly_api.AssemblySourceCreator):
    def __init__(self):        
        super().__init__()

    def _do_create_source(self, journal, source_request):
        super()._do_create_source(journal, source_request)

class EtsiNsSourceTree(assembly_api.AssemblySourceTree):
    def __init__(self, root_path=None):
        super().__init__(root_path)

    MANIFEST_FILE = 'MRF.mf'
    FILES_DIRECTORY = 'Files'
    
    @property
    def manifest_file_path(self):
        mf_path = self.resolve_relative_path(EtsiNsSourceTree.MANIFEST_FILE)
        if os.path.exists(mf_path):
            return mf_path

    @property
    def files_dir_path(self):
        files_path = self.resolve_relative_path(EtsiNsSourceTree.FILES_DIRECTORY)
        if os.path.exists(files_path):
            return files_path

class EtsiStagedSourceHandler(assembly_api.AssemblyStagedSourceHandler):
    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)
        self.tree = EtsiNsPkgContentTree(self.root_path)


    def compile_sources(self, journal, source_compiler):
        super().compile_sources(journal, source_compiler)
        compile_tree = EtsiNsPkgContentTree()

        journal.event('Compiling additional ETSI files for: {0}'.format(self.source_config.full_name))
        source_compiler.compile_tree(self.tree.files_dir_path, compile_tree.files_dir_path)
        source_compiler.compile_file(self.tree.manifest_file_path, compile_tree.manifest_file_path)
