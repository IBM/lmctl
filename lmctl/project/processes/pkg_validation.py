import lmctl.project.handlers.interface as handlers_api
import lmctl.project.validation as validation

class PackageValidationProcessError(Exception):
    pass

class PackageValidationProcess:

    def __init__(self, pkg_content, options, journal, env_sessions):
        self.pkg_content = pkg_content
        self.journal = journal
        self.options = options
        self.env_sessions = env_sessions

    def execute(self):
        return PackageValidationWorker(self.pkg_content, self.options, self.journal, self.env_sessions).work()

class PackageValidationWorker:

    def __init__(self, pkg_content, options, journal, env_sessions):
        self.pkg_content = pkg_content
        self.journal = journal
        self.__build_content_options(options)
        self.env_sessions = env_sessions

    def __build_content_options(self, cmd_options):
        self.options = handlers_api.ContentValidationOptions(allow_autocorrect=cmd_options.allow_autocorrect)

    def work(self):
        self.journal.section('Validate Content')
        all_errors = []
        all_warnings = []
        try:
            validate_content_result = self.pkg_content.handler.validate_content(self.journal, self.env_sessions, self.options)
        except handlers_api.ContentHandlerError as e:
            raise PackageValidationProcessError(str(e)) from e
        all_errors.extend(validate_content_result.errors)
        all_warnings.extend(validate_content_result.warnings)
        self.__validate_child_content(all_errors, all_warnings)
        return validation.ValidationResult(all_errors, all_warnings)

    def __validate_child_content(self, errors, warnings):
        subcontents = self.pkg_content.subcontents
        for subcontent in subcontents:
            self.journal.subproject(subcontent.meta.name)
            validation_result = PackageValidationWorker(subcontent, self.options, self.journal, self.env_sessions).work()
            errors.extend(validation_result.errors)
            warnings.extend(validation_result.warnings)
            self.journal.subproject_end(subcontent.meta.name)