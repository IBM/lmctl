import os
import logging
import distutils.dir_util
from ..tasks import ProjectLifecycleTask

class PackageServiceBehaviours(ProjectLifecycleTask):
    """
    Copies Service Behaviour sources to the packaging directory 
    """
    def __init__(self):
        super().__init__("Package Service Behaviour")
    
    def execute_work(self, tools, products):
        journal = self._get_journal()
        project_tree = self._get_project_tree()
        service_tests_path = project_tree.serviceBehaviour().directory()
        target_path = project_tree.build().packaging().serviceBehaviour().directory()
        if os.path.exists(service_tests_path):
            journal.add_text('Processing service tests found at {0}, copying to {1}'.format(service_tests_path, target_path))
            if not os.path.exists(os.path.dirname(target_path)):
                os.makedirs(os.path.dirname(target_path))
            distutils.dir_util.copy_tree(service_tests_path, target_path, 0)
            return self._return_passed()
        else:
            return self._return_skipped('No Service tests directory found at: {0}'.format(service_tests_path))