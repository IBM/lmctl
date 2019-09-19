import unittest
import traceback
import click.testing as click_testing
import lmctl.utils.logging as lmctl_logging

lmctl_logging.setup_logging()

class CommandTestCase(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.runner = click_testing.CliRunner()

    def assert_no_errors(self, result):
        if result.exit_code != 0:
            if result.exc_info:
                etype, value, tb = result.exc_info
                exception_string = ''.join(traceback.format_exception(etype, value, tb, None))
                self.fail('Unexpected exception thrown: \n---\n' + exception_string)  
            else:
                self.assertEqual(result.exit_code, 0)

    def assert_has_system_exit(self, result):
        self.assertNotEqual(result.exit_code, 0)
        etype, value, tb = result.exc_info
        if etype == SystemExit:
            pass
        else:
            etype, value, tb = result.exc_info
            exception_string = ''.join(traceback.format_exception(etype, value, tb, None))
            self.fail('Unexpected exception thrown: \n---\n' + exception_string)

    def assert_output(self, result, expected_output):
        expected_output += '\n'
        self.assertEqual(result.output, expected_output)