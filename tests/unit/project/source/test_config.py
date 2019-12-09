import unittest
import tempfile
import os
import yaml
import shutil
from lmctl.project.source.config import ProjectConfigRewriter, ProjectConfigParser, RootProjectConfig, ProjectConfigError, IncludedArtifactEntry, ArtifactDirectoryItem

OLD_STYLE_CONFIG = """\
name: testproject
vnfcs:
  definitions:
    vnfcA:
      directory: vnfcA
    vnfcB:
      directory: vnfcB
  packages:
    ansible-rm-vnfcs:
      packaging-type: ansible-rm
      executions:
      - vnfc: vnfcA
      - vnfc: vnfcB
"""

NEW_STYLE_CONFIG = """\
## Lmctl has updated this file with the latest schema changes. A backup of your existing project file has been placed in the same directory with a .bak extension
schema: '2.0'
name: testproject
version: '0.8'
contains:
- name: vnfcA
  type: Resource
  directory: vnfcA
  resource-manager: ansible-rm
- name: vnfcB
  type: Resource
  directory: vnfcB
  resource-manager: ansible-rm
"""

OLD_STYLE_NO_VNFCS = """\
name: testproject
vnfcs: 
  definitions: {}
  packages: {}
"""

NEW_STYLE_NO_VNFCS = """\
## Lmctl has updated this file with the latest schema changes. A backup of your existing project file has been placed in the same directory with a .bak extension
schema: '2.0'
name: testproject
version: '1.0'
contains: []
"""

