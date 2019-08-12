import os
from .build_resources_tree import BuildResourcesTree
from .package_tree import PackageTree

class BuildTree:
    """
    Describes the file structure from a directory that represents the working directory of an Lmctl build
    """
    def __init__(self, base):
        self.base = base
        self.resources_tree = BuildResourcesTree(os.path.join(self.base, 'resources'))
        self.packaging_tree = PackageTree(os.path.join(self.base, 'packaging'))

    def directory(self):
        """
        Returns:
          str: the root directory of this Build tree
        """
        return self.base

    def resources(self):
        """
        Returns:
          BuildResourcesTree: the remaining tree from the context of the Resources directory in this Build tree
        """
        return self.resources_tree

    def packaging(self):
        """
        Returns:
          PackageTree: the remaining tree from the context of the Package directory in this Build tree
        """
        return self.packaging_tree

    def packageFile(self, package_name):
        """
        Returns:
          str: the path to the final Package file
        """
        return os.path.join(self.base, '{0}.tgz'.format(package_name))

    def packageContentFile(self):
        """
        Returns:
          str: the path to the Content package file (a part of the final Package)
        """
        return os.path.join(self.base, 'content.tgz')
