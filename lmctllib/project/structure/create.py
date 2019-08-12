import os
import logging
import yaml
import lmctllib.utils.descriptors as descriptor_utils
from .project_tree import ProjectTree

logger = logging.getLogger(__name__)

class ProjectCreator:
    """
    Creates the starter directories and files for a new Lmctl Project
    """
    def __init__(self):
        pass

    def create(self, request):
        if not request.target_location:
            logger.error('Error: No target_location provided')
            exit(1)
        if not os.path.exists(request.target_location):
            os.makedirs(request.target_location)

        logger.info('Creating project at: {0}'.format(request.target_location))

        project_tree = ProjectTree(request.target_location)
        if(os.path.exists(project_tree.projectFile())):
            logger.error('Error: Target location given seems to already contain a Project (there is a project file: {0})'.format(project_tree.projectFile()))
            exit(1)

        if request.serviceType == 'VNF':
            self.__createVNF(request, project_tree)
        else:
            self.__createNS(request, project_tree)
        self.__createServiceDescriptor(request, project_tree)

        self.__createProjectFile(request, project_tree)

        logger.info('Project created successfully!')

    def __createProjectFile(self, request, project_tree):
        project_init = ProjectFileCreator(project_tree.directory())
        project_init.makeFile()

    def __createNS(self, request, project_tree):
        logger.info('Service Type: NS, creating Service Behaviour directory tree')
        os.makedirs(project_tree.serviceBehaviour().directory())
        os.makedirs(project_tree.serviceBehaviour().testsDirectory())
        os.makedirs(project_tree.serviceBehaviour().templatesDirectory())
        os.makedirs(project_tree.serviceBehaviour().runtimeDirectory())

    def __createVNF(self, request, project_tree):
        logger.info('Service Type: VNF, creating VNFCs directory')
        os.makedirs(project_tree.vnfcs().directory())
        for vnfc in request.vnfcs:
            logger.info('Creating directory for VNFC: {0}'.format(vnfc))
            os.makedirs(project_tree.vnfcs().vnfcDirectory(vnfc))

    def __createServiceDescriptor(self, request, project_tree):
        os.makedirs(project_tree.serviceDescriptor().directory())
        project_name = os.path.basename(request.target_location)
        if not project_name:
            project_name = os.path.basename(os.getcwd())
        descriptor = descriptor_utils.DescriptorModel({})
        descriptor_name = request.name
        if not descriptor_name:
            descriptor_name = project_name
        version = request.version
        if not version:
            version = '1.0'
        descriptor.setName('assembly', descriptor_name, version)
        logger.info('Creating service descriptor with name: {0}'.format(descriptor.getName()))
        with open(project_tree.serviceDescriptor().descriptorFile(), 'w') as descriptor_file:
            yaml.dump(descriptor.raw_descriptor, descriptor_file, default_flow_style=False)

class ProjectCreateRequest:

    def __init__(self):
        self.target_location = './'
        self.name = ''
        self.version = '1.0'
        self.serviceType = 'NS'
        self.vnfcs = []

class ProjectFileCreator:
    """
    Creates a lmctl project file based on the structure of a target directory. 
    When producing the project file, sub-directory structure will be checked for VNFCs (based on the structure dictated by the ProjectTree class) and include a vnfc-definition for each one found
    """
    def __init__(self, project_path):
        self.project_path = project_path

    def makeFile(self):
        project = self.make()
        project_tree = ProjectTree(self.project_path)
        project_file_path = project_tree.projectFile()
        with open(project_file_path, 'w') as project_file:
            yaml.dump(project, project_file, default_flow_style=False)

    def make(self):
        logger.info('Initiating project file at: {0}'.format(self.project_path))
        project_name = os.path.basename(self.project_path)
        if not project_name:
            project_name = os.path.basename(os.getcwd())
        logger.info('Project name calculated as: {0}'.format(project_name))
        project_tree = ProjectTree(self.project_path)
        vnfc_definitions = {}
        packages = {}

        vnfcs_dir = project_tree.vnfcs().directory()
        if os.path.exists(vnfcs_dir):
            for file in os.listdir(vnfcs_dir):
                if os.path.isdir(os.path.join(vnfcs_dir, file)):
                    vnfc_definitions[file] = {'directory': file}
        else:
            logger.info('Skipping VNFCs definitions as there is no VNFCs directory: {0}'.format(vnfcs_dir))

        if vnfc_definitions:
            package_identifer = 'ansible-rm-vnfcs'
            packging_type = 'ansible-rm'
            package_executions = []
            for vnfc_identifer, vnfc_def in vnfc_definitions.items():
                package_execution = {'vnfc': vnfc_identifer}
                package_executions.append(package_execution)
            packages[package_identifer] = {'packaging-type': packging_type, 'executions': package_executions}
        
        return {'name': project_name, 'vnfcs': {'definitions': vnfc_definitions, 'packages': packages}}           