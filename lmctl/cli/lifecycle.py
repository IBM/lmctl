import lmctl.journal as journal
import lmctl.project.journal as project_journal
import lmctl.project.source.core as project_sources
import lmctl.project.package.core as pkgs
import lmctl.cli.output as output
import lmctl.cli.ctlmgmt as ctlmgmt
import lmctl.drivers.lm.base as lm_drivers
import lmctl.drivers.arm as arm_drivers
import logging
from lmctl.project.sessions import EnvironmentSessions, EnvironmentSelectionError
from lmctl.project.types import ANSIBLE_RM_TYPES
from lmctl.client import TNCOClientError

logger = logging.getLogger(__name__)

FAILED = 'FAILED'
PASSED = 'PASSED'
PASSED_WITH_WARNINGS = 'PASSED (with warnings)'


def build_sessions_for_project(project_config, environment_name, lm_pwd=None, arm_name=None, config_path=None):
    lm_session = ctlmgmt.create_lm_session(environment_name, lm_pwd, config_path)
    if __has_arm_projects(project_config) and arm_name is not None:
        arm_session = ctlmgmt.create_arm_session(arm_name, environment_name, config_path)
    else:
        arm_session = None
    return EnvironmentSessions(lm_session, arm_session)

def __has_arm_projects(config):
    if config.resource_manager is not None and config.resource_manager in ANSIBLE_RM_TYPES:
        return True
    for subproject_entry in config.subproject_entries:
        found = __has_arm_projects(subproject_entry)
        if found:
            return True
    return False

def build_sessions_for_pkg(pkg_meta, environment_name, lm_pwd=None, arm_name=None, config_path=None):
    lm_session = ctlmgmt.create_lm_session(environment_name, lm_pwd, config_path)
    if __has_arm_content(pkg_meta) and arm_name is not None:
        arm_session = ctlmgmt.create_arm_session(arm_name, environment_name, config_path)
    else:
        arm_session = None
    return EnvironmentSessions(lm_session, arm_session)

def __has_arm_content(meta):
    if meta.resource_manager is not None and meta.resource_manager in ANSIBLE_RM_TYPES:
        return True
    for subcontent_entry in meta.subpkg_entries:
        found = __has_arm_content(subcontent_entry)
        if found:
            return True
    return False

def open_project(project_path):
    try:
        return project_sources.Project(project_path)
    except project_sources.InvalidProjectError as e:
        printer.print_text('Error: {0}'.format(str(e)))
        logger.exception(str(e))
        exit(1)

def get_pkg_and_open(pkg_path):
    try:
        pkg = pkgs.Pkg(pkg_path)
        return pkg, pkg.open()
    except pkgs.InvalidPackageError as e:
        printer.print_text('Error: {0}'.format(str(e)))
        logger.exception(str(e))
        exit(1)

def open_pkg(pkg_path):
    try:
        return pkgs.Pkg(pkg_path).open()
    except pkgs.InvalidPackageError as e:
        printer.print_text('Error: {0}'.format(str(e)))
        logger.exception(str(e))
        exit(1)

class Banner:

    def __init__(self, title):
        self.title = title

    def text(self, info=None):
        if info is None:
            return self.title
        return '{0} - {1}'.format(self.title, info)


class ProjectPrinter:

    def __init__(self):
        self.__sub_projects = []

    def inc_sub_project(self, name):
        self.__sub_projects.append(name)

    def dec_sub_project(self):
        if len(self.__sub_projects) > 0:
            del self.__sub_projects[-1]

    def __normalise_lines(self, lines):
        if type(lines) is str:
            return [lines]
        else:
            return lines

    def print_header(self, title):
        self.__print_root('===========================================================')
        self.__print_root(title)
        self.__print_root('===========================================================')

    def print_footer(self, title, lines=None):
        self.print_break()
        self.__print_root('===========================================================')
        self.__print_root(title)
        if lines is not None:
            lines = self.__normalise_lines(lines)
            for line in lines:
                self.__print_root('\t{0}'.format(line))
        self.__print_root('===========================================================')

    def print_warning(self, lines=None):
        self.print_break()
        self.__print('--- WARNING - --')
        if lines is not None:
            lines = self.__normalise_lines(lines)
            for line in lines:
                self.__print(line)
        else:
            self.__print('?')

    def print_section(self, section_name):
        self.print_break()
        self.__print('--> {0}'.format(section_name))

    def print_break(self):
        self.__print_root('')

    def print_lines(self, lines):
        lines = self.__normalise_lines(lines)
        for line in lines:
            self.__print(line)

    def print_text(self, text):
        self.__print(text)

    def __print(self, orig_text):
        full_text = ''
        if len(self.__sub_projects) > 0:
            for sub_project in self.__sub_projects:
                full_text += '[{0}]'.format(sub_project)
            full_text += ' '
        full_text += orig_text
        output.printer.text(full_text)

    def __print_root(self, orig_text):
        output.printer.text(orig_text)



