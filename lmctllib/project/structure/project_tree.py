import os
from .build_tree import BuildTree
from .vnfcs_tree import VnfcsTree
from .service_behaviour_tree import ServiceBehaviourTree
from .descriptor_tree import DescriptorTree
from .package_wrapper_tree import PackageWrapperTree

class ProjectTree:
    """
    Describes the file structure from a directory that represents the Project. 
    In essence, you may instantiate a ProjectTree in a directory that you believe represents a Project, then use the methods on this tree (and returned sub-trees) to navigate the contents. 
    The aim is to prevent hard-coded paths in code based around the directory structure of a Project.
    """
    def __init__(self, base):
        self.base = base
        self.workspace = '_lmctl'
        self.build_tree = BuildTree(os.path.join(self.base, self.workspace, '_build'))
        self.vnfcs_tree = VnfcsTree(os.path.join(self.base, 'VNFCs'))
        self.push_package_tree = PackageWrapperTree(os.path.join(self.base, self.workspace, '_pushpkg'))
        self.service_behaviour_tree = ServiceBehaviourTree(os.path.join(self.base, 'Behaviour'))
        self.descriptor_tree = DescriptorTree(os.path.join(self.base, 'Descriptor'))
       
    def directory(self):
        """
        Returns:
          str: the root directory of this Project tree
        """
        return self.base

    def backupDirectory(self):
        """
        Returns:
          str: the path to the backup directory of this Project
        """
        return os.path.join(self.base, self.workspace, '_prepull')

    def backup(self):
        """
        Returns:
          ProjectTree: the remaining tree from the context of the backup directory in this Project
        """
        return ProjectTree(self.backupDirectory())

    def projectFile(self):
        """
        Returns:
          str: the path to the lmctl project file in this Project
        """
        return os.path.join(self.base, 'lmproject.yml')

    def build(self):
        """
        Returns:
          BuildTree: the remaining tree from the context of the build directory in this Project
        """
        return self.build_tree

    def pushWorkspace(self):
        """
        Returns:
          PackageWrapperTree: the remaining tree from the context of the package push directory in this Project
        """
        return self.push_package_tree

    def vnfcs(self):
        """
        Returns:
          VnfcsTree: the remaining tree from the context of the VNFCs directory in this Project
        """
        return self.vnfcs_tree
    
    def serviceBehaviour(self):
        """
        Returns:
          ServiceBehaviourTree: the remaining tree from the context of the Service Behaviour directory in this Project
        """
        return self.service_behaviour_tree

    def serviceDescriptor(self):
        """
        Returns:
          DescriptorTree: the remaining tree from the context of the Descriptor directory in this Project
        """
        return self.descriptor_tree
