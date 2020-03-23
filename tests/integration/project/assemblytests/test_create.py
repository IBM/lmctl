import unittest
import tempfile
import shutil
import os
from tests.common.project_testing import (ProjectSimTestCase,
                                          PROJECT_CONTAINS_DIR, ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE, 
                                          ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 
                                          ASSEMBLY_RUNTIME_DIR, ASSEMBLY_TESTS_DIR)
from lmctl.project.source.creator import CreateAssemblyProjectRequest, AssemblySubprojectRequest, ProjectCreator, CreateOptions
from lmctl.project.source.core import Project

class TestCreateAssemblyProjects(ProjectSimTestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_create_defaults(self):
        request = CreateAssemblyProjectRequest()
        request.name = 'Test'
        request.target_location = self.tmp_dir
        creator = ProjectCreator(request, CreateOptions())
        creator.create()
        project = Project(self.tmp_dir)
        tester = self.assert_project(project)
        tester.assert_has_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), 'description: descriptor for Test')
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR))
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR))
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR))
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR))
        tester.assert_has_config({
            'schema':  '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Assembly',
            'packaging': 'tgz'
        })
        
    def test_create(self):
        request = CreateAssemblyProjectRequest()
        request.name = 'Test'
        request.target_location = self.tmp_dir
        request.version = '9.9'
        creator = ProjectCreator(request, CreateOptions())
        creator.create()
        project = Project(self.tmp_dir)
        tester = self.assert_project(project)
        tester.assert_has_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), 'description: descriptor for Test')
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR))
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR))
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR))
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR))
        tester.assert_has_config({
            'schema':  '2.0',
            'name': 'Test',
            'version': '9.9',
            'type': 'Assembly',
            'packaging': 'tgz'
        })

    def test_create_with_subprojects(self):
        request = CreateAssemblyProjectRequest()
        request.name = 'Test'
        request.target_location = self.tmp_dir
        request.version = '9.9'
        subprojectA_request = AssemblySubprojectRequest()
        subprojectA_request.name = 'SubA'
        subprojectA_request.directory = 'SubprojectA'
        request.subproject_requests.append(subprojectA_request)
        subprojectB_request = AssemblySubprojectRequest()
        subprojectB_request.name = 'SubB'
        subprojectB_request.directory = 'SubprojectB'
        request.subproject_requests.append(subprojectB_request)
        creator = ProjectCreator(request, CreateOptions())
        creator.create()
        project = Project(self.tmp_dir)
        tester = self.assert_project(project)
        tester.assert_has_file(os.path.join(ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), 'description: descriptor for Test')
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR))
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR))
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR))
        tester.assert_has_directory(os.path.join(ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR))
        tester.assert_has_config({
            'schema':  '2.0',
            'name': 'Test',
            'version': '9.9',
            'packaging': 'tgz',
            'type': 'Assembly',
            'contains': [
                {
                    'name': 'SubA',
                    'directory': 'SubprojectA',
                    'type': 'Assembly'
                },
                {
                    'name': 'SubB',
                    'directory':  'SubprojectB',
                    'type': 'Assembly'
                }
            ]
        })
        tester.assert_has_directory(PROJECT_CONTAINS_DIR)
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA'))
        tester.assert_has_file(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA', ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), 'description: descriptor for SubA')
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA', ASSEMBLY_BEHAVIOUR_DIR))
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA', ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR))
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA', ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR))
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA', ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR))
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB'))
        tester.assert_has_file(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB', ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE), 'description: descriptor for SubB')
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB', ASSEMBLY_BEHAVIOUR_DIR))
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB', ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR))
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB', ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR))
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB', ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR))
        