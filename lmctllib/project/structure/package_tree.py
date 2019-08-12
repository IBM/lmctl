import os
from .vnfcs_tree import VnfcsTree
from .service_behaviour_tree import ServiceBehaviourTree
from .descriptor_tree import DescriptorTree

class PackageTree:
    """
    Describes the file structure from a directory that represents the contents directory of a NS/VNF package
    """
    def __init__(self, base):
        self.base = base
        self.vnfcs_tree = VnfcsTree(os.path.join(self.base, 'VNFCs'))
        self.service_behaviour_tree = ServiceBehaviourTree(os.path.join(self.base, 'Behaviour'))
        self.descriptor_tree = DescriptorTree(os.path.join(self.base, 'Descriptor'))
       
    def directory(self):
        """
        Returns:
          str: the root directory of this Package tree
        """
        return self.base

    def serviceDescriptor(self):
        """
        Returns:
          DescriptorTree: the remaining tree from the context of the Descriptor directory in this Package tree
        """
        return self.descriptor_tree

    def vnfcs(self):
        """
        Returns:
          VnfcsTree: the remaining tree from the context of the Vnfcs directory in this Package tree
        """
        return self.vnfcs_tree

    def serviceBehaviour(self):
        """
        Returns:
          ServiceBehaviourTree: the remaining tree from the context of the Service Behaviour directory in this Package tree
        """
        return self.service_behaviour_tree
