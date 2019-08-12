import os

class VnfcsTree:
    """
    Describes the file structure from a directory that represents a holder of VNFC materials
    """
    def __init__(self, base):
        self.base = base

    def directory(self):
        """
        Returns:
          str: the root directory of this VNFCs tree
        """
        return self.base

    def vnfcDirectory(self, vnfc_name):
        """
        Returns:
          str: the path to the directory for contents of a single VNFC in this VNFC tree
        """
        return os.path.join(self.base, vnfc_name)
