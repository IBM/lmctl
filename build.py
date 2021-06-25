import os
import subprocess
import sys
import shutil
import json
import argparse
import git
import getpass
import time
import platform

PKG_ROOT = 'lmctl'
PKG_INFO = 'pkg_info.json'
DIST_DIR = 'dist'
WHL_FORMAT = 'lmctl-{version}-py3-none-any.whl'
DOCS_FORMAT = 'lmctl-{version}-docs'
DOCS_DIR = 'docs'
DOCKER_IMG_TAG = 'accanto/lmctl-jnlp-slave:{version}'
DOCKER_IMG_PATH = os.path.join('docker', 'jenkins-jnlp-slave')

parser=argparse.ArgumentParser()

parser.add_argument('--release', default=False, action='store_true')
parser.add_argument('--version', help='version to set for the release')
parser.add_argument('--post-version', help='version to set after the release')
parser.add_argument('--pypi-user', help='user for uploading to Pypi')
parser.add_argument('--pypi-pass', help='password for user uploading to Pypi')

args = parser.parse_args()
 
class BuildError(Exception):
    pass

class BuildVariables:

    def __init__(self):
        version = None
        post_version = None
        pypi_user = None
        pypi_pass = None

class Secret:

    def __init__(self, value):
        self.value = value

class Stage:

    def __init__(self, builder, title):
        self.builder = builder
        self.title = title
        self.exit_reason = None
        self.exit_code = 0

    def __enter__(self):
        print('================================================')
        print('{0}'.format(self.title))
        print('================================================')
        return self

    def __exit__(self, type, err_value, traceback):
        if err_value != None:
            # Legit python error thrown
            print('ERROR: {0}\n'.format(str(err_value)))
            self.exit_code = 1
            self.exit_reason = str(err_value)
            try:
                self.builder.report()
            except e:
                pass
            return    
        if self.exit_code != 0:
            if self.exit_reason != None:
                print(self.exit_reason)
            self.builder.report()
            exit(self.exit_code)
        else:
            print('')

    def _cmd_exit(self, exit_code):
        self.exit_code = exit_code

    def exit_with_error(self, exit_code, reason):
        self.exit_reason = reason
        self.exit_code = exit_code

    def parse_cmd(self, cmd):
        parsed_cmd = []
        printout = []
        for item in cmd:
            if isinstance(item, Secret):
                printout.append('***')
                parsed_cmd.append(item.value)
            else:
                printout.append(item)
                parsed_cmd.append(item)
        print('Executing: {0}'.format(' '.join(printout)))
        return parsed_cmd

    def run_cmd(self, *cmd):
        cmd = self.parse_cmd(cmd)
        working_dir = self.builder.project_path if self.builder.project_path != None and self.builder.project_path != '' else None
        process = subprocess.Popen(cmd, stdout=sys.stdout, stderr=sys.stderr, cwd=working_dir)
        process.communicate()
        if process.returncode != 0:
            return self._cmd_exit(process.returncode)

