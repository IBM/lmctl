import os
import shutil
import tempfile
import lmctl.project.source.core as project_sources

class SimulatedProject:

    def __init__(self, path):
        self.path = path
        self.project = None

    def destroy(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)

    def as_project(self):
        if not self.project:
            self.project = project_sources.Project(self.path)
        return self.project


class ProjectSimulator:

    def __init__(self, template_path, path=None):
        self.project_path = path
        if self.project_path is None:
            self.project_path = tempfile.mkdtemp()
        self.template_path = template_path

    def start(self):
        self._copy_project(self.template_path)
        return SimulatedProject(self.project_path)

    def _copy_project(self, template_path):
        if os.path.exists(self.project_path):
            shutil.rmtree(self.project_path)
        shutil.copytree(template_path, self.project_path)
        lmctl_workspace = os.path.join(self.project_path, '_lmctl')
        if os.path.exists(lmctl_workspace):
            shutil.rmtree(lmctl_workspace)

class SimulatedPkg:

    def __init__(self, pkg_holder_dir, pkg_path):
        self.path = pkg_path
        self.pkg_holder_dir = pkg_holder_dir

    def destroy(self):
        if os.path.exists(self.pkg_holder_dir):
            shutil.rmtree(self.pkg_holder_dir)

class PkgSimulator:

    def __init__(self, pkg_template_path, path=None):
        self.pkg_path = path
        self.pkg_holder_dir = tempfile.mkdtemp()
        if self.pkg_path is None:
            self.pkg_path = os.path.join(self.pkg_holder_dir, os.path.basename(os.path.normpath(pkg_template_path)))
        self.pkg_template_path = pkg_template_path

    def start(self):
        self._copy_pkg(self.pkg_template_path)
        return SimulatedPkg(self.pkg_holder_dir, self.pkg_path)

    def _copy_pkg(self, pkg_template_path):
        if os.path.exists(self.pkg_path):
            os.remove(self.pkg_path)
        shutil.copy2(pkg_template_path, self.pkg_path)
