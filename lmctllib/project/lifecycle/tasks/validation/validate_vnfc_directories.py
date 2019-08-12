import os
import logging
from ..tasks import ProjectLifecycleTask

class ValidateVnfcDirectories(ProjectLifecycleTask):
    """
    Validate VNFC directories exist 
    """
    def __init__(self):
        super().__init__("Validate VNFC directories")
    
    def execute_work(self, tools, products):
        project = self._get_project()
        vnfc_definitions = project.vnfcs.definitions
        if not vnfc_definitions:
            return self._return_skipped('No VNFC definitions defined')
        fail = False
        failures = []
        for vnfc_id, definition in vnfc_definitions.items():
            self._get_journal().add_text('Validating VNFC definition: {0}'.format(vnfc_id))
            directory = definition.directory  
            full_path = self._get_project_tree().vnfcs().vnfcDirectory(directory)
            self._get_journal().add_text('Checking for directory {0}'.format(full_path))          
            if not os.path.exists(full_path):
                self._get_journal().add_text('VNFC {0} has directory defined that does not exist: {1}'.format(vnfc_id, full_path))
                fail = True
                failures.append(vnfc_id)
        if fail:
            return self._return_failure('There are VNFC definitions with directories that do not exist: {0}'.format(', '.join(failures)))
        return self._return_passed()
