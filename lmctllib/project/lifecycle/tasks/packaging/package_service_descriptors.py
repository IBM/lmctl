import os
import shutil
from ..tasks import ProjectLifecycleTask

class PackageServiceDescriptor(ProjectLifecycleTask):
    """
    Copies Service Descriptor sources to the packaging directory 
    """
    def __init__(self):
        super().__init__("Package Service Descriptor")

    def execute_work(self, tools, products):
        journal = self._get_journal()
        service_descriptor_path = self._get_project_tree().serviceDescriptor().descriptorFile()
        target_path = self._get_project_tree().build().packaging().serviceDescriptor().descriptorFile()
        if os.path.exists(service_descriptor_path):
            journal.add_text('Processing service descriptor found at {0}, copying to {1}'.format(service_descriptor_path, target_path))
            if not os.path.exists(os.path.dirname(target_path)):
                os.makedirs(os.path.dirname(target_path))
            shutil.copy2(service_descriptor_path, target_path)
            return self._return_passed()
        else:
            return self._return_failure('No Service descriptor found at: {0}'.format(service_descriptor_path))