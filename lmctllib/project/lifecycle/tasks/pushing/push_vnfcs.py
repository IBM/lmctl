import os
import lmctllib.project.packaging as project_packaging
from ..tasks import ProjectLifecycleTask

class DeployVnfcs(ProjectLifecycleTask):
    """
    Pushes VNFCs to the target RM based on their packaging-types and package-executions configured on the Project
    """
    def __init__(self):
        super().__init__("Deploy VNFCs")
    
    def execute_work(self, tools, products):
        vnfc_packages = self._get_project().vnfcs.packages
        if not vnfc_packages:
            return self._return_skipped('Found no VNFC packages defined')
        for package_id, package_def in vnfc_packages.items():
            endResult = self.__deployVnfcs(tools, products, package_id, package_def)
            if endResult:
                return endResult
        return self._return_passed()

    def __deployVnfcs(self, tools, products, package_id, package_def):
        journal = self._get_journal()
        packaging_type = package_def.packaging_type
        journal.add_text('Executing {0} packaging for VNFCs using package manager type: {1}'.format(package_id, packaging_type))
        package_manager = project_packaging.getPackageManager(packaging_type, package_id, package_def)
        package_executions = package_def.executions
        vnfc_definitions = self._get_project().vnfcs.definitions
        for package_execution in package_executions:
            vnfc_ref = package_execution.vnfc
            vnfc_def = vnfc_definitions[vnfc_ref]
            if not vnfc_def:
                return self._return_failure('VNFC packages definition {0} references execution on VNFC not defined with ref {1}'.format(package_id, vnfc_ref))
            journal.add_text('Pushing VNFC: {0}'.format(vnfc_ref))
            vnfc_directory = vnfc_def.directory
            vnfc_pkg_dir = self._get_project_tree().pushWorkspace().content().vnfcs().vnfcDirectory(vnfc_directory)
            try:
                deploy_environment = package_manager.select_deploy_environment(self._get_environment(), self._get_environment_selectors())
                package_manager.deploy(self._get_journal(), deploy_environment, package_execution, vnfc_def, vnfc_pkg_dir)
            except project_packaging.PackageManagerException as e:
                return self._return_failure(str(e))
            journal.paragraph_break()
        package_manager.post_deploy(self._get_journal(), deploy_environment)