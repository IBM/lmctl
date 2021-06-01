import os
import lmctl.files as files
import lmctl.utils.descriptors as descriptor_utils
import lmctl.project.mutate.descriptor as descriptor_mutations
import lmctl.project.source.config_references as refs
import lmctl.project.handlers.interface as handlers_api
from .common import LIFECYCLE_WORKSPACE
from lmctl.project.source.config import RootProjectConfig

class StagingTree(files.Tree):
    CONTAINS_DIR = 'Contains'

    def __init__(self, root_path):
        super().__init__(root_path)

    def __relative_child_staging_path(self):
        return self.relative_path(StagingTree.CONTAINS_DIR)

    @property
    def subproject_staging_path(self):
        return self.resolve_relative_path(self.__relative_child_staging_path())

    def gen_subproject_staging_path(self, subproject_name):
        return self.resolve_relative_path(self.__relative_child_staging_path(), subproject_name)

    def gen_subproject_staging_tree(self, subproject_name):
        return StagingTree(self.gen_subproject_staging_path(subproject_name))

class StageProcessError(Exception):
    pass

class StageProcess:

    def __init__(self, project, options, journal):
        self.project = project
        self.options = options
        self.journal = journal
        self.references = refs.ConfigReferences(self.project.config)

    def __create_staging_tree(self):
        staging_workspace = os.path.join(self.project.tree.root_path, LIFECYCLE_WORKSPACE, 'staging')
        return StagingTree(staging_workspace)

    def execute(self):
        staging_tree = self.__create_staging_tree()
        StageWorker(self.project, self.options, staging_tree, self.journal, self.references).work()
        return staging_tree

class StageWorker:

    def __init__(self, project, options, staging_tree, journal, references):
        self.project = project
        self.options = options
        self.journal = journal
        self.staging_tree = staging_tree
        self.references = references

    def work(self):
        self.__prepare_stage_directories()
        self.__stage_sources()
        self.__stage_child_projects()

    def __prepare_stage_directories(self):
        files.clean_directory(self.staging_tree.root_path)

    def __stage_sources(self):
        self.journal.section('Stage Sources')
        source_stager = SourceStager(self.journal, self.project.config, self.staging_tree.root_path, self.references)
        try:
            self.project.source_handler.stage_sources(self.journal, source_stager)
        except handlers_api.SourceHandlerError as e:
            raise StageProcessError(str(e)) from e
        self.__stage_tosca(source_stager)

    def __stage_tosca(self, source_stager):
        if isinstance(self.project.config, RootProjectConfig):
            tosca_metadata_path = self.project.tree.resolve_relative_path(handlers_api.TOSCA_METADATA)
            if os.path.exists(tosca_metadata_path):
                self.journal.event('Staging TOSCA-Metadata at {0}'.format(tosca_metadata_path))
                source_stager.stage_tree(self.project.tree.resolve_relative_path(handlers_api.TOSCA_METADATA), handlers_api.TOSCA_METADATA)
    
    def __stage_child_projects(self):
        subprojects = self.project.subprojects
        if len(subprojects) == 0:
            return
        for subproject in subprojects:
            self.journal.subproject(subproject.config.name)
            child_staging_tree = self.staging_tree.gen_subproject_staging_tree(subproject.config.directory)
            StageWorker(subproject, self.options, child_staging_tree, self.journal, self.references).work()
            self.journal.subproject_end(subproject.config.name)

class SourceStager:

    def __init__(self, journal, source_config, staging_path, references):
        self.journal = journal
        self.source_config = source_config
        self.staging_path = staging_path
        self.references = references

    def _join_path(self, base_path, relative_path):
        return os.path.join(base_path, relative_path)

    def _make_path(self, base_path, relative_path):
        full_path = self._join_path(base_path, relative_path)
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return full_path

    def stage_file(self, orig_path, relative_staging_path, mutator=None):
        target_path = self._make_path(self.staging_path, relative_staging_path)
        if mutator is None:
            files.copy_file(orig_path, target_path)
        else:
            with open(orig_path, 'r') as file:
                old_contents = file.read()
            new_contents = mutator.apply(old_contents)
            with open(target_path, 'w') as file:
                file.write(new_contents)
        return target_path

    def stage_tree(self, orig_path, relative_staging_path):
        target_path = self._make_path(self.staging_path, relative_staging_path)
        files.copy_tree(orig_path, target_path)
        return target_path

    def copy_staged_file(self, orig_path, relative_staging_path):
        src_path = self._make_path(self.staging_path, orig_path)
        target_path = self._make_path(self.staging_path, relative_staging_path)
        files.copy_file(src_path, target_path)
        return target_path

    def stage_descriptor(self, orig_path, relative_staging_path, is_template=False):
        staged_path = self.stage_file(orig_path, relative_staging_path)
        descriptor = descriptor_utils.DescriptorParser().read_from_file(staged_path)
        descriptor = descriptor_mutations.DescriptorStageMutator(self.source_config, self.references, self.journal).apply(descriptor, is_template=is_template)
        descriptor_utils.DescriptorParser().write_to_file(descriptor, staged_path)
        return staged_path