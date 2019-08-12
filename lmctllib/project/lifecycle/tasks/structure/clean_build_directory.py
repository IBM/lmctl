import os
import shutil
from ..tasks import ProjectLifecycleTask

class CleanBuildDirectory(ProjectLifecycleTask):
    """
    Clears out the build directory 
    """
    def __init__(self):
        super().__init__("Clean Build Directory")

    def execute_work(self, tools, products):
        build_dir = self._get_project_tree().build().directory()
        if os.path.exists(build_dir):
            self._get_journal().add_text('Removing directory: {0}'.format(build_dir))
            shutil.rmtree(build_dir)
        self._get_journal().add_text('Creating directory: {0}'.format(build_dir))
        os.makedirs(build_dir)
        return self._return_passed()