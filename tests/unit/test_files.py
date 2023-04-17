import unittest
import tempfile
import os
import shutil
import tarfile

from lmctl.files import safely_extract_tar

class TestFileUtils(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.tmp_dir = tempfile.mkdtemp()

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            pass#shutil.rmtree(self.tmp_dir)

    def _alter_tar_info_to_appear_outside_dir(self, tarinfo):
        tarinfo.name = os.path.join('..', tarinfo.name)
        return tarinfo
    
    def test_safely_extract_tar_allows_files_that_do_not_navigate_outside_parent_directory(self):
        # Create Files for TAR
        file_A = os.path.join(self.tmp_dir, 'fileA.txt')
        with open(file_A, 'w') as f:
            f.write('TestA')
        file_B = os.path.join(self.tmp_dir, 'fileB.txt')
        with open(file_B, 'w') as f:
            f.write('TestB')
        # Create a TAR containing a file with safe paths
        # ./
        #   fileA.txt
        #   DirB/
        #     fileB1.txt
        tar_path = os.path.join(self.tmp_dir, 'test.tar')
        with tarfile.open(tar_path, 'w:xz') as tar:
            tar.add(file_A, arcname='fileA.txt')
            tar.add(file_B, arcname=os.path.join('DirB', 'fileB.txt'))

        extraction_path = os.path.join(self.tmp_dir, 'extraction')
        with tarfile.open(tar_path, 'r') as tar:
            safely_extract_tar(tar, extraction_path)

        self.assertTrue(os.path.exists(os.path.join(extraction_path, 'fileA.txt')))
        self.assertTrue(os.path.exists(os.path.join(extraction_path, 'DirB', 'fileB.txt')))

    def test_safely_extract_tar_catches_malicious_file(self):
        # Create a TAR containing a file with an unsafe path 
        file_name = 'dummy-file.txt'
        file_path = os.path.join(self.tmp_dir, file_name)
        with open(file_path, 'w') as f:
            f.write('Test')
        tar_path = os.path.join(self.tmp_dir, 'test.tar')
        with tarfile.open(tar_path, 'w:xz') as tar:
            tar.add(file_path, filter=self._alter_tar_info_to_appear_outside_dir)

        with tarfile.open(tar_path, 'r') as tar:
            with self.assertRaises(ValueError) as ctx:
                safely_extract_tar(tar, self.tmp_dir)
        
        expected_path_in_error = '..' + self.tmp_dir + os.sep + file_name
        self.assertEqual(str(ctx.exception), f'TAR contains a file which attempts to traverse to a path outside of the target extraction path: {expected_path_in_error}')