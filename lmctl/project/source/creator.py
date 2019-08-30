import os
import yaml
from lmctl.project.journal import ProjectJournal
import lmctl.project.types as types
import lmctl.project.source.config as projectconf
import lmctl.project.source.core as project_sources
import lmctl.project.handlers.manager as handlers_manager
import lmctl.project.handlers.interface as handlers_api

class CreateProjectBaseRequest:

    def __init__(self):
        self.name = None
        self.subproject_requests = []

class CreateProjectRequest(CreateProjectBaseRequest):

    def __init__(self):
        super().__init__()
        self.target_location = './'
        self.version = '1.0'

class CreateAssemblyProjectRequest(CreateProjectRequest):

    def __init__(self):
        super().__init__()

class CreateResourceProjectRequest(CreateProjectRequest):

    def __init__(self):
        super().__init__()
        self.resource_manager = None

class SubprojectRequest(CreateProjectBaseRequest):

    def __init__(self):
        super().__init__()
        self.directory = None


class AssemblySubprojectRequest(SubprojectRequest):

    def __init__(self):
        super().__init__()


class ResourceSubprojectRequest(SubprojectRequest):

    def __init__(self):
        super().__init__()
        self.resource_manager = None


class CreateError(Exception):
    pass


class CreateOptions:

    def __init__(self):
        self.journal_consumer = None

class ProjectCreator:

    def __init__(self, request, options):
        self.request = request
        self.options = options

    def create(self):
        journal = ProjectJournal(self.options.journal_consumer)
        self.__validate_request()
        self.__create_project_directory(journal)
        project_config = self.__build_config(journal)
        self.__create_sources(journal, project_config)
        self.__write_project_file(journal, project_config)

    def __create_project_directory(self, journal):
        journal.section('Create Project Directory')
        if not os.path.exists(self.request.target_location):
            journal.event('Creating directory: {0}'.format(self.request.target_location))
            os.makedirs(self.request.target_location)
        else:
            journal.event('Directory {0} already exists'.format(self.request.target_location))
        
    def __validate_request(self):
        if not self.request.target_location:
            raise CreateError('No target location for project was provided')
        project_tree = project_sources.ProjectTree(self.request.target_location)
        if(os.path.exists(project_tree.project_file_path)):
            raise CreateError('Target location given seems to already contain a project (there is an existing project file: {0})'.format(project_tree.project_file_path))
    
    def __build_config(self, journal):
        journal.section('Create Project Configuration')
        journal.event('Preparing configuration for {0}'.format(self.request.name))
        project_type = types.ASSEMBLY_PROJECT_TYPE
        resource_manager = None
        if isinstance(self.request, CreateResourceProjectRequest):
            project_type = types.RESOURCE_PROJECT_TYPE
            resource_manager = self.request.resource_manager
        try:
            subproject_entries = self.__build_subproject_entries(journal, self.request.subproject_requests)
            project_config = projectconf.RootProjectConfig(projectconf.SCHEMA_2_0, self.request.name, self.request.version, project_type, resource_manager, subproject_entries)
            return project_config
        except projectconf.ProjectConfigError as e:
            raise CreateError(str(e)) from e
            
    def __build_subproject_entries(self, journal, subproject_requests):
        entries = []
        for subproject_request in subproject_requests:
            journal.event('Preparing configuration for {0}'.format(subproject_request.name))
            project_type = types.ASSEMBLY_PROJECT_TYPE
            resource_manager = None
            if isinstance(subproject_request, ResourceSubprojectRequest):
                project_type = types.RESOURCE_PROJECT_TYPE
                resource_manager = subproject_request.resource_manager
            nested_subproject_requests = subproject_request.subproject_requests
            nested_subproject_entries = self.__build_subproject_entries(journal, nested_subproject_requests)
            entries.append(projectconf.SubprojectEntry(subproject_request.name, subproject_request.directory, project_type, resource_manager, nested_subproject_entries))
        return entries

    def __create_sources(self, journal, project_config):
        journal.section('Create Sources')
        try:
            self.__create_sources_for(journal, self.request.target_location, project_config)
        except handlers_api.SourceCreationError as e:
            raise CreateError(str(e)) from e

    def __create_sources_for(self, journal, path, source_config):
        journal.event('Creating sources for {0}'.format(source_config.name))
        tree = project_sources.ProjectBaseTree(path)
        source_creator = handlers_manager.source_creator_for(source_config)()
        source_request = handlers_api.SourceCreationRequest(path, source_config)
        source_creator.create_source(journal, source_request)
        subprojects = source_config.subprojects
        if len(subprojects) > 0:
            subprojects_path = tree.child_projects_path
            if not os.path.exists(subprojects_path):
                journal.event('Creating directory for subprojects: {0}'.format(subprojects_path))
                os.makedirs(subprojects_path)
            for subproject in subprojects:
                journal.subproject(subproject.name)
                subproject_path = tree.gen_child_project_path(subproject.directory)
                self.__create_sources_for(journal, subproject_path, subproject)
                journal.subproject_end(subproject.name)

    def __write_project_file(self, journal, project_config):
        journal.section('Create Profile File')
        project_tree = project_sources.ProjectTree(self.request.target_location)
        journal.event('Creating project file: {0}'.format(project_tree.project_file_path))
        with open(project_tree.project_file_path, 'w') as writer:
            yaml.dump(project_config.to_dict(), writer, default_flow_style=False, sort_keys=False)