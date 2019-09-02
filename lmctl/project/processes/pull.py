import os
import lmctl.files as files
import lmctl.project.handlers.interface as handlers_api
from .common import LIFECYCLE_WORKSPACE
import lmctl.project.source.config_references as refs

class BackupTree(files.Tree):
    CONTAINS_DIR = 'Contains'

    def __init__(self, root_path):
        super().__init__(root_path)

    def __relative_child_backup_path(self):
        return self.relative_path(BackupTree.CONTAINS_DIR)

    @property
    def subproject_backup_path(self):
        return self.resolve_relative_path(self.__relative_child_backup_path())

    def gen_subproject_backup_path(self, subproject_name):
        return self.resolve_relative_path(self.__relative_child_backup_path(), subproject_name)

    def gen_subproject_backup_tree(self, subproject_name):
        return BackupTree(self.gen_subproject_backup_path(subproject_name))

class PullProcessError(Exception):
    pass

class PullProcess:

    def __init__(self, project, options, journal, env_sessions):
        self.project = project
        self.options = options
        self.journal = journal
        self.env_sessions = env_sessions
        self.references = refs.ConfigReferences(self.project.config)

    def __create_backup_tree(self):
        backup_path = os.path.join(self.project.tree.root_path, LIFECYCLE_WORKSPACE, 'pre_pull_backup')
        return BackupTree(backup_path)

    def execute(self):
        backup_tree = self.__create_backup_tree()
        return PullWorker(self.project, self.options, backup_tree, self.journal, self.env_sessions, self.references).work()

class PullWorker:

    def __init__(self, project, options, backup_tree, journal, env_sessions, references):
        self.project = project
        self.options = options
        self.journal = journal
        self.backup_tree = backup_tree
        self.env_sessions = env_sessions
        self.references = references

    def work(self):
        self.__pull_sources()
        self.__pull_child_projects()

    def __pull_sources(self):
        self.journal.section('Pull Sources')
        backup_tool = SourceBackupTool(self.journal, self.project.config, self.backup_tree.root_path)
        try:
            self.project.source_handler.pull_sources(self.journal, backup_tool, self.env_sessions, self.references)
        except handlers_api.SourceHandlerError as e:
            raise PullProcessError(str(e)) from e
        
    def __pull_child_projects(self):
        subprojects = self.project.subprojects
        if len(subprojects) == 0:
            return
        for subproject in subprojects:
            self.journal.subproject(subproject.config.name)
            child_backup_tree = self.backup_tree.gen_subproject_backup_tree(subproject.config.directory)
            PullWorker(subproject, self.options, child_backup_tree, self.journal, self.env_sessions, self.references).work()
            self.journal.subproject_end(subproject.config.name)

class SourceBackupTool:

    def __init__(self, journal, source_config, backup_path):
        self.journal = journal
        self.source_config = source_config
        self.backup_path = backup_path

    def _join_path(self, base_path, relative_path):
        return os.path.join(base_path, relative_path)

    def _make_path(self, base_path, relative_path):
        full_path = self._join_path(base_path, relative_path)
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return full_path

    def backup_file(self, orig_path, relative_backup_path):
        target_path = self._make_path(self.backup_path, relative_backup_path)
        files.copy_file(orig_path, target_path)

    def backup_tree(self, orig_path, relative_backup_path=None):
        if relative_backup_path is None:
            backup_path = self.backup_path
        else:
            backup_path = self._make_path(self.backup_path, relative_backup_path)
        files.copy_tree(orig_path, backup_path)

        