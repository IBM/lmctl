import os
import zipfile
import yaml
import lmctl.files as files
import lmctl.project.validation as project_validation
import lmctl.project.handlers.interface as handlers_api
from lmctl.project.mutate.base import Mutator
from .ansiblerm_content import AnsibleRmCsarContentTree, AnsibleRmPkgContentTree

class AnsibleRmSourceTree(files.Tree):

    DESCRIPTOR_DIR_NAME = 'descriptor'
    LIFECYCLE_DIR_NAME = 'lifecycle'
    META_INF_DIR_NAME = 'Meta-Inf'
    MANIFEST_FILE_NAME = 'manifest.MF'
    TESTS_DIR_NAME = 'tests'

    def gen_descriptor_file_path(self, resource_name):
        return self.resolve_relative_path(AnsibleRmSourceTree.DESCRIPTOR_DIR_NAME, '{0}.yml'.format(resource_name))

    @property
    def lifecycle_path(self):
        return self.resolve_relative_path(AnsibleRmSourceTree.LIFECYCLE_DIR_NAME)

    def gen_lifecycle_file(self, lifecycle_name):
        return self.resolve_relative_path(AnsibleRmSourceTree.LIFECYCLE_DIR_NAME, '{0}.yml'.format(lifecycle_name))

    @property
    def meta_inf_path(self):
        return self.resolve_relative_path(AnsibleRmSourceTree.META_INF_DIR_NAME)

    @property
    def meta_inf_manifest_file_path(self):
        return self.resolve_relative_path(AnsibleRmSourceTree.META_INF_DIR_NAME, AnsibleRmSourceTree.MANIFEST_FILE_NAME)

    @property
    def tests_path(self):
        return self.resolve_relative_path(AnsibleRmSourceTree.TESTS_DIR_NAME)

class AnsibleRmSourceCreatorDelegate(handlers_api.ResourceSourceCreatorDelegate):

    def __init__(self):
        super().__init__()

    def create_source(self, journal, source_request, file_ops_executor):
        source_tree = AnsibleRmSourceTree()
        file_ops = []
        descriptor_content ='description: descriptor for {0}'.format(source_request.source_config.name)
        file_ops.append(handlers_api.CreateFileOp(source_tree.gen_descriptor_file_path(source_request.source_config.name), descriptor_content, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.lifecycle_path, handlers_api.EXISTING_IGNORE))
        install_content = '---\n- name: Install\n  hosts: all\n  gather_facts: False'
        file_ops.append(handlers_api.CreateFileOp(source_tree.gen_lifecycle_file('Install'), install_content, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.meta_inf_path, handlers_api.EXISTING_IGNORE))
        manifest_content = 'resource-manager: ansible'
        file_ops.append(handlers_api.CreateFileOp(source_tree.meta_inf_manifest_file_path, manifest_content, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.tests_path, handlers_api.EXISTING_IGNORE))
        file_ops_executor(file_ops)

class AnsibleRmCompileError(handlers_api.SourceHandlerError):
    pass


class AnsibleRmSourceHandlerDelegate(handlers_api.ResourceSourceHandlerDelegate):

    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)
        self.tree = AnsibleRmSourceTree(self.root_path)

    def validate_sources(self, journal, source_validator, validation_options):
        errors = []
        warnings = []
        self.__validate_lifecycle(journal, errors, warnings)
        self.__validate_meta_inf(journal, errors, warnings)
        return project_validation.ValidationResult(errors, warnings)

    def get_main_descriptor(self):
        main_descriptor_path = self.tree.gen_descriptor_file_path(self.source_config.name)
        return main_descriptor_path

    def __validate_lifecycle(self, journal, errors, warnings):
        lifecycle_path = self.tree.lifecycle_path
        if not os.path.exists(lifecycle_path):
            msg = 'No lifecycle sources found at: {0}'.format(lifecycle_path)
            journal.error_event(msg)
            errors.append(project_validation.ValidationViolation(msg))
        else:
            journal.event('Lifecycle found at: {0}'.format(lifecycle_path))

    def __validate_meta_inf(self, journal, errors, warnings):
        meta_inf_path = self.tree.meta_inf_manifest_file_path
        if not os.path.exists(meta_inf_path):
            msg = 'No manifest found at: {0}'.format(meta_inf_path)
            journal.error_event(msg)
            errors.append(project_validation.ValidationViolation(msg))
        else:
            journal.event('Manifest found at: {0}'.format(meta_inf_path))

    def stage_sources(self, journal, source_stager):
        staging_tree = AnsibleRmCsarContentTree()
        journal.event('Staging resource descriptor for {0} at {1}'.format(self.source_config.full_name, self.get_main_descriptor()))
        source_stager.stage_descriptor(self.get_main_descriptor(), staging_tree.gen_descriptor_file_path(self.source_config.full_name))
        included_items = [
            {'path': self.tree.lifecycle_path, 'alias': staging_tree.lifecycle_path},
            {'path': self.tree.tests_path, 'alias': staging_tree.tests_path},
            {'path': self.tree.meta_inf_path, 'alias': staging_tree.meta_inf_path}
        ]
        self.__stage_directories(journal, source_stager, included_items)
        manifest_file_path = self.tree.meta_inf_manifest_file_path
        source_stager.stage_file(manifest_file_path, staging_tree.meta_inf_manifest_file_path, ManifestStagingMutator(self.source_config.full_name, self.source_config.version))

    def __stage_directories(self, journal, source_stager, items):
        for item in items:
            if os.path.exists(item['path']):
                journal.event('Staging directory {0}'.format(item['path']))
                source_stager.stage_tree(item['path'], item['alias'])

    def build_staged_source_delegate(self, staging_path):
        return AnsibleRmStagedSourceHandlerDelegate(staging_path, self.source_config)


