import os
import shutil
import distutils.dir_util
import string
import unicodedata
import logging

logger = logging.getLogger(__name__)

class Tree:

    def __init__(self, root_path=None):
        if root_path is None:
            root_path = ''
        self.root_path = root_path

    def relative_path(self, *relative_paths):
        return os.path.join(*relative_paths)

    def resolve_relative_path(self, *relative_paths):
        return os.path.join(self.root_path, *relative_paths)


def clean_directory(directory_path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
    os.makedirs(directory_path)


def remove_directory(directory_path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)


def create_directories(*directories):
    for directory in directories:
        os.makedirs(directory)


def copy_file(src, dest):
    shutil.copy2(src, dest)


def copy_tree(src, dest):
    distutils.dir_util.copy_tree(src, dest, 0)


def immediate_sub_directories(parent_directory):
    sub_directory_paths = []
    for sub_name in os.listdir(parent_directory):
        sub_path = os.path.join(parent_directory, sub_name)
        if os.path.isdir(sub_path):
            sub_directory_paths.append(sub_path)
    return sub_directory_paths


valid_file_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)

filename_size_limit = 255


def safe_file_name(unsafe_filename):
    # remove spaces
    safe_filename = unsafe_filename.replace(' ', '_')
    # valid ascii
    safe_filename = unicodedata.normalize('NFKD', safe_filename).encode('ASCII', 'ignore').decode()
    # keep valid charts
    safe_filename = ''.join(char for char in safe_filename if char in valid_file_chars)
    if len(safe_filename) > filename_size_limit:
        logger.info("Filename over file name limit {0}, truncating characters. Filename may no longer be unique".format(filename_size_limit))
    return safe_filename[:filename_size_limit]

def is_in_directory(subject, target_dir):
    absolute_target_dir = os.path.abspath(target_dir)
    absolute_subject = os.path.abspath(subject)
    common_prefix = os.path.commonprefix([absolute_subject, absolute_target_dir])
    return common_prefix == absolute_target_dir

def safely_extract_tar(tar, target_path='.', *extract_args, **extract_kwargs):
    for member in tar.getmembers():
        ## Where the extracted file will end up
        anticipated_member_path = os.path.join(target_path, member.name)
        
        ## Verify the file will end up in the target directory
        ## The target file path should have the same prefix as the target directory, 
        ## as it should be the target directory, otherwise the file is being extracted to a different directory
        if not is_in_directory(anticipated_member_path, target_path):
            raise ValueError(f'TAR contains a file which attempts to traverse to a path outside of the target extraction path: {member.name}')
        
    tar.extractall(target_path, *extract_args, **extract_kwargs) 
