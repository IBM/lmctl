import os

class DescriptorTree:
    """
    Describes the file structure from a directory that represents a holder of Descriptors for the projects NS/VNF
    """
    def __init__(self, base):
        self.base = base

    def directory(self):
        """
        Returns:
          str: the root directory of this Descriptor tree
        """
        return self.base

    def descriptorFile(self):
        """
        Returns:
          str: the path to the main assembly Descriptor
        """
        return os.path.join(self.base, 'assembly.yml')