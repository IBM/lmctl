import unittest
import unittest.mock as mock
import os
from lmctl.project.source.core import Project, Options, ValidateOptions, BuildOptions, PullOptions, InvalidProjectError, ProjectBaseTree, ProjectTree, SubprojectTree
from lmctl.project.source.config import RootProjectConfig
from lmctl.project.handlers.assembly import AssemblySourceHandler
from lmctl.project.handlers.resource import ResourceSourceHandler
from tests.common.project_testing import ProjectSimTestCase, PROJECT_CONTAINS_DIR, PROJECT_FILE_YML, PROJECT_FILE_YAML


class TestOptions(unittest.TestCase):

    def test_has_journal_consumer(self):
        self.assertTrue(hasattr(Options(), 'journal_consumer'))
        self.assertTrue(hasattr(ValidateOptions(), 'journal_consumer'))
        self.assertTrue(hasattr(BuildOptions(), 'journal_consumer'))
        self.assertTrue(hasattr(PullOptions(), 'journal_consumer'))

class TestProject(ProjectSimTestCase):

    def test_init_throws_error_when_root_path_not_provided(self):
        with self.assertRaises(ValueError) as context:
            Project(None)
        self.assertEqual(str(context.exception), 'root_path must be provided for a Project')

    def test_init_assembly(self):
        assembly_project_sim = self.simlab.simulate_assembly_basic()
        assembly_project = Project(assembly_project_sim.path)
        self.assertTrue(isinstance(assembly_project.tree, ProjectTree))
        self.assertTrue(isinstance(assembly_project.config, RootProjectConfig))
        self.assertTrue(isinstance(assembly_project.source_handler, AssemblySourceHandler))
        self.assertEqual(assembly_project.source_handler.root_path, assembly_project.tree.root_path)
        self.assertEqual(assembly_project.source_handler.source_config, assembly_project.config)

    def test_init_resource(self):
        resource_project_sim = self.simlab.simulate_arm_basic()
        resource_project = Project(resource_project_sim.path)
        self.assertTrue(isinstance(resource_project.tree, ProjectTree))
        self.assertTrue(isinstance(resource_project.config, RootProjectConfig))
        self.assertTrue(isinstance(resource_project.source_handler, ResourceSourceHandler))
        self.assertEqual(resource_project.source_handler.root_path, resource_project.tree.root_path)
        self.assertEqual(resource_project.source_handler.source_config, resource_project.config)

    def test_init_missing_projectfile(self):
        project_sim = self.simlab.simulate_assembly_basic()
        project_file_path = os.path.join(project_sim.path, PROJECT_FILE_YML)
        os.remove(project_file_path)
        with self.assertRaises(InvalidProjectError) as context:
            Project(project_sim.path)
        self.assertEqual(str(context.exception), 'Could not find project file at path: {0}'.format(project_file_path))

    @mock.patch('lmctl.project.source.core.project_journal.ProjectJournal')
    @mock.patch('lmctl.project.source.core.validation_exec.ValidationProcess')
    def test_validate_uses_process(self, mock_validation_process_init, mock_proj_journal_init):
        project_sim = self.simlab.simulate_assembly_basic()
        project = Project(project_sim.path)
        mock_consumer = mock.MagicMock()
        options = ValidateOptions()
        options.journal_consumer = mock_consumer
        result = project.validate(options)
        mock_proj_journal_init.assert_called_once_with(mock_consumer)
        mock_proj_journal = mock_proj_journal_init.return_value
        mock_validation_process_init.assert_called_once_with(project, options, mock_proj_journal)
        mock_validation_process = mock_validation_process_init.return_value
        mock_validation_process.execute.assert_called_once()
        self.assertEqual(result, mock_validation_process.execute.return_value)


class TestProjectBaseTree(unittest.TestCase):

    def test_child_projects_path(self):
        tree = ProjectBaseTree()
        self.assertEqual(tree.child_projects_path, PROJECT_CONTAINS_DIR)
        tree = ProjectBaseTree('test')
        self.assertEqual(tree.child_projects_path, os.path.join('test', PROJECT_CONTAINS_DIR))

    def test_gen_child_project_path(self):
        tree = ProjectBaseTree()
        self.assertEqual(tree.gen_child_project_path('A'), os.path.join(PROJECT_CONTAINS_DIR, 'A'))
        tree = ProjectBaseTree('test')
        self.assertEqual(tree.gen_child_project_path('B'), os.path.join('test', PROJECT_CONTAINS_DIR, 'B'))

class TestProjectTree(ProjectSimTestCase):

    def test_extends_base(self):
        self.assertTrue(issubclass(ProjectTree, ProjectBaseTree))

    def test_project_file_name(self):
        tree = ProjectTree()
        self.assertEqual(tree.project_file_name, PROJECT_FILE_YML)
        tree = ProjectTree('test')
        self.assertEqual(tree.project_file_name, PROJECT_FILE_YML)

    def test_project_file_path(self):
        tree = ProjectTree()
        self.assertEqual(tree.project_file_path, PROJECT_FILE_YML)
        tree = ProjectTree('test')
        self.assertEqual(tree.project_file_path, os.path.join('test', PROJECT_FILE_YML))

    def test_project_file_name_detects_yaml(self):
        project_sim = self.simlab.simulate_assembly_with_yaml_project_file()
        tree = ProjectTree(project_sim.path)
        self.assertEqual(tree.project_file_name, PROJECT_FILE_YAML)

    def test_project_file_path_detects_yaml(self):
        project_sim = self.simlab.simulate_assembly_with_yaml_project_file()
        tree = ProjectTree(project_sim.path)
        self.assertEqual(tree.project_file_path, os.path.join(project_sim.path, PROJECT_FILE_YAML))

    def test_project_file_name_throws_error_when_yaml_and_yml_detected(self):
        project_sim = self.simlab.simulate_assembly_with_yaml_project_file()
        yml_path = os.path.join(project_sim.path, PROJECT_FILE_YML)
        with open(yml_path, 'w') as writer:
            pass
        tree = ProjectTree(project_sim.path)
        with self.assertRaises(InvalidProjectError) as context:
            tree.project_file_name
        self.assertEqual(str(context.exception), 'Project has both a {0} file and a {1} file when there should only be one'.format(PROJECT_FILE_YML, PROJECT_FILE_YAML))

    def test_project_file_path_throws_error_when_yaml_and_yml_detected(self):
        project_sim = self.simlab.simulate_assembly_with_yaml_project_file()
        yml_path = os.path.join(project_sim.path, PROJECT_FILE_YML)
        with open(yml_path, 'w') as writer:
            pass
        tree = ProjectTree(project_sim.path)
        with self.assertRaises(InvalidProjectError) as context:
            tree.project_file_path
        self.assertEqual(str(context.exception), 'Project has both a {0} file and a {1} file when there should only be one'.format(PROJECT_FILE_YML, PROJECT_FILE_YAML))


class TestSubprojectTree(unittest.TestCase):

    def test_extends_base(self):
        self.assertTrue(issubclass(SubprojectTree, ProjectBaseTree))

