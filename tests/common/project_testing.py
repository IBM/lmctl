from tests.common.simulations.project_lab import ProjectSimLab
import unittest
import yaml
import os
import shutil
import tarfile
import zipfile
import tempfile

WORKSPACE = '_lmctl'

BACKUP_DIR = 'pre_pull_backup'

PROJECT_CONTAINS_DIR = 'Contains'
PROJECT_VNFCS_DIR = 'VNFCs'
PROJECT_FILE_YML = 'lmproject.yml'
PROJECT_FILE_YAML = 'lmproject.yaml'

PKG_CONTENT_DIR = 'content'
PKG_META_YML_FILE = 'lmpkg.yml'

ASSEMBLY_DESCRIPTOR_DIR = 'Descriptor'
ASSEMBLY_DESCRIPTOR_YML_FILE = 'assembly.yml'
ASSEMBLY_DESCRIPTOR_YAML_FILE = 'assembly.yaml'

ASSEMBLY_BEHAVIOUR_DIR = 'Behaviour'
ASSEMBLY_CONFIGURATIONS_DIR = 'Configurations'
ASSEMBLY_RUNTIME_DIR = 'Runtime'
ASSEMBLY_TESTS_DIR = 'Tests'

ARM_DESCRIPTOR_DIR = 'descriptor'
ARM_LIFECYCLE_DIR = 'lifecycle'
ARM_METAINF_DIR = 'Meta-Inf'
ARM_MANIFEST_FILE = 'manifest.MF'
ARM_TEST_DIR = 'tests'

class ProjectSimTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.simlab = ProjectSimLab()
        super().__init__(*args, **kwargs)

    def tearDown(self):
        self.simlab.destroySims()

    def assert_validation_errors(self, validation_result, *errors):
        self.assertTrue(len(validation_result.errors), len(errors))
        idx = 0
        for error in errors:
            self.assertEqual(validation_result.errors[idx].message, errors[idx])
            idx+=1

    def assert_project(self, project):
        return ProjectAssertions(project)

    def assert_package(self, pkg):
        return PkgAssertions(pkg)

    def assert_zip(self, zip_file_path):
        return ZipFileAssertions(zip_file_path)


class ProjectAssertions:

    def __init__(self, project):
        self.project = project
        self.tc = unittest.TestCase('__init__')
        self.tc.maxDiff = None
    
    def __full_path(self, rel_path):
        return os.path.join(self.project.tree.root_path, rel_path)

    def assert_has_backup(self, expected_backup_file_path, expected_backup_content):
        backup_path = os.path.join(self.project.tree.root_path, WORKSPACE, BACKUP_DIR)
        self.assert_has_file(os.path.join(backup_path, expected_backup_file_path), expected_backup_content)

    def assert_has_no_backup(self, expected_backup_file_path):
        backup_path = os.path.join(self.project.tree.root_path, WORKSPACE, BACKUP_DIR)
        self.assert_has_no_file(os.path.join(backup_path, expected_backup_file_path))

    def assert_has_no_file(self, expected_file_path):
        full_path = self.__full_path(expected_file_path)
        self.tc.assertFalse(os.path.exists(full_path))

    def assert_has_file(self, expected_file_path, expected_file_content):
        full_path = self.__full_path(expected_file_path)
        self.tc.assertTrue(os.path.exists(full_path))
        with open(full_path, 'r') as file:
            content = file.read()
        self.tc.assertEqual(content, expected_file_content)

    def assert_has_directory(self, rel_directory_path):
        full_path = self.__full_path(rel_directory_path)
        self.tc.assertTrue(os.path.exists(full_path))

    def assert_has_config(self, expected_config_dict):
        config_path = self.__full_path(PROJECT_FILE_YML)
        self.tc.assertTrue(os.path.exists(config_path))
        with open(config_path, 'r') as config_file:
            config_content = yaml.safe_load(config_file.read())
        self.tc.assertEqual(config_content, expected_config_dict)
        
class PkgAssertions:

    def __init__(self, pkg):
        self.pkg = pkg
        self.temp_dir = None
        self.tc = unittest.TestCase('__init__')
        self.tc.maxDiff = None

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp()
        with tarfile.open(self.pkg.path, mode='r:gz') as pkg_tar:
            pkg_tar.extractall(self.temp_dir)
        return self

    def __exit__(self, type, value, traceback):
        if self.temp_dir is not None and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def __full_content_path(self, content_path):
        return os.path.join(self.temp_dir, PKG_CONTENT_DIR, content_path)

    def assert_has_content_file(self, content_path):
        self.tc.assertTrue(os.path.exists(self.__full_content_path(content_path)))

    def assert_has_descriptor_file(self, expected_descriptor_path, expected_descriptor_content):
        full_path = self.__full_content_path(expected_descriptor_path)
        self.tc.assertTrue(os.path.exists(full_path))
        with open(full_path, 'r') as descriptor_file:
            descriptor_content = descriptor_file.read()
        self.tc.assertEqual(descriptor_content, expected_descriptor_content)

    def assert_has_meta(self, expected_meta_dict):
        meta_path = os.path.join(self.temp_dir, PKG_META_YML_FILE)
        self.tc.assertTrue(os.path.exists(meta_path))
        with open(meta_path, 'r') as meta_file:
            meta_content = yaml.safe_load(meta_file.read())
        self.tc.assertEqual(meta_content, expected_meta_dict)

    def assert_has_directory(self, rel_directory_path):
        full_path = self.__full_content_path(rel_directory_path)
        self.tc.assertTrue(os.path.exists(full_path))

    def assert_has_file_path(self, expected_file_path):
        full_path = self.__full_content_path(expected_file_path)
        self.tc.assertTrue(os.path.exists(full_path))

    def assert_has_file(self, expected_file_path, expected_file_content):
        full_path = self.__full_content_path(expected_file_path)
        self.tc.assertTrue(os.path.exists(full_path))
        with open(full_path, 'r') as file:
            content = file.read()
        self.tc.assertEqual(content, expected_file_content)

    def get_file_path(self, expected_file_path):
        full_path = self.__full_content_path(expected_file_path)
        return full_path


class ZipFileAssertions:

    def __init__(self, zip_file_path):
        self.zip_file_path = zip_file_path
        self.temp_dir = None
        self.tc = unittest.TestCase('__init__')

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(self.zip_file_path, mode='r') as zip_reader:
            zip_reader.extractall(self.temp_dir)
        return self

    def __exit__(self, type, value, traceback):
        if self.temp_dir is not None and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def __full_content_path(self, content_path):
        return os.path.join(self.temp_dir, content_path)

    def assert_has_directory(self, rel_directory_path):
        full_path = self.__full_content_path(rel_directory_path)
        self.tc.assertTrue(os.path.exists(full_path))

    def assert_has_file(self, expected_file_path, expected_file_content):
        full_path = self.__full_content_path(expected_file_path)
        self.tc.assertTrue(os.path.exists(full_path))
        with open(full_path, 'r') as file:
            content = file.read()
        self.tc.assertEqual(content, expected_file_content)
