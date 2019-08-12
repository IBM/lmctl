import os

class ServiceBehaviourTree:
    """
    Describes the file structure from a directory that represents a holder of Service Behaviour materials
    """
    def __init__(self, base):
        self.base = base

    def directory(self):
        """
        Returns:
          str: the root directory of this Service Behaviour tree
        """
        return self.base

    def testsDirectory(self):
        """
        Returns:
          str: the path to the Tests directory of this Service Behaviour tree
        """
        return os.path.join(self.base, 'Tests')
    
    def templatesDirectory(self):
        """
        Returns:
          str: the path to the Templates directory of this Service Behaviour tree
        """
        return os.path.join(self.base, 'Templates')

    def runtimeDirectory(self):
        """
        Returns:
          str: the path to the Runtime directory of this Service Behaviour tree
        """
        return os.path.join(self.base, 'Runtime')
