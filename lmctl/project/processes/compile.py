import os
import lmctl.files as files
import lmctl.project.handlers.interface as handlers_api
from lmctl.project.package.core import ExpandedPkgTree
from .common import LIFECYCLE_WORKSPACE

class CompileProcessError(Exception):
    pass

class CompileProcess:

    def __init__(self, project, options, staging_tree, journal):
        self.project = project
        self.options = options
        self.journal = journal
        self.staging_tree = staging_tree

    def __create_content_tree(self):
        compile_workspace = os.path.join(self.project.tree.root_path, LIFECYCLE_WORKSPACE, 'compile')
        return ExpandedPkgTree(compile_workspace)

    def execute(self):
        content_tree = self.__create_content_tree()
        CompileWorker(self.project, self.options, self.staging_tree, content_tree, self.journal).work()
        return content_tree


class CompileWorker:

    def __init__(self, project, options, staging_tree, content_tree, journal):
        self.project = project
        self.options = options
        self.journal = journal
        self.staging_tree = staging_tree
        self.content_tree = content_tree

    def work(self):
        self.__prepare_compile_directories()
        self.__compile_sources()
        self.__compile_child_projects()

    def __prepare_compile_directories(self):
        files.clean_directory(self.content_tree.root_path)

    def __compile_sources(self):
        self.journal.section('Compile Package')
        try:
            staged_source_handler = self.project.source_handler.build_staged_source_handler(self.staging_tree.root_path)
            source_compiler = SourceCompiler(self.journal, self.project.config, self.content_tree.root_path)
            staged_source_handler.compile_sources(self.journal, source_compiler)
        except handlers_api.SourceHandlerError as e:
            raise CompileProcessError(str(e)) from e
        self.__compile_tosca(source_compiler)

    def __compile_tosca(self, source_compiler):
        tosca_metadata_path = self.staging_tree.resolve_relative_path(handlers_api.TOSCA_METADATA)
        if os.path.exists(tosca_metadata_path):
            source_compiler.compile_tree(tosca_metadata_path, handlers_api.TOSCA_METADATA)
        
    def __compile_child_projects(self):
        subprojects = self.project.subprojects
        if len(subprojects) == 0:
            return
        for subproject in subprojects:
            self.journal.subproject(subproject.config.name)
            child_staging_tree = self.staging_tree.gen_subproject_staging_tree(subproject.config.directory)
            child_content_tree = self.content_tree.gen_child_content_tree(subproject.config.directory)
            CompileWorker(subproject, self.options, child_staging_tree, child_content_tree, self.journal).work()
            self.journal.subproject_end(subproject.config.name)

class SourceCompiler:

    def __init__(self, journal, source_config, compile_path):
        self.journal = journal
        self.source_config = source_config
        self.compile_path = compile_path

    def _join_path(self, base_path, relative_path):
        return os.path.join(base_path, relative_path)

    def _make_path(self, base_path, relative_path):
        full_path = self._join_path(base_path, relative_path)
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return full_path

    def compile_tree(self, orig_path, relative_compile_path=None):
        if relative_compile_path is None:
            compile_path = self.compile_path
        else:
            compile_path = self._make_path(self.compile_path, relative_compile_path)
        files.copy_tree(orig_path, compile_path)

    def make_file_path(self, relative_compile_path):
        return self._make_path(self.compile_path, relative_compile_path)

    def compile_file(self, orig_path, relative_compile_path):
        target_path = self._make_path(self.compile_path, relative_compile_path)
        files.copy_file(orig_path, target_path)

