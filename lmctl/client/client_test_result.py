from typing import List

class TestResult:

    def __init__(self, name: str, error: Exception = None):
        self.name = name
        self.error = error
    
    @property
    def passed(self):
        return self.error is None

class TestResults: 

    def __init__(self, tests: List[TestResult] = None):
        self.tests = tests or []
        
    @property
    def passed(self):
        for t in self.tests:
            if not t.passed:
                return False
        return True