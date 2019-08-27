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
        
    def test_extract_non_tar_pkg(self):
        pkg_sim = self.simlab.simulate_pkg_general_invalid_zip()
        pkg = Pkg(pkg_sim.path)
        tmp_dir = tempfile.mkdtemp()
        try:
            with self.assertRaises(tarfile.ReadError) as context:
                pkg.extract(tmp_dir)
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