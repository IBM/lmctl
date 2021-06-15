import tests.unit.cli.commands.command_testing as command_testing
import lmctl.utils.logging as lmctl_logging
from lmctl.cli.commands.logdir import logdir

class TestLogdirCommand(command_testing.CommandTestCase):

    def test_logdir(self):
        expected_log_dir = str(lmctl_logging.log_dir())
        result = self.runner.invoke(logdir)
        self.assert_no_errors(result)
        self.assert_output(result, expected_log_dir)
        