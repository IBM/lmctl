
class ValidationViolation:

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return f'{self.__class__.__name__}(message: {self.message})'

    def __repr__(self):
        return f'{self.__class__.__name__}(message: {self.message!r})'

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

    def __str__(self):
        return f'{self.__class__.__name__}(errors: {self.errors}, warnings: {self.warnings})'

    def __repr__(self):
        return f'{self.__class__.__name__}(errors: {self.errors!r}, warnings: {self.warnings!r})'