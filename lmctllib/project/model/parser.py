from .model import Project, VnfcDefinition, VnfcPackage, VnfcPackageExecution, Vnfcs

class ProjectParser:
    """
    Handles reading a raw dictionary contents of a project file into Project objects
    """
    def __init__(self, raw_project):
        if not raw_project:
            raise ValueError('raw_project must be defined')
        self.raw_project = raw_project

    def parse(self):
        self.projectName = self.__readProjectName()
        vnfcs = self.__readVnfcs()
        return Project(self.projectName, vnfcs)

    def __readProjectName(self):
        if 'name' not in self.raw_project:
            raise ProjectParsingException('Project is missing name')
        return self.raw_project['name']

    def __readVnfcs(self):
        definitions = {}
        packages = {}
        if 'vnfcs' in self.raw_project:
            vnfcs = self.raw_project['vnfcs']
            definitions = self.__readVnfcDefinitions(vnfcs)
            packages = self.__readVnfcPackages(vnfcs)   
        return Vnfcs(definitions, packages)

    def __readVnfcDefinitions(self, vnfcs):
        definitions = {}
        if 'definitions' in vnfcs:
            for vnfc_def_id, raw_vnfc_def in vnfcs['definitions'].items():
                vnfc_definition = self.__readVnfcDefinition(vnfc_def_id, raw_vnfc_def)
                definitions[vnfc_def_id] = vnfc_definition
        return definitions

    def __readVnfcDefinition(self, vnfc_def_id, raw_vnfc_def):
        if 'directory' in raw_vnfc_def:
            directory = raw_vnfc_def['directory']
        else:
            directory = vnfc_def_id
        return VnfcDefinition(vnfc_def_id, directory)

    def __readVnfcPackages(self, vnfcs):
        packages = {}
        if 'packages' in vnfcs:
            for vnfc_package_id, raw_vnfc_package in vnfcs['packages'].items():
                vnfc_package = self.__readVnfcPackage(vnfc_package_id, raw_vnfc_package)
                packages[vnfc_package_id] = vnfc_package
        return packages

    def __readVnfcPackage(self, vnfc_package_id, raw_vnfc_package):
        if 'packaging-type' in raw_vnfc_package:
            packaging_type = raw_vnfc_package['packaging-type']
        else:
            raise ProjectParsingException('VNFC package definition with id {0} is missing packaging-type'.format(vnfc_package_id))
        executions = self.__readVnfcPackageExecutions(vnfc_package_id, raw_vnfc_package)
        return VnfcPackage(vnfc_package_id, packaging_type, executions)

    def __readVnfcPackageExecutions(self, vnfc_package_id, raw_vnfc_package):
        executions = []
        if 'executions' in raw_vnfc_package:
            for raw_execution in raw_vnfc_package['executions']:
                execution =  self.__readVnfcPackageExecution(vnfc_package_id, raw_execution)
                executions.append(execution)
        return executions

    def __readVnfcPackageExecution(self, vnfc_package_id, raw_execution):
        if 'vnfc' in raw_execution:
            vnfc = raw_execution['vnfc']
        else:
            raise ProjectParsingException('VNFC package definition with id {0} includes an execution missing a vnfc value'.format(vnfc_package_id))
        return VnfcPackageExecution(vnfc)

class ProjectParsingException(Exception):
    pass