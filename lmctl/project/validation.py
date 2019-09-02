
class ValidationViolation:

    def __init__(self, message):
        self.message = message


class ValidationResult:

    def __init__(self, errors=None, warnings=None):
        if errors is None:
            errors = []
        self.errors = errors
        if warnings is None:
            warnings = []
        self.warnings = warnings

    def passed(self):
        return not self.has_errors()

    def has_errors(self):
        return len(self.errors) > 0

    def has_warnings(self):
        return len(self.warnings) > 0

    @staticmethod
    def single_error(violation):
        return ValidationResult([violation], [])
