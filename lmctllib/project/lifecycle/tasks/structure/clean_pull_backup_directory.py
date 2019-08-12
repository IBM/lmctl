import os
import logging
import shutil
from ..tasks import ProjectLifecycleTask

class CleanBackupDirectory(ProjectLifecycleTask):
    """
    Cleans out the backup directory 
    """
    def __init__(self):
        super().__init__("Clean Backup Directory")

    def execute_work(self, tools, products):
        bkup_dir = self._get_project_tree().backupDirectory()
        if os.path.exists(bkup_dir):
            self._get_journal().add_text('Removing directory: {0}'.format(bkup_dir))
            shutil.rmtree(bkup_dir)
        self._get_journal().add_text('Creating directory: {0}'.format(bkup_dir))
        os.makedirs(bkup_dir)

        return self._return_passed()