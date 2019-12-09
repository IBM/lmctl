import unittest
import os
import tests.common.simulations.project_lab as project_lab
from tests.common.project_testing import ProjectSimTestCase, PKG_ARTIFACTS_DIR, PROJECT_CONTAINS_DIR
from lmctl.project.source.core import Project, BuildResult, BuildOptions
import lmctl.project.package.core as pkgs

class TestBuildProjectWithArtifacts(ProjectSimTestCase):

    def test_build(self):
        project_sim = self.simlab.simulate_gen_with_artifacts()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        result = project.build(build_options)
        self.assertIsInstance(result, BuildResult)
        self.assertFalse(result.validation_result.has_warnings())
        pkg = result.pkg
        self.assertIsNotNone(pkg)
        self.assertIsInstance(pkg, pkgs.Pkg)
        package_base_name = os.path.basename(pkg.path)
        self.assertEqual(package_base_name, 'with_artifacts-1.0.tgz')
        with self.assert_package(pkg) as pkg_tester:
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'with_artifacts',
                'version': '1.0',
                'type': 'Assembly',
                'includedArtifacts': [
                    {
                        'name': 'ImgZ',
                        'type': 'docker-image',
                        'path': 'ImgZ',
                        'items': [
                            'imgZ.txt'
                        ]
                    },
                    {
                        'name': 'ImgA',
                        'type': 'docker-image',
                        'path': 'ImgA',
                        'items': [
                            'imgA1.txt',
                            'imgA2.txt'
                        ]
                    },
                    {
                        'name': 'ImgB',
                        'type': 'docker-image',
                        'path': 'ImgB',
                        'items': [
                            'imgB4.txt',
                            'imgB1.txt',
                            'imgB3.txt',
                            'imgB2.txt'
                        ]
                    },
                    {
                        'name': 'ImgC',
                        'type': 'docker-image',
                        'path': 'ImgC',
                        'items': [
                            'imgC1.txt'
                        ]
                    }
                ]
            })
            pkg_tester.assert_has_directory(PKG_ARTIFACTS_DIR)
            pkg_tester.assert_has_directory(os.path.join(PKG_ARTIFACTS_DIR, 'ImgZ'))
            pkg_tester.assert_has_file(os.path.join(PKG_ARTIFACTS_DIR, 'ImgZ', 'imgZ.txt'), 'imgZ')
            pkg_tester.assert_has_directory(os.path.join(PKG_ARTIFACTS_DIR, 'ImgA'))
            pkg_tester.assert_has_file(os.path.join(PKG_ARTIFACTS_DIR, 'ImgA', 'imgA1.txt'), 'imgA1')
            pkg_tester.assert_has_file(os.path.join(PKG_ARTIFACTS_DIR, 'ImgA', 'imgA2.txt'), 'imgA2')
            pkg_tester.assert_has_directory(os.path.join(PKG_ARTIFACTS_DIR, 'ImgB'))
            pkg_tester.assert_has_file(os.path.join(PKG_ARTIFACTS_DIR, 'ImgB', 'imgB1.txt'), 'imgB1')
            pkg_tester.assert_has_file(os.path.join(PKG_ARTIFACTS_DIR, 'ImgB', 'imgB2.txt'), 'imgB2')
            pkg_tester.assert_has_file(os.path.join(PKG_ARTIFACTS_DIR, 'ImgB', 'imgB3.txt'), 'imgB3')
            pkg_tester.assert_has_file(os.path.join(PKG_ARTIFACTS_DIR, 'ImgB', 'imgB4.txt'), 'imgB4')
            pkg_tester.assert_has_directory(os.path.join(PKG_ARTIFACTS_DIR, 'ImgC'))
            pkg_tester.assert_has_file(os.path.join(PKG_ARTIFACTS_DIR, 'ImgC', 'imgC1.txt'), 'imgC1')
            pkg_tester.assert_has_no_file(os.path.join(PKG_ARTIFACTS_DIR, 'ImgC', 'imgC2.txt'))

    def test_build_subproject(self):
        project_sim = self.simlab.simulate_gen_contains_with_artifacts()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        result = project.build(build_options)
        self.assertIsInstance(result, BuildResult)
        self.assertFalse(result.validation_result.has_warnings())
        pkg = result.pkg
        self.assertIsNotNone(pkg)
        self.assertIsInstance(pkg, pkgs.Pkg)
        package_base_name = os.path.basename(pkg.path)
        self.assertEqual(package_base_name, 'contains_with_artifacts-1.0.tgz')
        with self.assert_package(pkg) as pkg_tester:
            pkg_tester.assert_has_meta({
                'schema': '2.0',
                'name': 'contains_with_artifacts',
                'version': '1.0',
                'type': 'Assembly',
                'contains': [
                    {
                        'name': 'sub_with_artifacts',
                        'type': 'Resource',
                        'directory': 'sub_with_artifacts', 
                        'resource-manager': 'brent',
                        'includedArtifacts': [
                            {
                                'name': 'ImgZ',
                                'type': 'docker-image',
                                'path': 'ImgZ',
                                'items': [
                                    'imgZ.txt'
                                ]
                            },
                            {
                                'name': 'ImgA',
                                'type': 'docker-image',
                                'path': 'ImgA',
                                'items': [
                                    'imgA1.txt',
                                    'imgA2.txt'
                                ]
                            },
                            {
                                'name': 'ImgB',
                                'type': 'docker-image',
                                'path': 'ImgB',
                                'items': [
                                    'imgB4.txt',
                                    'imgB1.txt',
                                    'imgB3.txt',
                                    'imgB2.txt'
                                ]
                            },
                            {
                                'name': 'ImgC',
                                'type': 'docker-image',
                                'path': 'ImgC',
                                'items': [
                                    'imgC1.txt'
                                ]
                            }
                        ]
                    }
                ]
            })
            sub_artifacts_dir = os.path.join(PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_WITH_ARTIFACTS, PKG_ARTIFACTS_DIR)
            pkg_tester.assert_has_directory(sub_artifacts_dir)
            pkg_tester.assert_has_directory(os.path.join(sub_artifacts_dir, 'ImgZ'))
            pkg_tester.assert_has_file(os.path.join(sub_artifacts_dir, 'ImgZ', 'imgZ.txt'), 'imgZ')
            pkg_tester.assert_has_directory(os.path.join(sub_artifacts_dir, 'ImgA'))
            pkg_tester.assert_has_file(os.path.join(sub_artifacts_dir, 'ImgA', 'imgA1.txt'), 'imgA1')
            pkg_tester.assert_has_file(os.path.join(sub_artifacts_dir, 'ImgA', 'imgA2.txt'), 'imgA2')
            pkg_tester.assert_has_directory(os.path.join(sub_artifacts_dir, 'ImgB'))
            pkg_tester.assert_has_file(os.path.join(sub_artifacts_dir, 'ImgB', 'imgB1.txt'), 'imgB1')
            pkg_tester.assert_has_file(os.path.join(sub_artifacts_dir, 'ImgB', 'imgB2.txt'), 'imgB2')
            pkg_tester.assert_has_file(os.path.join(sub_artifacts_dir, 'ImgB', 'imgB3.txt'), 'imgB3')
            pkg_tester.assert_has_file(os.path.join(sub_artifacts_dir, 'ImgB', 'imgB4.txt'), 'imgB4')
            pkg_tester.assert_has_directory(os.path.join(sub_artifacts_dir, 'ImgC'))
            pkg_tester.assert_has_file(os.path.join(sub_artifacts_dir, 'ImgC', 'imgC1.txt'), 'imgC1')
            pkg_tester.assert_has_no_file(os.path.join(sub_artifacts_dir, 'ImgC', 'imgC2.txt'))