class ConsoleProjectJournalConsumer(journal.Consumer):

    def __init__(self, printer):
        self.printer = printer
        self.__prev = None

    def is_interested(self, entry):
        return isinstance(entry, project_journal.ProjectEvent)

    def consume(self, entry):
        if isinstance(entry, project_journal.SubprojectEvent):
            self.printer.inc_sub_project(entry.sub_project_name)
        elif isinstance(entry, project_journal.SubprojectEndEvent):
            self.printer.dec_sub_project()
        elif isinstance(entry, project_journal.SectionEvent):
            self.printer.print_section(self.__to_text(entry.to_readable()))
        elif isinstance(entry, project_journal.StageEvent):
            if not self.__prev_was_section():
                self.printer.print_break()
            self.printer.print_text(self.__to_text(entry.to_readable()))
        elif isinstance(entry, project_journal.Event):
            self.printer.print_text(self.__to_text(entry.to_readable()))
        self.__prev = entry

    def __to_text(self, text):
        return text

    def __prev_was_section(self):
        return self.__prev is not None and isinstance(self.__prev, project_journal.SectionEvent)


class ValidationReporter:

    def error_report(self, validation_result):
        report = ['Validation returned with the following errors:']
        for violation in validation_result.errors:
            report.append('\t- {0}'.format(violation.message))
        return report

    def warning_report(self, validation_result):
        report = ['Validation returned with the following warnings:']
        for violation in validation_result.warnings:
            report.append('\t- {0}'.format(violation.message))
        return report


class TestReporter:

    def failed_report(self, test_report):
        report = ['The following tests failed:']
        report.extend(self.__get_failure_details_from(test_report))
        return report

    def __get_failure_details_from(self, test_report):
        details = self.__get_suite_report_failures(test_report)
        for sub_report in test_report.sub_reports:
            details.extend(self.__get_failure_details_from(sub_report))
        return details

    def __get_suite_report_failures(self, test_report):
        suite_report = test_report.suite_report
        details = []
        if suite_report.has_failures():
            details.append('  {0}'.format(test_report.full_name))
            failed_execs = suite_report.get_failed()
            for failed_exec in failed_execs:
                details.append('    {0}'.format(failed_exec.detail))
        return details


class ExecutionController:

    def __init__(self, title):
        self.banner = Banner(title)
        self.result = PASSED
        self.detail = []
        self.consumer = ConsoleProjectJournalConsumer(printer)

    def start(self, start_info=None):
        printer.print_header(self.banner.text(start_info))

    def include_failure(self, detail):
        self.result = FAILED
        if type(detail) is list:
            self.detail.extend(detail)
        else:
            self.detail.append(detail)

    def end_with_failure(self, detail):
        self.include_failure(detail)
        self.finalise()

    def include_warning(self, warning):
        if self.result != FAILED:
            self.result = PASSED_WITH_WARNINGS
        printer.print_warning(warning)

    def execute(self, exec_func, *args):
        try:
            response = exec_func(*args)
        except project_sources.BuildValidationError as e:
            self.process_validation_result(e.validation_result)
            return self.end_with_failure(ValidationReporter().error_report(e.validation_result))  # Should not reach, as above should find errors and end_with_failure
        except pkgs.PushValidationError as e:
            self.process_validation_result(e.validation_result)
            return self.end_with_failure(ValidationReporter().error_report(e.validation_result))  # Should not reach, as above should find errors and end_with_failure
        except (TNCOClientError, project_sources.ProjectError, pkgs.PackageError, EnvironmentSelectionError, lm_drivers.LmDriverException, arm_drivers.AnsibleRmDriverException) as e:
            self.include_failure(str(e))
            return self.finalise()
        return response

    def finalise(self):
        printer.print_footer(self.banner.text(self.result), self.detail)
        if self.result == FAILED:
            exit(1)
        exit(0)

    def process_validation_result(self, validation_result):
        if validation_result.has_warnings():
            validation_report = ValidationReporter().warning_report(validation_result)
            self.include_warning(validation_report)
        if validation_result.has_errors():
            validation_report = ValidationReporter().error_report(validation_result)
            self.end_with_failure(validation_report)

    def process_test_report(self, test_report):
        printer.print_section('Test Results')
        printer.print_text('Passed: {0}, Failed: {1}, Skipped: {2}'.format(test_report.passed_count(), test_report.failed_count(), test_report.skipped_count()))
        if test_report.failed_count() > 0:
            report = TestReporter().failed_report(test_report)
            self.end_with_failure(report)


printer = ProjectPrinter()
