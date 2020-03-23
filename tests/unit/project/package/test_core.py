import unittest
import tempfile
import tarfile
import shutil
import os
from tests.common.project_testing import ProjectSimTestCase, PKG_META_YML_FILE, PKG_CONTENT_DIR
from lmctl.project.package.core import Pkg, PkgContent

class TestPkg(ProjectSimTestCase):

    def test_extract(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_basic()
        pkg = Pkg(pkg_sim.path)
        tmp_dir = tempfile.mkdtemp()
        try:
            pkg.extract(tmp_dir)
            self.assertTrue(os.path.exists(os.path.join(tmp_dir, PKG_META_YML_FILE)))
            self.assertTrue(os.path.exists(os.path.join(tmp_dir, PKG_CONTENT_DIR)))
        finally:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)

    def test_open(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_basic()
        pkg = Pkg(pkg_sim.path)
        tmp_dir = tempfile.mkdtemp()
        try:
            content = pkg.open(tmp_dir)
            self.assertIsInstance(content, PkgContent)
            self.assertTrue(os.path.exists(os.path.join(tmp_dir, PKG_META_YML_FILE)))
            self.assertTrue(os.path.exists(os.path.join(tmp_dir, PKG_CONTENT_DIR)))
        finally:
            if os.path.exists(tmp_dir):
                shutil.rmtree(tmp_dir)

    def test_inspect(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_basic()
        pkg = Pkg(pkg_sim.path)
        inspection_report = pkg.inspect()
        self.assertEqual(inspection_report.name, 'basic')
        self.assertEqual(inspection_report.version, '1.0')
        self.assertEqual(len(inspection_report.includes), 1)
        first_include = inspection_report.includes[0]
        self.assertEqual(first_include.name, 'basic')
        self.assertEqual(first_include.descriptor_name, 'assembly::basic::1.0')
        self.assertIsNone(first_include.resource_manager)

    def test_inspect_with_subcontent(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_brent_basic()
        pkg = Pkg(pkg_sim.path)
        inspection_report = pkg.inspect()
        self.assertEqual(inspection_report.name, 'contains_basic')
        self.assertEqual(inspection_report.version, '1.0')
        self.assertEqual(len(inspection_report.includes), 2)
        first_include = inspection_report.includes[0]
        self.assertEqual(first_include.name, 'contains_basic')
        self.assertEqual(first_include.descriptor_name, 'assembly::contains_basic::1.0')
        self.assertIsNone(first_include.resource_manager)
        second_include = inspection_report.includes[1]
        self.assertEqual(second_include.name, 'sub_basic-contains_basic')
        self.assertEqual(second_include.descriptor_name, 'resource::sub_basic-contains_basic::1.0')
        self.assertEqual(second_include.resource_manager, 'brent')
        
