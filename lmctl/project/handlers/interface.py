import abc
import os
import shutil

############################
# Source Creator Exceptions
############################

class SourceCreationError(Exception):
    pass

############################
# Source Creators
############################

class SourceCreationRequest:

    def __init__(self, target_path, source_config):
        self.target_path = target_path
        self.source_config = source_config

class SourceCreator(abc.ABC):

    def __init__(self):
        pass

    def _execute_file_ops(self, file_ops, path, journal):
        for file_op in file_ops:
            file_op.execute(path, journal)

    def create_source(self, journal, source_request):
        pass

class ResourceSourceCreatorDelegate(abc.ABC):

    def __init__(self):
        pass

    def create_source(self, journal, source_request, file_ops_executor):
        pass

EXISTING_FAIL = 'fail'
EXISTING_OVERWRITE = 'overwrite'
EXISTING_IGNORE = 'ignore'

class CreateFileOp:

    def __init__(self, relative_file_path, content=None, on_existing=EXISTING_FAIL):
        self.relative_file_path = relative_file_path
        self.content = content
        self.on_existing = on_existing

    def execute(self, path, journal):
        full_path = os.path.join(path, self.relative_file_path)
        if os.path.exists(full_path):
            if self.on_existing == EXISTING_FAIL:
                raise SourceCreationError('File already exists: {0}'.format(full_path))
            elif self.on_existing == EXISTING_IGNORE:
                journal.event('Not creating file as it already exists: {0}'.format(full_path))
                return
            else:
                journal.event('Replacing file: {0}'.format(full_path))
                os.remove(full_path)
        else:
            journal.event('Creating file: {0}'.format(full_path))
        dir_name = os.path.dirname(full_path)
        os.makedirs(dir_name, exist_ok=True)
        with open(full_path, 'w') as writer:
            writer.write(self.content)


class CreateDirectoryOp:

    def __init__(self, relative_dir_path, on_existing=EXISTING_FAIL):
        self.relative_dir_path = relative_dir_path
        self.on_existing = on_existing

    def execute(self, path, journal):
        full_path = os.path.join(path, self.relative_dir_path)
        if os.path.exists(full_path):
            if self.on_existing == EXISTING_FAIL:
                raise SourceCreationError('Directory already exists: {0}'.format(full_path))
            elif self.on_existing == EXISTING_IGNORE:
                journal.event('Not creating directory as it already exists: {0}'.format(full_path))
                return
            else:
                journal.event('Replacing directory (and all contents): {0}'.format(full_path))
                shutil.rmtree(full_path)
        else:
            journal.event('Creating directory: {0}'.format(full_path))
        os.makedirs(full_path)


############################
# Source Handler Exceptions
############################

class SourceHandlerError(Exception):
    pass

class InvalidSourceError(SourceHandlerError):
    pass

class InvalidSourceTypeError(SourceHandlerError):
    pass

class PullSourceError(SourceHandlerError):
    pass

############################
# Source Handlers
############################

class SourceHandler(abc.ABC):

    def __init__(self, root_path, source_config):
        self.root_path = root_path
        self.source_config = source_config

    @abc.abstractmethod
    def validate_sources(self, journal, source_validator):
        pass

    @abc.abstractmethod
    def stage_sources(self, journal, source_stager):
        pass

    @abc.abstractmethod
    def build_staged_source_handler(self, staging_path):
        pass

    @abc.abstractmethod
    def pull_sources(self, journal, backup_tool, env_sessions, references):
        pass

    @abc.abstractmethod
    def list_elements(self, journal, element_type):
        pass

ELEMENT_TYPE_TESTS = 'tests'

class StagedSourceHandler(abc.ABC):

    def __init__(self, root_path, source_config):
        self.root_path = root_path
        self.source_config = source_config

    @abc.abstractmethod
    def compile_sources(self, journal, source_compiler):
        pass


class ResourceSourceHandlerDelegate(abc.ABC):

    def __init__(self, root_path, source_config):
        if root_path is None:
            raise ValueError('root_path must be provided for a source handler delegate')
        self.root_path = root_path
        self.source_config = source_config

    @abc.abstractmethod
    def validate_sources(self, journal, source_validator):
        pass

    @abc.abstractmethod
    def stage_sources(self, journal, source_stager):
        pass

    @abc.abstractmethod
    def build_staged_source_delegate(self, staging_path):
        pass

    @abc.abstractmethod
    def get_main_descriptor(self):
        pass


class ResourceStagedSourceHandlerDelegate(abc.ABC):

    def __init__(self, root_path, source_config):
        if root_path is None:
            raise ValueError('root_path must be provided for a source handler delegate')
        self.root_path = root_path
        self.source_config = source_config

    @abc.abstractmethod
    def compile_sources(self, journal, source_compiler):
        pass

############################
# Content Exceptions
############################

class ContentHandlerError(Exception):
    pass

class InvalidContentTypeError(ContentHandlerError):
    pass

############################
# Content Handlers
############################

class PkgContentHandler(abc.ABC):

    def __init__(self, root_path, meta):
        self.root_path = root_path
        self.meta = meta

    @abc.abstractmethod
    def validate_content(self, journal, env_sessions):
        pass

    @abc.abstractmethod
    def push_content(self, journal, env_sessions):
        pass

    @abc.abstractmethod
    def execute_tests(self, journal, env_sessions, selected_tests):
        pass


class ResourceContentHandlerDelegate(abc.ABC):

    def __init__(self, root_path, meta):
        if root_path is None:
            raise ValueError('root_path must be provided for a source handler delegate')
        self.root_path = root_path
        self.meta = meta

    @abc.abstractmethod
    def validate_content(self, journal, env_sessions):
        pass

    @abc.abstractmethod
    def push_content(self, journal, env_sessions):
        pass