class Builder:

    def __init__(self):
        self.project_path = os.path.dirname(__file__)
        self.project_path_is_current_dir = False
        if self.project_path == None or self.project_path == '':
            self.project_path_is_current_dir = True
        self.stages = []
        self.args_to_vars()
        
    def args_to_vars(self):
        self.vars = BuildVariables()
        self.vars.version = args.version
        self.vars.post_version = args.post_version
        self.vars.pypi_user = args.pypi_user
        self.vars.pypi_pass = args.pypi_pass

    def report(self):
        print('================================================')
        print('Build Result')
        print('================================================')
        for s in self.stages:
            if s.exit_code == 0:
                print('  {0} - OK'.format(s.title))
            else:
                print('  {0} - FAILED'.format(s.title))
        print(' ')

    def stage(self, title):
        stage = Stage(self, title)
        self.stages.append(stage)
        return stage

    def _establish_who_we_are(self):
        if self.project_path_is_current_dir:
            print('Building at: ./')
        else:
            print('Building at: {0}'.format(self.project_path))

    def doIt(self):
        self._establish_who_we_are()
        if args.release == True:
            self.release()
        else:
            self.build()
        self.report()

    def build(self):
        self.determine_version()
        self.run_unit_tests()
        self.build_python_wheel()
        self.pkg_docs()

    def release(self):
        if self.vars.version is None:
            raise ValueError('Must set --version when releasing')
        if self.vars.post_version is None:
            raise ValueError('Must set --post-version when releasing')
        self.set_version()
        self.build()
        self.push_whl()
        print('Waiting 5 seconds for Pypi to update....')
        # Give the whl some time to be indexed on pypi
        time.sleep(5)
        self.build_jnlp_docker_image() # Requires the whl to have been pushed
        self.push_jnlp_docker_image()
        self.push_release_git_changes()
        self.set_post_version()
        self.push_post_release_git_changes()

    def get_pypi_details(self):
        if self.vars.pypi_user is None:
            self.vars.pypi_user = input('Pypi Username: ')
        if self.vars.pypi_pass is None:
            self.vars.pypi_pass = getpass.getpass('Pypi Password:')

    def set_version(self):
        with self.stage('Setting Release Version') as s:
            pkg_info_path = os.path.join(self.project_path, PKG_ROOT, PKG_INFO)
            print('Setting version in {0} to {1}'.format(pkg_info_path, self.vars.version))
            with open(pkg_info_path, 'r') as f:
                pkg_info_data = json.load(f)
            pkg_info_data['version'] = self.vars.version
            with open(pkg_info_path, 'w') as f:
                json.dump(pkg_info_data, f)            
                
    def run_unit_tests(self):
        with self.stage('Run Unit Tests') as s:
            s.run_cmd('python3', '-m', 'unittest', 'discover', '-s', 'tests.unit')

    def build_python_wheel(self):
        with self.stage('Build Wheel') as s:
            print('Cleaning directory: {0}'.format(DIST_DIR))
            dist_path = os.path.join(self.project_path, DIST_DIR)
            if os.path.exists(dist_path):
                shutil.rmtree(dist_path)
            s.run_cmd('python3', 'setup.py', 'bdist_wheel')

    def set_post_version(self):
        with self.stage('Setting Post Release Version') as s:
            pkg_info_path = os.path.join(self.project_path, PKG_ROOT, PKG_INFO)
            print('Setting version in {0} to {1}'.format(pkg_info_path, self.vars.post_version))
            with open(pkg_info_path, 'r') as f:
                pkg_info_data = json.load(f)
            pkg_info_data['version'] = self.vars.post_version
            with open(pkg_info_path, 'w') as f:
                json.dump(pkg_info_data, f)
            
    def push_release_git_changes(self):
        with self.stage('Commit Release Changes') as s:
            repo = git.Repo(self.project_path)
            repo.index.add([os.path.join(PKG_ROOT, PKG_INFO)])
            repo.index.commit('Update version for release')
            if self.vars.version in repo.tags:
                repo.delete_tag(self.vars.version)
            repo.create_tag(self.vars.version)

    def push_post_release_git_changes(self):
        with self.stage('Commit Post Release Changes') as s:
            repo = git.Repo(self.project_path)
            repo.index.add([os.path.join(PKG_ROOT, PKG_INFO)])
            repo.index.commit('Update version for development')
            origin = repo.remote('origin')
            origin.push()
            origin.push(tags=True)

    def push_whl(self):
        with self.stage('Push Whl to Pypi') as s:
            self.get_pypi_details()
            whl_path = os.path.join(self.project_path, DIST_DIR, WHL_FORMAT.format(version=self.vars.version))
            s.run_cmd('python3', '-m', 'twine', 'upload', whl_path, '-u', self.vars.pypi_user, '-p', Secret(self.vars.pypi_pass))

    def determine_version(self):
        with self.stage('Gathering Version') as s:
            pkg_info_path = os.path.join(self.project_path, PKG_ROOT, PKG_INFO)
            print('Reading version from {0}'.format(pkg_info_path))
            with open(pkg_info_path, 'r') as f:
                pkg_info_data = json.load(f)
            if 'version' not in pkg_info_data:
                return s.exit_with_error('\'version\' not found in {0}'.format(pkg_info_path))
            else:
                self.vars.version = pkg_info_data['version']
                print('Found version is: {0}'.format(self.vars.version))

    def pkg_docs(self):
        with self.stage('Package Docs') as s:
            print('Packaging docs at {0}'.format(DOCS_DIR))
            docs_output = DOCS_FORMAT.format(version=self.vars.version)
            docs_output_file = docs_output + '.tgz'
            transform_command = 's/{0}/{1}/'.format(DOCS_DIR, docs_output)
            # Note that a system running on Mac will return 'Darwin' for platform.system()
            if platform.system() == 'Darwin':
                transform_command = '/{0}/{1}/'.format(DOCS_DIR, docs_output)           
                s.run_cmd('tar', '-cvz', '-s', transform_command, '-f', docs_output_file, DOCS_DIR+'/')
            else:
                s.run_cmd('tar', '-cvzf', docs_output_file, DOCS_DIR+'/', '--transform', transform_command)

            
    def build_jnlp_docker_image(self):
        with self.stage('Build JNLP Slave Docker Image') as s:
            img_tag = DOCKER_IMG_TAG.format(version=self.vars.version)
            s.run_cmd('docker', 'build', '--build-arg', 'LMCTL_VERSION={version}'.format(version=self.vars.version), '-t', img_tag, DOCKER_IMG_PATH)

    def push_jnlp_docker_image(self):
        with self.stage('Push JNLP Slave Docker Image') as s:
            img_tag = DOCKER_IMG_TAG.format(version=self.vars.version)
            s.run_cmd('docker', 'push', img_tag)

def main():
  builder = Builder()
  builder.doIt()

if __name__== "__main__":
  main()