class TestProjectConfigRewriter(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_rewrite(self):
        file_path = os.path.join(self.tmp_dir, 'rewrite.yml')
        with open(file_path, 'w') as f:
            f.write(OLD_STYLE_CONFIG)
        old_config_dict = yaml.safe_load(OLD_STYLE_CONFIG)
        new_config_dict = ProjectConfigRewriter(file_path, old_config_dict, '0.8').rewrite()
        expected_new_config_dict = {
            'schema': '2.0',
            'name': 'testproject',
            'version': '0.8',
            'contains': [
                {
                    'name': 'vnfcA',
                    'type': 'Resource',
                    'directory': 'vnfcA',
                    'resource-manager': 'ansible-rm'
                },
                {
                    'name': 'vnfcB',
                    'type': 'Resource',
                    'directory': 'vnfcB',
                    'resource-manager': 'ansible-rm'
                }
            ]
        }
        self.assertDictEqual(new_config_dict, expected_new_config_dict)
        backup_path = os.path.join(self.tmp_dir, 'rewrite.yml.bak')
        self.assertTrue(os.path.exists(backup_path))
        with open(backup_path, 'r') as f:
            backup_config = f.read()
        self.assertEqual(backup_config, OLD_STYLE_CONFIG)
        with open(file_path, 'r') as f:
            new_config = f.read()
        self.assertEqual(new_config, NEW_STYLE_CONFIG)

    def test_rewrite_no_vnfcs(self):
        file_path = os.path.join(self.tmp_dir, 'rewrite.yml')
        with open(file_path, 'w') as f:
            f.write(OLD_STYLE_NO_VNFCS)
        old_config_dict = yaml.safe_load(OLD_STYLE_NO_VNFCS)
        new_config_dict = ProjectConfigRewriter(file_path, old_config_dict).rewrite()
        expected_new_config_dict = {
            'schema': '2.0',
            'name': 'testproject',
            'version': '1.0',
            'contains': []
        }
        self.assertDictEqual(new_config_dict, expected_new_config_dict)
        backup_path = os.path.join(self.tmp_dir, 'rewrite.yml.bak')
        self.assertTrue(os.path.exists(backup_path))
        with open(backup_path, 'r') as f:
            backup_config = f.read()
        self.assertEqual(backup_config, OLD_STYLE_NO_VNFCS)
        with open(file_path, 'r') as f:
            new_config = f.read()
        self.assertEqual(new_config, NEW_STYLE_NO_VNFCS)

class TestProjectConfigParser(unittest.TestCase):
    
    def test_parse_assembly(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly'
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertIsInstance(parsed_config, RootProjectConfig)
        self.assertEqual(parsed_config.schema, '2.0')
        self.assertEqual(parsed_config.name, 'Test')
        self.assertEqual(parsed_config.version, '1.0')
        self.assertEqual(parsed_config.project_type, 'Assembly')
        self.assertEqual(parsed_config.resource_manager, None)
        self.assertEqual(parsed_config.subproject_entries, [])

    def test_parse_resource(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Resource',
            'resource-manager': 'brent'
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertIsInstance(parsed_config, RootProjectConfig)
        self.assertEqual(parsed_config.schema, '2.0')
        self.assertEqual(parsed_config.name, 'Test')
        self.assertEqual(parsed_config.version, '1.0')
        self.assertEqual(parsed_config.project_type, 'Resource')
        self.assertEqual(parsed_config.resource_manager, 'brent')
        self.assertEqual(parsed_config.subproject_entries, [])
        
    def test_parse_subprojects(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'contains': [
                {
                    'name': 'SubA',
                    'type': 'Resource',
                    'resource-manager': 'brent',
                    'directory': 'SubA'
                },
                {
                    'name': 'SubB',
                    'type': 'Assembly',
                    'directory': 'SubB'
                }
            ]
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertIsInstance(parsed_config, RootProjectConfig)
        self.assertEqual(len(parsed_config.subproject_entries), 2)
        subA_entry = parsed_config.subproject_entries[0]
        self.assertEqual(subA_entry.name, 'SubA')
        self.assertEqual(subA_entry.project_type, 'Resource')
        self.assertEqual(subA_entry.resource_manager, 'brent')
        self.assertEqual(subA_entry.directory, 'SubA')
        self.assertEqual(subA_entry.subproject_entries, [])
        subB_entry = parsed_config.subproject_entries[1]
        self.assertEqual(subB_entry.name, 'SubB')
        self.assertEqual(subB_entry.project_type, 'Assembly')
        self.assertEqual(subB_entry.directory, 'SubB')
        self.assertEqual(subB_entry.subproject_entries, [])
    
    def test_parse_nested_subprojects(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'contains': [
                {
                    'name': 'SubA',
                    'type': 'Resource',
                    'resource-manager': 'brent',
                    'directory': 'SubA',
                    'contains': [
                        {
                            'name': 'SubA1',
                            'type': 'Assembly',
                            'directory': 'moreSub'
                        }
                    ]
                }
            ]
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertIsInstance(parsed_config, RootProjectConfig)
        self.assertEqual(len(parsed_config.subproject_entries), 1)
        subA_entry = parsed_config.subproject_entries[0]
        self.assertEqual(len(subA_entry.subproject_entries), 1)
        subA1_entry = subA_entry.subproject_entries[0]
        self.assertEqual(subA1_entry.name, 'SubA1')
        self.assertEqual(subA1_entry.project_type, 'Assembly')
        self.assertEqual(subA1_entry.directory, 'moreSub')
        self.assertEqual(subA1_entry.subproject_entries, [])

    def test_parse_invalid_no_name(self):
        invalid_config = {
            'schema': '2.0',
            'version': '1.0',
            'type': 'Assembly'
        }
        with self.assertRaises(ProjectConfigError) as context:
            ProjectConfigParser.from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'name must be defined')

    def test_parse_invalid_no_schema(self):
        invalid_config = {
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly'
        }
        with self.assertRaises(ProjectConfigError) as context:
            ProjectConfigParser.from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'schema must be defined')

    def test_parse_invalid_no_version(self):
        invalid_config = {
            'name': 'Test',
            'schema': '2.0',
            'type': 'Assembly'
        }
        with self.assertRaises(ProjectConfigError) as context:
            ProjectConfigParser.from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'version must be defined')

    def test_parse_valid_no_type(self):
        valid_config = {
            'name': 'Test',
            'schema': '2.0',
            'version': '1.0'
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertEqual(parsed_config.project_type, 'Assembly')

    def test_parse_invalid_resource_no_resource_manager(self):
        invalid_config = {
            'name': 'Test',
            'schema': '2.0',
            'type': 'Resource',
            'version': '1.0'
        }
        with self.assertRaises(ProjectConfigError) as context:
            ProjectConfigParser.from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'resource_manager must be defined when type is Resource')

    def test_parse_invalid_subproject_no_name(self):
        invalid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'contains': [
                {
                    'type': 'Resource',
                    'resource-manager': 'brent',
                    'directory': 'SubA'
                }
            ]
        }
        with self.assertRaises(ProjectConfigError) as context:
            ProjectConfigParser.from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'name must be defined')

    def test_parse_valid_subproject_no_directory(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'contains': [
                {
                    'type': 'Resource',
                    'resource-manager': 'brent',
                    'name': 'SubA'
                }
            ]
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertEqual(parsed_config.subproject_entries[0].directory, 'SubA')

    def test_parse_valid_subproject_no_type(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'contains': [
                {
                    'name': 'SubA',
                    'directory': 'SubA'
                }
            ]
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertEqual(parsed_config.project_type, 'Assembly')

    def test_parse_invalid_subproject_resource_no_resource_manager(self):
        invalid_config = {
            'name': 'Test',
            'schema': '2.0',
            'type': 'Resource',
            'version': '1.0',
            'contains': [
                {
                    'name': 'SubA',
                    'directory': 'SubA',
                    'type': 'Resource'
                }
            ]
        }
        with self.assertRaises(ProjectConfigError) as context:
            ProjectConfigParser.from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'resource_manager must be defined when type is Resource')

    def test_parse_included_artifacts(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'includedArtifacts': [
                {
                    'name': 'dockertest',
                    'type': 'docker-image',
                    'path': 'Images/docker.tar'
                },
                {
                    'name': 'glancetest',
                    'type': 'glance-image',
                    'path': 'Images/glance.tar'
                }
            ]
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertEqual(len(parsed_config.included_artifacts), 2)
        first_artifact = parsed_config.included_artifacts[0]
        self.assertIsInstance(first_artifact, IncludedArtifactEntry)
        self.assertEqual(first_artifact.artifact_name, 'dockertest')
        self.assertEqual(first_artifact.artifact_type, 'docker-image')
        self.assertEqual(first_artifact.path, 'Images/docker.tar')
        self.assertEqual(first_artifact.items, [])
        second_artifact = parsed_config.included_artifacts[1]
        self.assertIsInstance(second_artifact, IncludedArtifactEntry)
        self.assertEqual(second_artifact.artifact_name, 'glancetest')
        self.assertEqual(second_artifact.artifact_type, 'glance-image')
        self.assertEqual(second_artifact.path, 'Images/glance.tar')
        self.assertEqual(second_artifact.items, [])

    def test_parse_included_artefacts(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'includedArtefacts': [
                {
                    'name': 'dockertest',
                    'type': 'docker-image',
                    'path': 'Images/docker.tar'
                }
            ],
            'includedArtifacts': [
                {
                    'name': 'glancetest',
                    'type': 'glance-image',
                    'path': 'Images/glance.tar'
                }
            ]
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertEqual(len(parsed_config.included_artifacts), 2)
        first_artifact = parsed_config.included_artifacts[0]
        self.assertIsInstance(first_artifact, IncludedArtifactEntry)
        self.assertEqual(first_artifact.artifact_name, 'dockertest')
        self.assertEqual(first_artifact.artifact_type, 'docker-image')
        self.assertEqual(first_artifact.path, 'Images/docker.tar')
        self.assertEqual(first_artifact.items, [])
        second_artifact = parsed_config.included_artifacts[1]
        self.assertIsInstance(second_artifact, IncludedArtifactEntry)
        self.assertEqual(second_artifact.artifact_name, 'glancetest')
        self.assertEqual(second_artifact.artifact_type, 'glance-image')
        self.assertEqual(second_artifact.path, 'Images/glance.tar')
        self.assertEqual(second_artifact.items, [])
        
    def test_parsed_included_artifacts_wildcard_items(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'includedArtifacts': [
                {
                    'name': 'dirtest',
                    'type': 'k8s-resources',
                    'path': 'a_directory',
                    'items': '*'
                }
            ]
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertEqual(len(parsed_config.included_artifacts), 1)
        first_artifact = parsed_config.included_artifacts[0]
        self.assertIsInstance(first_artifact, IncludedArtifactEntry)
        self.assertEqual(first_artifact.artifact_name, 'dirtest')
        self.assertEqual(first_artifact.artifact_type, 'k8s-resources')
        self.assertEqual(first_artifact.path, 'a_directory')
        self.assertEqual(len(first_artifact.items), 1)
        self.assertIsInstance(first_artifact.items[0], ArtifactDirectoryItem)
        self.assertEqual(first_artifact.items[0].path, '*')
        self.assertTrue(first_artifact.items[0].is_wildcard)
    
    def test_parsed_included_artifacts_with_named_items(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'includedArtifacts': [
                {
                    'name': 'dirtest',
                    'type': 'k8s-resources',
                    'path': 'a_directory',
                    'items': [
                        'itemA',
                        'itemB'
                    ]
                }
            ]
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertEqual(len(parsed_config.included_artifacts), 1)
        first_artifact = parsed_config.included_artifacts[0]
        self.assertIsInstance(first_artifact, IncludedArtifactEntry)
        self.assertEqual(first_artifact.artifact_name, 'dirtest')
        self.assertEqual(first_artifact.artifact_type, 'k8s-resources')
        self.assertEqual(first_artifact.path, 'a_directory')
        self.assertEqual(len(first_artifact.items), 2)
        self.assertIsInstance(first_artifact.items[0], ArtifactDirectoryItem)
        self.assertEqual(first_artifact.items[0].path, 'itemA')
        self.assertFalse(first_artifact.items[0].is_wildcard)
        self.assertIsInstance(first_artifact.items[1], ArtifactDirectoryItem)
        self.assertEqual(first_artifact.items[1].path, 'itemB')
        self.assertFalse(first_artifact.items[1].is_wildcard)

    def test_parsed_included_artifacts_with_named_items_and_wildcard(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'includedArtifacts': [
                {
                    'name': 'dirtest',
                    'type': 'k8s-resources',
                    'path': 'a_directory',
                    'items': [
                        'itemA',
                        '*',
                        'itemB'
                    ]
                }
            ]
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertEqual(len(parsed_config.included_artifacts), 1)
        first_artifact = parsed_config.included_artifacts[0]
        self.assertIsInstance(first_artifact, IncludedArtifactEntry)
        self.assertEqual(first_artifact.artifact_name, 'dirtest')
        self.assertEqual(first_artifact.artifact_type, 'k8s-resources')
        self.assertEqual(first_artifact.path, 'a_directory')
        self.assertEqual(len(first_artifact.items), 3)
        self.assertIsInstance(first_artifact.items[0], ArtifactDirectoryItem)
        self.assertEqual(first_artifact.items[0].path, 'itemA')
        self.assertFalse(first_artifact.items[0].is_wildcard)
        self.assertIsInstance(first_artifact.items[1], ArtifactDirectoryItem)
        self.assertEqual(first_artifact.items[1].path, '*')
        self.assertTrue(first_artifact.items[1].is_wildcard)
        self.assertIsInstance(first_artifact.items[2], ArtifactDirectoryItem)
        self.assertEqual(first_artifact.items[2].path, 'itemB')
        self.assertFalse(first_artifact.items[2].is_wildcard)

    def test_parsed_subprojects_with_included_artifacts(self):
        valid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'contains': [
                {
                    'name': 'SubA',
                    'directory': 'SubA',
                    'type': 'Resource',
                    'resource-manager': 'brent',
                    'includedArtifacts': [
                        {
                            'name': 'dockertest',
                            'type': 'docker-image',
                            'path': 'Images/docker.tar'
                        },
                        {
                            'name': 'glancetest',
                            'type': 'glance-image',
                            'path': 'Images/glance.tar'
                        }
                    ]
                }
            ]
        }
        parsed_config = ProjectConfigParser.from_dict(valid_config)
        self.assertEqual(len(parsed_config.subproject_entries), 1)
        subA_entry = parsed_config.subproject_entries[0]
        self.assertEqual(len(subA_entry.included_artifacts), 2)
        first_artifact = subA_entry.included_artifacts[0]
        self.assertIsInstance(first_artifact, IncludedArtifactEntry)
        self.assertEqual(first_artifact.artifact_name, 'dockertest')
        self.assertEqual(first_artifact.artifact_type, 'docker-image')
        self.assertEqual(first_artifact.path, 'Images/docker.tar')
        self.assertEqual(first_artifact.items, [])
        second_artifact = subA_entry.included_artifacts[1]
        self.assertIsInstance(second_artifact, IncludedArtifactEntry)
        self.assertEqual(second_artifact.artifact_name, 'glancetest')
        self.assertEqual(second_artifact.artifact_type, 'glance-image')
        self.assertEqual(second_artifact.path, 'Images/glance.tar')
        self.assertEqual(second_artifact.items, [])

    def test_parsed_included_artifacts_with_duplicate_names(self):
        invalid_config = {
            'schema': '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'includedArtifacts': [
                {
                    'name': 'A',
                    'type': 'docker-image',
                    'path': 'Images/A.img'
                },
                {
                    'type': 'docker-image',
                    'path': 'Images/A.img'
                }
            ]
        }
        with self.assertRaises(ProjectConfigError) as context:
            ProjectConfigParser.from_dict(invalid_config)
        self.assertEqual(str(context.exception), 'Mulitple artifacts with name A. Set \"name\" for each entry to a unique value')
