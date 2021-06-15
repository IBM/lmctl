import click.testing as click_testing
import traceback
import tempfile
import os
import shutil
import yaml
from typing import List, Any, Callable
from tests.integration.integration_test_base import IntegrationTest

class CLIIntegrationTest(IntegrationTest):

    def before_test(self):
        super().before_test()
        # Disable max diff on assertion failures
        self.maxDiff = None
        self.cli_runner = click_testing.CliRunner()

    def assert_output(self, result, expected_output):
        expected_output += '\n'
        self.assertEqual(result.output, expected_output)
        
    def assert_has_system_exit(self, result):
        self.assertNotEqual(result.exit_code, 0)
        etype, value, tb = result.exc_info
        if etype == SystemExit:
            pass
        else:
            etype, value, tb = result.exc_info
            exception_string = ''.join(traceback.format_exception(etype, value, tb, None))
            self.fail(f'Unexpected exception thrown: \n---\n{exception_string}\n---{result.output}')  

    def assert_no_errors(self, result):
        if result.exit_code != 0:
            if result.exc_info:
                etype, value, tb = result.exc_info
                exception_string = ''.join(traceback.format_exception(etype, value, tb, None))
                self.fail(f'Unexpected exception thrown: \n---\n{exception_string}\n---{result.output}')  
            else:
                self.assertEqual(result.exit_code, 0)
    
    def _find_in_list_output(self, parsed_list_output: List[Any], items_to_find: List[Any], matcher: Callable = None):
        still_finding = items_to_find.copy()
        for item in parsed_list_output:
            match = None
            for target in still_finding:
                if matcher is None:
                    if item == target:
                        match = target
                        break
                elif matcher(item, target):
                    match = target
                    break
            if match is not None:
                still_finding.remove(match)
        if len(still_finding) > 0:
            self.fail(f'Did not find the following items in the output: {still_finding}')

    @staticmethod
    def _build_check_process_success(tester):
        def check_process_success(process_id: str) -> bool:
            process = tester.default_client.processes.get(process_id)
            status = process.get('status')
            if status in ['Completed']:
                return True
            elif status in ['Cancelled', 'Failed']:
                reason = process.get('statusReason')
                raise Exception(f'Process failed with status {status}, reason: {reason}')
            else:
                return False
        return check_process_success
