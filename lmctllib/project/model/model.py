
class VnfcPackageExecution:
    """
    Configuration of single execution of a VNFC packaging job. 
    Inidicates the VNFC definition this execution is for
    """
    def __init__(self, vnfc):
        if not vnfc:
            raise ValueError('vnfc must be defined')
        self.vnfc = vnfc

class VnfcPackage:
    """
    Configuration of a VNFC packaging job on a Project. 
    This indicates how VNFC(s) are packaged and deployed to a Resource Manager
    """
    def __init__(self, identifier: str, packaging_type: str, executions: list = []):
        if not identifier:
            raise ValueError('identifier must be defined')
        self.identifier = identifier
        if not packaging_type:
            raise ValueError('packaging-type must be defined')
        self.packaging_type = packaging_type
        self.executions = executions

class VnfcDefinition:
    """
    Configuration of a VNFC belonging to a Project
    """
    def __init__(self, identifier, directory):
        if not identifier:
            raise ValueError('identifier must be defined')
        self.identifier = identifier
        if not directory:
            raise ValueError('directory must be defined')
        self.directory = directory


class Vnfcs:
    """
    Configuration VNFC definitions and packaging in a Project
    """
    def __init__(self, definitions=None, packages=None):
        if definitions is None:
            definitions = {}
        if packages is None:
            packages = {}
        self.definitions = definitions
        self.packages = packages

class Project:
    """
    Handles configuration of an Lmctl project
    """
    def __init__(self, name, vnfcs: Vnfcs):
        if not name:
            raise ValueError('name must be defined')
        self.name = name
        if vnfcs is None:
            vnfcs = {}
        self.vnfcs = vnfcs
