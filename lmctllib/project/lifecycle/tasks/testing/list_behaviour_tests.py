import os
import logging
import json
from ..tasks import ProjectLifecycleTask

class ListBehaviourTests(ProjectLifecycleTask):
    """
    Lists available Service Behaviour tests
    """
    def __init__(self):
        super().__init__("List Behaviour Tests")
    
    def execute_work(self, tools, products):
        tests_path = self._get_project_tree().serviceBehaviour().testsDirectory()
        if os.path.exists(tests_path):
            for root, dirs, files in os.walk(tests_path):  
                for filename in files:
                    if(filename.endswith(".json")):
                        file_path = os.path.join(root, filename)
                        with open(file_path, 'rt') as f:
                            scenario_content = json.loads(f.read())
                            self._get_journal().add_text('\t- {0} (Location: {1})'.format(scenario_content['name'], file_path))
        else:
            self._get_journal().add_text('No tests found at {0}'.format(tests_path))
        return self._return_passed()