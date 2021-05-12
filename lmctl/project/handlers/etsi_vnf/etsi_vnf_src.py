import os
import zipfile
import lmctl.project.handlers.resource as resource_api
import lmctl.project.handlers.brent as brent_api
import lmctl.project.handlers.interface as handlers_api
from lmctl.project.handlers.brent.brent_content import BrentResourcePackageContentTree, BrentPkgContentTree
from .etsi_vnf_content import EtsiVnfPkgContentTree

class EtsiVnfSourceTree(brent_api.BrentSourceTree):
    def __init__(self, root_path=None):
        super().__init__(root_path=root_path)

    MANIFEST_FILE = 'MRF.mf'
    FILES_DIRECTORY = 'Files'

    @property
    def manifest_file_path(self):
        mf_path = self.resolve_relative_path(EtsiVnfSourceTree.MANIFEST_FILE)
        if os.path.exists(mf_path):
            return mf_path

    @property
    def files_dir_path(self):
        files_path = self.resolve_relative_path(EtsiVnfSourceTree.FILES_DIRECTORY)
        if os.path.exists(files_path):
            return files_path


class EtsiVnfSourceHandler(brent_api.BrentSourceHandlerDelegate):
    def __init__(self, root_path, source_config):           
        super().__init__(root_path, source_config)
        self.tree = EtsiVnfSourceTree(self.root_path)
        

    def stage_sources(self, journal, source_stager):
        staging_tree = EtsiVnfSourceTree()     
        self.__stage_etsi_files(journal, source_stager, staging_tree)        
        super().stage_sources(journal, source_stager)


    def __stage_etsi_files(self, journal, source_stager, staging_tree):
        manifest_path = self.tree.manifest_file_path
        journal.stage('Staging Manifest file for {0} at {1}'.format(self.source_config.name, manifest_path))
        source_stager.stage_file(manifest_path, staging_tree.manifest_file_path)
        # contents of Files directory
        files_dir = self.tree.files_dir_path
        journal.stage('Staging Files Directory for {0} at {1}'.format(self.source_config.name, files_dir))
        source_stager.stage_tree(files_dir, staging_tree.files_dir_path)
        # add Definitions dir content (MRF.yml etc.)
        definitions_dir = self.tree.definitions_path
        source_stager.stage_tree(definitions_dir, staging_tree.definitions_path)        


    def build_staged_source_handler(self, staging_path):
        return EtsiVnfStagedSourceHandler(staging_path, self.source_config)

    def pull_sources(self, journal, backup_tool, env_sessions, references):
        journal.event('Nothing to pull')
        return

class EtsiVnfSourceCreator(resource_api.ResourceSourceCreator):
    def __init__(self):
        super().__init__()

    def _do_create_source(self, journal, source_request):
        super()._do_create_source(journal, source_request)    



class EtsiVnfStagedSourceHandler(brent_api.BrentStagedSourceHandlerDelegate):

    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)        

    def compile_sources(self, journal, source_compiler):
        pkg_tree = EtsiVnfPkgContentTree()
        self.__build_res_pkg(journal, source_compiler, pkg_tree)
        self.__add_root_descriptor(journal, source_compiler, pkg_tree)

        compile_tree = EtsiVnfPkgContentTree()
        self.tree = EtsiVnfPkgContentTree(self.root_path)
        journal.event('Compiling additional ETSI files for: {0}'.format(self.source_config.full_name))
        source_compiler.compile_tree(self.tree.files_dir_path, compile_tree.files_dir_path)
        source_compiler.compile_file(self.tree.manifest_file_path, compile_tree.manifest_file_path)
        source_compiler.compile_tree(self.tree.definitions_dir_path, compile_tree.definitions_dir_path)

    def __add_root_descriptor(self, journal, source_compiler, pkg_tree):
        relative_root_descriptor_path = pkg_tree.root_descriptor_file_path
        source_compiler.compile_file(self.tree.descriptor_file_path, relative_root_descriptor_path)

    def __build_res_pkg(self, journal, source_compiler, pkg_tree):
        res_pkg_content_tree = BrentResourcePackageContentTree()
        relative_res_pkg_path = pkg_tree.gen_resource_package_file_path(self.source_config.full_name)
        full_res_pkg_path = source_compiler.make_file_path(relative_res_pkg_path)
        journal.event('Creating Resource package for {0}: {1}'.format(self.source_config.name, relative_res_pkg_path))
        with zipfile.ZipFile(full_res_pkg_path, "w") as res_pkg:
            included_items = [
                {'path': self.tree.definitions_path, 'alias': res_pkg_content_tree.definitions_path, 'required': True},
                {'path': self.tree.lifecycle_path, 'alias': res_pkg_content_tree.lifecycle_path, 'required': True}
            ]
            for included_item in included_items:
                self.__add_directory_if_exists(journal, res_pkg, included_item)

    def __add_directory_if_exists(self, journal, res_pkg, included_item):
        path = included_item['path']
        if os.path.exists(path):
            journal.event('Adding directory to Resource package: {0}'.format(os.path.basename(path)))
            res_pkg.write(path, arcname=included_item['alias'])
            rootlen = len(path) + 1
            for root, dirs, files in os.walk(path):
                for dirname in dirs:
                    full_path = os.path.join(root, dirname)
                    res_pkg.write(full_path, arcname=os.path.join(included_item['alias'], full_path[rootlen:]))
                for filename in files:
                    full_path = os.path.join(root, filename)
                    res_pkg.write(full_path, arcname=os.path.join(included_item['alias'], full_path[rootlen:]))
        else:
            if included_item['required']:
                msg = 'Required directory for Resource package not found: {0}'.format(path)
                journal.error_event(msg)
                raise handlers_api.SourceHandlerError(msg)
            else:
                journal.event('Skipping directory for Resource package, not found: {0}'.format(path))        