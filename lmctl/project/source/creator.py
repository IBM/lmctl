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
        self.params = {}

class CreateProjectRequest(CreateProjectBaseRequest):

    def __init__(self):
        super().__init__()
        self.target_location = './'
        self.version = '1.0'

class CreateAssemblyProjectRequest(CreateProjectRequest):

    def __init__(self):
        super().__init__()

class CreateTypeProjectRequest(CreateProjectRequest):

    def __init__(self):
        super().__init__()

class CreateResourceProjectRequest(CreateProjectRequest):

    def __init__(self):
        super().__init__()
        self.resource_manager = None

class CreateEtsiNsProjectRequest(CreateProjectRequest):

    def __init__(self):
        super().__init__()
        self.params = {'packaging':'csar'}

class CreateEtsiVnfProjectRequest(CreateProjectRequest):

    def __init__(self):
        super().__init__()
        self.params = {'packaging':'csar'}
        self.resource_manager = None

class SubprojectRequest(CreateProjectBaseRequest):

    def __init__(self):
        super().__init__()
        self.directory = None
        self.params = {}

class AssemblySubprojectRequest(SubprojectRequest):

    def __init__(self):
        super().__init__()

class TypeSubprojectRequest(SubprojectRequest):

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
        self.__param_values = {}

    def create(self):
        self.__param_values = {}
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
    
    def __param_key_from_name_chain(self, name_chain):
        key = ''
        for name in name_chain:
            if len(key)>0:
                key += '.'
            key += name
        return key

    def __build_config(self, journal):
        journal.section('Create Project Configuration')
        journal.event('Preparing configuration for {0}'.format(self.request.name))
        project_type = types.ASSEMBLY_PROJECT_TYPE
        resource_manager = None
        if isinstance(self.request, CreateResourceProjectRequest):
            project_type = types.RESOURCE_PROJECT_TYPE
            resource_manager = self.request.resource_manager
        elif isinstance(self.request, CreateTypeProjectRequest):
            project_type = types.TYPE_PROJECT_TYPE
        elif isinstance(self.request, CreateEtsiNsProjectRequest):
            project_type = types.ETSI_NS_PROJECT_TYPE
        elif isinstance(self.request, CreateEtsiVnfProjectRequest):
            project_type = types.ETSI_VNF_PROJECT_TYPE           
            resource_manager = self.request.resource_manager
        packaging = handlers_api.TGZ_PACKAGING
        if 'packaging' in self.request.params:
            packaging = self.request.params['packaging']
            if packaging != handlers_api.TGZ_PACKAGING and packaging != handlers_api.CSAR_PACKAGING:
                raise CreateError(str('packaging param value must be \'{0}\' or \'{1}\''.format(handlers_api.CSAR_PACKAGING, handlers_api.TGZ_PACKAGING)))
        try:
            param_values = handlers_api.SourceCreationParamValues(self.request.params)
            self.__param_values[self.request.name] = param_values
            subproject_entries = self.__build_subproject_entries(journal, self.request.subproject_requests, param_values, [self.request.name])
            project_config = projectconf.RootProjectConfig(projectconf.SCHEMA_2_0, self.request.name, self.request.version, project_type, resource_manager, subproject_entries, packaging=packaging)
            return project_config
        except projectconf.ProjectConfigError as e:
            raise CreateError(str(e)) from e
            
    def __build_subproject_entries(self, journal, subproject_requests, parent_param_values, name_chain):
        entries = []
        for subproject_request in subproject_requests:
            journal.event('Preparing configuration for {0}'.format(subproject_request.name))
            project_type = types.ASSEMBLY_PROJECT_TYPE
            resource_manager = None
            if isinstance(subproject_request, ResourceSubprojectRequest):
                project_type = types.RESOURCE_PROJECT_TYPE
                resource_manager = subproject_request.resource_manager
            elif isinstance(subproject_request, TypeSubprojectRequest):
                project_type = types.TYPE_PROJECT_TYPE
            nested_subproject_requests = subproject_request.subproject_requests
            param_values = handlers_api.SourceCreationParamValues(subproject_request.params, parent_param_values)
            new_name_chain = [*name_chain, subproject_request.name]
            param_key = self.__param_key_from_name_chain(new_name_chain)
            self.__param_values[param_key] = param_values
            nested_subproject_entries = self.__build_subproject_entries(journal, nested_subproject_requests, param_values, new_name_chain)
            new_entry = projectconf.SubprojectEntry(subproject_request.name, subproject_request.directory, project_type, resource_manager, nested_subproject_entries)
            entries.append(new_entry)
        return entries

    def __create_sources(self, journal, project_config):
        journal.section('Create Sources')
        try:
            self.__create_sources_for(journal, self.request.target_location, project_config, [project_config.name])
        except handlers_api.SourceCreationError as e:
            raise CreateError(str(e)) from e

    def __create_sources_for(self, journal, path, source_config, name_chain):
        journal.event('Creating sources for {0}'.format(source_config.name))
        tree = project_sources.ProjectBaseTree(path)
        source_creator = handlers_manager.source_creator_for(source_config)()
        param_key = self.__param_key_from_name_chain(name_chain)
        params = self.__param_values.get(param_key, None)
        source_request = handlers_api.SourceCreationRequest(path, source_config, params)
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
                self.__create_sources_for(journal, subproject_path, subproject, [*name_chain, subproject.name])
                journal.subproject_end(subproject.name)

    def __write_project_file(self, journal, project_config):
        journal.section('Create Profile File')
        project_tree = project_sources.ProjectTree(self.request.target_location)
        journal.event('Creating project file: {0}'.format(project_tree.project_file_path))
        with open(project_tree.project_file_path, 'w') as writer:
            yaml.dump(project_config.to_dict(), writer, default_flow_style=False, sort_keys=False)


class CreateSourcesOperation:

    def __init__(self, journal, creator, request):
        self.journal = journal
        self.creator = creator
        self.request = request