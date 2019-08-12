import os
from .package_tree import PackageTree

class PackageWrapperTree:
    """
    Describes the file structure from a directory that represents the NS/VNF package
    """
    def __init__(self, base):
        self.base = base
        self.content_tree = PackageTree(os.path.join(self.base, 'content'))

    def directory(self):
        """
        Returns:
          str: the root directory of this Package Wrapper tree
        """
        return self.base

    def projectFile(self):
        """
        Returns:
          str: the path to the lmctl project file in this Package tree
        """
        return os.path.join(self.base, 'lmproject.yml')

    def contentFile(self):
        """
        Returns:
          str: the path to the contents file in this Package tree
        """
        return os.path.join(self.base, 'content.tgz')

    def content(self):
        """
        Returns:
          PackageTree: the remaining tree from the context of the expanded contents directory in this Package Wrapper tree
        """
        return self.content_tree
