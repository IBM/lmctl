import os
import tarfile
import lmctllib.pipeline as pipeline
import lmctllib.journal as journal
from ..tasks import ProjectLifecycleTask, PRODUCT_PKG_PATH
from .packaging import establishBuiltPackageName

class ExtractBuildPackage(ProjectLifecycleTask):
    """
    Extracts the contents of a NS/VNF package to the "push" workspace 
    """
    def __init__(self):
        super().__init__("Extract Build Package")

    def execute_work(self, tools: pipeline.TaskTools, products: pipeline.TaskProducts):
        journal = self._get_journal()
        if products.has_value(PRODUCT_PKG_PATH):
            pkg_path = products.get_value(PRODUCT_PKG_PATH)
        else: 
            pkg_name = establishBuiltPackageName(self._get_project_name(), self._get_project_tree())
            pkg_path = self._get_project_tree().build().packageFile(pkg_name)
        journal.add_text('Extracting package: {0}'.format(pkg_path))
        extraction_dir = self._get_project_tree().pushWorkspace().directory()
        if os.path.exists(pkg_path):
            with tarfile.open(pkg_path, mode='r:gz') as pkg_tar:
                pkg_tar.extractall(extraction_dir)
        else:
            msg = 'No package found at {0}'.format(pkg_path)
            return self._return_failure(msg)

        inner_content_pkg_path = self._get_project_tree().pushWorkspace().contentFile()
        extracted_content_path = self._get_project_tree().pushWorkspace().content().directory()
        if os.path.exists(inner_content_pkg_path):
            with tarfile.open(inner_content_pkg_path, mode='r:gz') as content_tar:
                content_tar.extractall(extracted_content_path)
        else:
            msg = 'Invalid package, does not include content package {0}'.format(inner_content_pkg_path)
            return self._return_failure(msg)
        return self._return_passed()
