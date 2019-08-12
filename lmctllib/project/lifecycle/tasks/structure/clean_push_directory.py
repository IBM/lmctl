import os
import logging
import shutil
from ..tasks import ProjectLifecycleTask

class CleanPushDirectory(ProjectLifecycleTask):
    """
    Cleans out the push workspace
    """
    def __init__(self):
        super().__init__("Clean Push Directory")

    def execute_work(self, tools, products):
        push_dir = self._get_project_tree().pushWorkspace().directory()
        if os.path.exists(push_dir):
            self._get_journal().add_text('Removing directory: {0}'.format(push_dir))
            shutil.rmtree(push_dir)
        self._get_journal().add_text('Creating directory: {0}'.format(push_dir))
        os.makedirs(push_dir)
        return self._return_passed()