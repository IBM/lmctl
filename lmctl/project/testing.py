TEST_STATUS_PASSED = 'PASSED'
TEST_STATUS_FAILED = 'FAILED'
TEST_STATUS_SKIPPED = 'SKIPPED'

class PkgTestReport:

    def __init__(self, name, full_name, suite_report, sub_reports):
        self.name = name
        self.full_name = full_name
        self.suite_report = suite_report
        self.sub_reports = sub_reports

    def has_failures(self):
        return len(self.failed_count()) > 0

    def has_skipped(self):
        return len(self.skipped_count()) > 0

    def has_passed(self):
        return len(self.passed_count()) > 0

    def passed_count(self):
        count = self.suite_report.passed_count()
        for sub_report in self.sub_reports:
            count += sub_report.passed_count()
        return count

    def failed_count(self):
        count = self.suite_report.failed_count()
        for sub_report in self.sub_reports:
            count += sub_report.failed_count()
        return count

    def skipped_count(self):
        count = self.suite_report.skipped_count()
        for sub_report in self.sub_reports:
            count += sub_report.skipped_count()
        return count


class TestSuiteExecutionReport:

    def __init__(self, entries):
        self.entries = entries

    def __get_result(self, result):
        matching = []
        for entry in self.entries:
            if entry.result == result:
                matching.append(entry)
        return matching

    def get_passed(self):
        return self.__get_result(TEST_STATUS_PASSED)

    def get_skipped(self):
        return self.__get_result(TEST_STATUS_SKIPPED)

    def get_failed(self):
        return self.__get_result(TEST_STATUS_FAILED)

    def has_failures(self):
        return len(self.get_failed()) > 0

    def has_skipped(self):
        return len(self.get_skipped()) > 0

    def has_passed(self):
        return len(self.get_passed()) > 0

    def passed_count(self):
        return len(self.get_passed())

    def failed_count(self):
        return len(self.get_failed())

    def skipped_count(self):
        return len(self.get_skipped())


class TestExecutionReportEntry:

    def __init__(self, test_name, result, detail=None):
        self.test_name = test_name
        self.result = result
        self.detail = detail