class AnsibleRmStagedSourceHandlerDelegate(handlers_api.ResourceStagedSourceHandlerDelegate):

    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)
        self.tree = AnsibleRmCsarContentTree(self.root_path)

    def compile_sources(self, journal, source_compiler):
        pkg_tree = AnsibleRmPkgContentTree()
        self.__build_csar(journal, source_compiler, pkg_tree)
        self.__add_root_descriptor(journal, source_compiler, pkg_tree)

    def __add_root_descriptor(self, journal, source_compiler, pkg_tree):
        relative_root_descriptor_path = pkg_tree.gen_root_descriptor_file_path(self.source_config.full_name)
        source_compiler.compile_file(self.tree.gen_descriptor_file_path(self.source_config.full_name), relative_root_descriptor_path)

    def __build_csar(self, journal, source_compiler, pkg_tree):
        csar_content_tree = AnsibleRmCsarContentTree()
        relative_csar_path = pkg_tree.gen_csar_file_path(self.source_config.full_name)
        full_csar_path = source_compiler.make_file_path(relative_csar_path)
        journal.event('Creating CSAR for Resource {0}: {1}'.format(self.source_config.name, relative_csar_path))
        with zipfile.ZipFile(full_csar_path, "w") as csar:
            included_items = [
                {'path': self.tree.descriptor_path, 'alias': csar_content_tree.descriptor_path, 'required': True},
                {'path': self.tree.lifecycle_path, 'alias': csar_content_tree.lifecycle_path, 'required': True},
                {'path': self.tree.tests_path, 'alias': csar_content_tree.tests_path, 'required': False},
                {'path': self.tree.meta_inf_path, 'alias': csar_content_tree.meta_inf_path, 'required': True}
            ]
            for included_item in included_items:
                self.__add_directory_if_exists(journal, csar, included_item)

    def __add_directory_if_exists(self, journal, csar, included_item):
        path = included_item['path']
        if os.path.exists(path):
            journal.event('Adding directory to CSAR: {0}'.format(os.path.basename(path)))
            csar.write(path, arcname=included_item['alias'])
            rootlen = len(path) + 1
            for root, dirs, files in os.walk(path):
                for filename in files:
                    full_path = os.path.join(root, filename)
                    csar.write(full_path, arcname=os.path.join(included_item['alias'], full_path[rootlen:]))
        else:
            if included_item['required']:
                msg = 'Required directory for Resource CSAR not found: {0}'.format(path)
                journal.error_event(msg)
                raise AnsibleRmCompileError(msg)
            else:
                journal.event('Skipping directory for Resource CSAR, not found: {0}'.format(path))


class ManifestStagingMutator(Mutator):

    def __init__(self, resource_name, resource_version):
        self.resource_name = resource_name
        self.resource_version = resource_version

    def apply(self, original_content):
        manifest_dict = yaml.safe_load(original_content)
        new_manifest_dict = {
            'name': self.resource_name,
            'version': float(self.resource_version)
        }
        for key, value in manifest_dict.items():
            if key != 'name' and key != 'version':
                new_manifest_dict[key] = value
        return yaml.dump(new_manifest_dict, sort_keys=False)
