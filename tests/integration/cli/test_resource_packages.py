from .cli_test_base import CLIIntegrationTest
from typing import List, Any, Callable, Dict
from lmctl.cli.entry import cli
from lmctl.cli.format import TableFormat
from lmctl.client import TNCOClientHttpError
import os
import time

class TestResourcePackages(CLIIntegrationTest):

    def test_create_with_file(self):
        pkg_path = self.tester.build_resource_package_from(self.tester.test_file('dummy_resource'), self.tester.tmp_file('dummy_resource.zip'), suffix='resource-pkg-cmd-create-with-file')
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcepkg', '-e', 'default', '-f', pkg_path
            ])
        resource_descriptor = self.tester.load_descriptor_from(self.tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='resource-pkg-cmd-create-with-file')
        descriptor_name = resource_descriptor['name']
        self.assert_output(create_result, f'Created from package: {descriptor_name}')
    
    def test_create_without_file_fails(self):
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcepkg', '-e', 'default'
            ])
        self.assert_has_system_exit(create_result)
        expected_output = 'Usage: cli create resourcepkg [OPTIONS]'
        expected_output += '\nTry \'cli create resourcepkg --help\' for help.'
        expected_output += '\n\nError: Missing option \'-f\' / \'--file\'.'
        self.assert_output(create_result, expected_output)

    def test_update_with_file(self):
        pkg_path = self.tester.build_resource_package_from(self.tester.test_file('dummy_resource'), self.tester.tmp_file('dummy_resource.zip'), suffix='resource-pkg-cmd-update-with-file')
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcepkg', '-e', 'default', '-f', pkg_path
            ])
        resource_descriptor = self.tester.load_descriptor_from(self.tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='resource-pkg-cmd-update-with-file')
        descriptor_name = resource_descriptor['name']
        update_result = self.cli_runner.invoke(cli, [
            'update', 'resourcepkg', descriptor_name, '-e', 'default', '-f', pkg_path
            ])
        self.assert_no_errors(update_result)
        self.assert_output(update_result, f'Updated package for: {descriptor_name}')
    
    def test_update_without_file_fails(self):
        update_result = self.cli_runner.invoke(cli, [
            'update', 'resourcepkg', '-e', 'default', 'SomeName'
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update resourcepkg [OPTIONS] NAME'
        expected_output += '\nTry \'cli update resourcepkg --help\' for help.'
        expected_output += '\n\nError: Missing option \'-f\' / \'--file\'.'
        self.assert_output(update_result, expected_output)
    
    def test_update_without_name_fails(self):
        pkg_path = self.tester.build_resource_package_from(self.tester.test_file('dummy_resource'), self.tester.tmp_file('dummy_resource.zip'), suffix='resource-pkg-cmd-update-without-name')
        update_result = self.cli_runner.invoke(cli, [
            'update', 'resourcepkg', '-e', 'default', '-f', pkg_path
            ])
        self.assert_has_system_exit(update_result)
        expected_output = 'Usage: cli update resourcepkg [OPTIONS] NAME'
        expected_output += '\nTry \'cli update resourcepkg --help\' for help.'
        expected_output += '\n\nError: Missing argument \'NAME\'.'
        self.assert_output(update_result, expected_output)

    def test_delete_with_name(self):
        pkg_path = self.tester.build_resource_package_from(self.tester.test_file('dummy_resource'), self.tester.tmp_file('dummy_resource.zip'), suffix='resource-pkg-cmd-create-with-file')
        create_result = self.cli_runner.invoke(cli, [
            'create', 'resourcepkg', '-e', 'default', '-f', pkg_path
            ])
        resource_descriptor = self.tester.load_descriptor_from(self.tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='resource-pkg-cmd-create-with-file')
        descriptor_name = resource_descriptor['name']
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcepkg', '-e', 'default', descriptor_name
            ])
        self.assert_output(delete_result, f'Removed package for: {descriptor_name}')
        
    def _A_test_delete_with_ignore_missing(self):
        delete_result = self.cli_runner.invoke(cli, [
            'delete', 'resourcepkg', '-e', 'default', 'NonExistentObj', '--ignore-missing'
            ])

        self.assert_no_errors(delete_result)
        self.assert_output(delete_result, f'No Resource Package found with name NonExistentObj (ignoring)')