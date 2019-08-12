import os
import tarfile
import shutil
import lmctllib.pipeline as pipeline
import lmctllib.journal as journal
import lmctllib.project.structure as project_struct
from .packaging import establishBuiltPackageName
from ..tasks import ProjectLifecycleTask

class FinalPackage(ProjectLifecycleTask):
    """
    Produces the final build artifact of the project. Takes everything in the "packaging" directory and produces a "content" tgz file. 
    This tgz is then included alongside the project lmproject file in the final tgz package, created in the build directory of the project.
    """
    def __init__(self):
        super().__init__("Final Package")

    def execute_work(self, tools: pipeline.TaskTools, products: pipeline.TaskProducts):
        journal = self._get_journal()
        project_tree = self._get_project_tree()
        pkg_src_dir = project_tree.build().packaging().directory()
        pkg_name = establishBuiltPackageName(self._get_project_name(), project_tree)
        pkg_path = project_tree.build().packageFile(pkg_name)
        content_pkg_path = project_tree.build().packageContentFile()
        if os.path.exists(pkg_src_dir):
            journal.add_text('Building final package: {0}'.format(pkg_path))
            with tarfile.open(content_pkg_path, mode="w:gz") as pkg_tar:
                rootlen = len(pkg_src_dir) + 1
                for root, dirs, files in os.walk(pkg_src_dir):
                    for filename in files:
                        full_path = os.path.join(root, filename)
                        pkg_tar.add(full_path, arcname=full_path[rootlen:])
            with tarfile.open(pkg_path, mode="w:gz") as pkg_tar:
                pkg_tree = project_struct.PackageWrapperTree(pkg_path)
                pkg_tar.add(content_pkg_path, arcname=os.path.basename(pkg_tree.contentFile()))
                project_file = project_tree.projectFile()
                pkg_tar.add(project_file, arcname=os.path.basename(pkg_tree.projectFile()))
            os.remove(content_pkg_path)
        else:
            return self._return_failure('Could not find packaging directory: {0}'.format(pkg_src_dir))
        return self._return_passed()