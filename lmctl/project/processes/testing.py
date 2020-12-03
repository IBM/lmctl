import lmctl.project.handlers.interface as handlers_api
import lmctl.project.testing as project_testing

class TestProcessError(Exception):
    pass

class TestProcess:

    def __init__(self, pkg_content, options, journal, env_sessions):
        self.pkg_content = pkg_content
        self.journal = journal
        self.options = options
        self.env_sessions = env_sessions

    def execute(self):
        return TestWorker(self.pkg_content, self.options, self.journal, self.env_sessions).work()

class TestWorker:

    def __init__(self, pkg_content, options, journal, env_sessions):
        self.pkg_content = pkg_content
        self.journal = journal
        self.options = options
        self.env_sessions = env_sessions

    def work(self):
        child_test_reports = self.__test_child_content()
        test_report = self.__test_content()
        return project_testing.PkgTestReport(self.pkg_content.meta.name, self.pkg_content.meta.full_name, test_report, child_test_reports)

    def __filter_selected_tests(self):
        return self.options.selected_tests

    def __test_content(self):
        self.journal.section('Execute Tests')
        try:
            test_report = self.pkg_content.handler.execute_tests(self.journal, self.env_sessions, self.__filter_selected_tests())
            return test_report
        except handlers_api.ContentHandlerError as e:
            raise TestProcessError(str(e)) from e

    def __test_child_content(self):
        child_reports = []
        subcontents = self.pkg_content.subcontents
        for subcontent in subcontents:
            self.journal.subproject(subcontent.meta.name)
            test_report = TestWorker(subcontent, self.options, self.journal, self.env_sessions).work()
            child_reports.append(test_report)
            self.journal.subproject_end(subcontent.meta.name)
        return child_reports
