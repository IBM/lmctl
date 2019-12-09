import os
import tarfile
import yaml
import lmctl.files as files
import lmctl.project.package.core as pkgs
import lmctl.project.package.meta as pkg_metas
from .common import LIFECYCLE_WORKSPACE

class PkgBuildTree(files.Tree):

    @property
    def pkg_meta_file_name(self):
        return pkgs.ExpandedPkgTree.PKG_META_FILE_YML

    def pkg_meta_file_path(self):
        return self.resolve_relative_path(self.pkg_meta_file_name)

    def gen_pkg_path(self, project_name, project_version):
        return self.resolve_relative_path('{0}-{1}.tgz'.format(project_name, project_version))

class PkgProcessError(Exception):
    pass

class PkgProcess:

    def __init__(self, project, options, content_tree, journal):
        self.project = project
        self.options = options
        self.content_tree = content_tree
        self.journal = journal

    def __create_pkg_build_tree(self):
        return PkgBuildTree(os.path.join(self.project.tree.root_path, LIFECYCLE_WORKSPACE, 'build'))

    def execute(self):
        self.journal.section('Finalise Package')
        build_tree = self.__create_pkg_build_tree()
        files.clean_directory(build_tree.root_path)
        pkg_meta_file_path = build_tree.pkg_meta_file_path()
        self.__create_pkg_meta(pkg_meta_file_path)
        pkg_path = build_tree.gen_pkg_path(self.project.config.full_name, self.project.config.version)
        self.journal.event('Creating package at: {0}'.format(pkg_path))
        pkg_tree = pkgs.ExpandedPkgTree()
        compiled_content_path = self.content_tree.root_path
        with tarfile.open(pkg_path, mode="w:gz") as pkg_tar:
            content_dir = pkg_tree.content_dir_name
            rootlen = len(compiled_content_path) + 1
            for root, dirs, filelist in os.walk(compiled_content_path):
                for file_name in filelist:
                    full_path = os.path.join(root, file_name)
                    file_size = os.path.getsize(full_path)
                    arcname = os.path.join(content_dir, full_path[rootlen:])
                    if file_size > 100000000:
                        # For big files let people know. TODO: make this more generic, so we can report long running tasks as events
                        self.journal.event('Processing large file {0} ({1:.2f} mb), this may take some time...'.format(os.path.basename(full_path), (file_size/1000000)))
                    pkg_tar.add(full_path, arcname=arcname)
            pkg_tar.add(pkg_meta_file_path, arcname=pkg_tree.pkg_meta_file_name)
        self.__clear_compile_directory()
        try:
            return pkgs.Pkg(pkg_path)
        except pkgs.InvalidPackageError as e:
            raise PkgProcessError(str(e)) from e

    def __clear_compile_directory(self):
        files.remove_directory(self.content_tree.root_path)

    def __create_pkg_meta(self, pkg_meta_file_path):
        builder = pkg_metas.RootPkgMetaBuilder()
        builder.schema(self.project.config.schema)
        builder.name(self.project.config.name)
        builder.content_type(self.project.config.project_type)
        builder.version(self.project.config.version)
        builder.resource_manager(self.project.config.resource_manager)
        self.__add_included_artifacts_entries(self.project.config, builder, self.content_tree)
        self.__add_child_projects_to_pkg_meta(self.project.config, builder)
        try:
            pkg_meta = builder.build()
        except pkg_metas.PkgMetaError as e:
           raise PkgProcessError(str(e)) from e
        with open(pkg_meta_file_path, 'w') as pkg_meta_file:
            yaml.dump(pkg_meta.to_dict(), pkg_meta_file, default_flow_style=False, sort_keys=False)
        return pkg_meta_file_path

    def __add_child_projects_to_pkg_meta(self, config, meta_builder):
        subprojects = config.subprojects
        for subproject_config in subprojects:
            subpkg_builder = meta_builder.subpkg_entry_builder()
            subpkg_builder.name(subproject_config.name)
            subpkg_builder.content_type(subproject_config.project_type)
            subpkg_builder.directory(subproject_config.directory)
            subpkg_builder.resource_manager(subproject_config.resource_manager)
            self.__add_included_artifacts_entries(subproject_config, subpkg_builder, self.content_tree.gen_child_content_tree(subproject_config.directory))
            self.__add_child_projects_to_pkg_meta(subproject_config, subpkg_builder)

    def __add_included_artifacts_entries(self, config, meta_builder, content_tree):
        artifacts_content_dir = content_tree.artifacts_path
        for included_artifact_entry in config.included_artifacts:
            dir_name = included_artifact_entry.artifact_name
            path_to_compiled_dir = os.path.join(artifacts_content_dir, dir_name)
            if not os.path.exists(path_to_compiled_dir):
                raise PkgProcessError('Artifact named {0} has not been compiled correctly, there is no directory found for it in the compiled source'.format(path_to_compiled_dir))
            artifact_entry_builder = meta_builder.included_artifact_builder()
            artifact_entry_builder.artifact_name(included_artifact_entry.artifact_name)
            artifact_entry_builder.artifact_type(included_artifact_entry.artifact_type)
            artifact_entry_builder.path(dir_name)
            if len(included_artifact_entry.items) == 0:
                artifact_entry_builder.add_item(os.path.basename(included_artifact_entry.path))
            else:
                named_files = []
                for item in included_artifact_entry.items:
                    if not item.is_wildcard:
                        named_files.append(os.path.basename(item.path))
                for item in included_artifact_entry.items:
                    if item.is_wildcard:
                        for file_name in os.listdir(os.path.join(artifacts_content_dir, dir_name)):
                            if file_name not in named_files:
                                artifact_entry_builder.add_item(file_name)
                    else:
                        artifact_entry_builder.add_item(item.path)