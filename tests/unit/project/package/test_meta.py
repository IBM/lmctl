import unittest
import tempfile
import os
import yaml
import shutil
from lmctl.project.package.meta import PkgMetaRewriter

OLD_STYLE_META = """\
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

NEW_STYLE_META = """\
schema: '2.0'
name: testproject
version: '0.8'
contains:
- name: vnfcA
  type: Resource
  directory: vnfcA
  resource-manager: ansible-rm
  full-name-override: vnfcA
- name: vnfcB
  type: Resource
  directory: vnfcB
  resource-manager: ansible-rm
  full-name-override: vnfcB
"""

OLD_STYLE_NO_VNFCS = """\
name: testproject
vnfcs: 
  definitions: {}
  packages: {}
"""

NEW_STYLE_NO_VNFCS = """\
schema: '2.0'
name: testproject
version: '1.0'
contains: []
"""


class TestPkgMetaRewriter(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if self.tmp_dir and os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def test_rewrite(self):
        file_path = os.path.join(self.tmp_dir, 'rewrite.yml')
        new_path = os.path.join(self.tmp_dir, 'new_rewrite.yml')
        with open(file_path, 'w') as f:
            f.write(OLD_STYLE_META)
        old_config_dict = yaml.safe_load(OLD_STYLE_META)
        new_config_dict = PkgMetaRewriter(file_path, new_path, old_config_dict, '0.8').rewrite()
        expected_new_config_dict = {
            'schema': '2.0',
            'name': 'testproject',
            'version': '0.8',
            'contains': [
                {
                    'name': 'vnfcA',
                    'type': 'Resource',
                    'directory': 'vnfcA',
                    'resource-manager': 'ansible-rm',
                    'full-name-override': 'vnfcA'
                },
                {
                    'name': 'vnfcB',
                    'type': 'Resource',
                    'directory': 'vnfcB',
                    'resource-manager': 'ansible-rm',
                    'full-name-override': 'vnfcB'
                }
            ]
        }
        self.assertDictEqual(new_config_dict, expected_new_config_dict)
        backup_path = os.path.join(self.tmp_dir, 'rewrite.yml.bak')
        self.assertTrue(os.path.exists(backup_path))
        with open(backup_path, 'r') as f:
            backup_config = f.read()
        self.assertEqual(backup_config, OLD_STYLE_META)
        with open(new_path, 'r') as f:
            new_config = f.read()
        self.assertEqual(new_config, NEW_STYLE_META)

    
    def test_rewrite_no_vnfcs(self):
        file_path = os.path.join(self.tmp_dir, 'rewrite.yml')
        new_path = os.path.join(self.tmp_dir, 'new_rewrite.yml')
        with open(file_path, 'w') as f:
            f.write(OLD_STYLE_NO_VNFCS)
        old_config_dict = yaml.safe_load(OLD_STYLE_NO_VNFCS)
        new_config_dict = PkgMetaRewriter(file_path, new_path, old_config_dict).rewrite()
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
        with open(new_path, 'r') as f:
            new_config = f.read()
        self.assertEqual(new_config, NEW_STYLE_NO_VNFCS)

    