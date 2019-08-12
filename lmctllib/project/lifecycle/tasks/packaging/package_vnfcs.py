import os
import shutil
import distutils.dir_util 
import lmctllib.project.model as project_model
import lmctllib.project.packaging as project_packaging
from ..tasks import ProjectLifecycleTask

class PackageVnfcs(ProjectLifecycleTask):
    """
    Packages VNFCs according to their packaging type
    """
    def __init__(self):
        super().__init__("Package VNFCs")
    
    def execute_work(self, tools, products):
        vnfc_packages = self._get_project().vnfcs.packages
        if not vnfc_packages:
            return self._return_skipped('Found no VNFC packages in project definition')
        for package_id, package_def in vnfc_packages.items():
            endResult = self.__packageVnfcs(tools, products, package_id, package_def)
            if endResult:
                return endResult

        return self._return_passed()

    def __packageVnfcs(self, tools, products, package_id, package_def: project_model.VnfcPackage):
        packaging_type = package_def.packaging_type
        journal = self._get_journal()
        journal.add_text('Producing {0} package for VNFCs using packaging type: {1}'.format(package_id, packaging_type))
        package_manager = project_packaging.getPackageManager(packaging_type, package_id, package_def)
        if package_manager is None:
            return self._return_failure('No package manager found for VNFC packaging-type {0}'.format(packaging_type))
        package_executions = package_def.executions
        if not package_executions:
            return self._return_failure('No executions included on VNFC packages definition {0}'.format(package_id))
        vnfc_definitions = self._get_project().vnfcs.definitions
        for package_execution in package_executions:
            vnfc_ref = package_execution.vnfc
            vnfc_def = vnfc_definitions[vnfc_ref]
            if not vnfc_def:
                return self._return_failure('VNFC packages definition {0} references execution on VNFC not defined with ref {1}'.format(package_id, vnfc_ref))
            journal.add_text('Packaging VNFC {0} using package manager type: {1}'.format(vnfc_ref, packaging_type))
            vnfc_directory = vnfc_def.directory
            vnfc_src_dir = self._get_project_tree().vnfcs().vnfcDirectory(vnfc_directory)
            vnfc_build_dir = self._get_project_tree().build().resources().vnfcs().vnfcDirectory(vnfc_directory)
            if os.path.exists(vnfc_build_dir):
                shutil.rmtree(vnfc_build_dir)
            distutils.dir_util.copy_tree(vnfc_src_dir, vnfc_build_dir, 0)
            vnfc_package_dir = self._get_project_tree().build().packaging().vnfcs().vnfcDirectory(vnfc_directory)
            os.makedirs(vnfc_package_dir)
            try:
                package_manager.package(self._get_journal(), package_execution, vnfc_def, vnfc_build_dir, vnfc_package_dir)
            except project_packaging.PackageManagerException as e:
                return self._return_failure(str(e))
        return None
