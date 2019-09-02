import unittest
import tempfile
import shutil
import os
from tests.common.project_testing import (ProjectSimTestCase, PROJECT_CONTAINS_DIR, ARM_DESCRIPTOR_DIR, 
                                            ARM_LIFECYCLE_DIR, ARM_METAINF_DIR, ARM_MANIFEST_FILE, ARM_TEST_DIR)
from lmctl.project.source.creator import CreateResourceProjectRequest, ResourceSubprojectRequest, ProjectCreator, CreateOptions
from lmctl.project.source.core import Project

class TestCreateAnsibleRmProjects(ProjectSimTestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_create_defaults(self):
        request = CreateResourceProjectRequest()
        request.name = 'Test'
        request.target_location = self.tmp_dir
        request.resource_manager = 'ansiblerm'
        creator = ProjectCreator(request, CreateOptions())
        creator.create()
        project = Project(self.tmp_dir)
        tester = self.assert_project(project)
        tester.assert_has_file(os.path.join(ARM_DESCRIPTOR_DIR, 'Test.yml'), 'description: descriptor for Test')
        tester.assert_has_directory(ARM_LIFECYCLE_DIR)
        tester.assert_has_file(os.path.join(ARM_METAINF_DIR, ARM_MANIFEST_FILE), 'resource-manager: ansible')
        tester.assert_has_directory(ARM_TEST_DIR)
        tester.assert_has_config({
            'schema':  '2.0',
            'name': 'Test',
            'version': '1.0',
            'type': 'Resource',
            'resource-manager': 'ansiblerm'
        })
    
    def test_create(self):
        request = CreateResourceProjectRequest()
        request.name = 'Test'
        request.target_location = self.tmp_dir
        request.resource_manager = 'ansiblerm'
        request.version = '9.9'
        creator = ProjectCreator(request, CreateOptions())
        creator.create()
        project = Project(self.tmp_dir)
        tester = self.assert_project(project)
        tester.assert_has_file(os.path.join(ARM_DESCRIPTOR_DIR, 'Test.yml'), 'description: descriptor for Test')
        tester.assert_has_directory(ARM_LIFECYCLE_DIR)
        tester.assert_has_file(os.path.join(ARM_METAINF_DIR, ARM_MANIFEST_FILE), 'resource-manager: ansible')
        tester.assert_has_directory(ARM_TEST_DIR)
        tester.assert_has_config({
            'schema':  '2.0',
            'name': 'Test',
            'version': '9.9',
            'type': 'Resource',
            'resource-manager': 'ansiblerm'
        })

    def test_create_with_subprojects(self):
        request = CreateResourceProjectRequest()
        request.name = 'Test'
        request.target_location = self.tmp_dir
        request.resource_manager = 'ansiblerm'
        request.version = '9.9'
        subprojectA_request = ResourceSubprojectRequest()
        subprojectA_request.name = 'SubA'
        subprojectA_request.directory = 'SubprojectA'
        subprojectA_request.resource_manager = 'ansiblerm'
        request.subproject_requests.append(subprojectA_request)
        subprojectB_request = ResourceSubprojectRequest()
        subprojectB_request.name = 'SubB'
        subprojectB_request.directory = 'SubprojectB'
        subprojectB_request.resource_manager = 'ansiblerm'
        request.subproject_requests.append(subprojectB_request)
        creator = ProjectCreator(request, CreateOptions())
        creator.create()
        project = Project(self.tmp_dir)
        tester = self.assert_project(project)
        tester.assert_has_file(os.path.join(ARM_DESCRIPTOR_DIR, 'Test.yml'), 'description: descriptor for Test')
        tester.assert_has_directory(ARM_LIFECYCLE_DIR)
        tester.assert_has_file(os.path.join(ARM_METAINF_DIR, ARM_MANIFEST_FILE), 'resource-manager: ansible')
        tester.assert_has_directory(ARM_TEST_DIR)
        tester.assert_has_config({
            'schema':  '2.0',
            'name': 'Test',
            'version': '9.9',
            'type': 'Resource',
            'resource-manager': 'ansiblerm',
            'contains': [
                {
                    'name': 'SubA',
                    'directory': 'SubprojectA',
                    'type': 'Resource',
                    'resource-manager': 'ansiblerm'
                },
                {
                    'name': 'SubB',
                    'directory':  'SubprojectB',
                    'type': 'Resource',
                    'resource-manager': 'ansiblerm'
                }
            ]
        })
        tester.assert_has_directory(PROJECT_CONTAINS_DIR)
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA'))
        tester.assert_has_file(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA', ARM_DESCRIPTOR_DIR, 'SubA.yml'), 'description: descriptor for SubA')
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA', ARM_LIFECYCLE_DIR))
        tester.assert_has_file(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA', ARM_METAINF_DIR, ARM_MANIFEST_FILE), 'resource-manager: ansible')
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA', ARM_LIFECYCLE_DIR))
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectA', ARM_TEST_DIR))
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB'))
        tester.assert_has_file(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB', ARM_DESCRIPTOR_DIR, 'SubB.yml'), 'description: descriptor for SubB')
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB', ARM_LIFECYCLE_DIR))
        tester.assert_has_file(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB', ARM_METAINF_DIR, ARM_MANIFEST_FILE), 'resource-manager: ansible')
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB', ARM_LIFECYCLE_DIR))
        tester.assert_has_directory(os.path.join(PROJECT_CONTAINS_DIR, 'SubprojectB', ARM_TEST_DIR))