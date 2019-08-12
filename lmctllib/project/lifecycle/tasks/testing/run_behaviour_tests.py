import logging
import os
import json
import time
import lmctllib.utils.descriptors as descriptor_utils
from ..tasks import ProjectLifecycleTask, PRODUCT_SELECTED_TESTS

class RunBehaviourTests(ProjectLifecycleTask):
    """
    Run Service Behaviour Tests
    """
    ALL_BEHAVIOUR_TESTS = '*'

    def __init__(self):
        super().__init__("Run Behaviour Tests")
    
    def execute_work(self, tools, products):
        if products.has_value(PRODUCT_SELECTED_TESTS):
            behaviour_tests = products.get_value(PRODUCT_SELECTED_TESTS)
        else:
            behaviour_tests = RunBehaviourTests.ALL_BEHAVIOUR_TESTS
        env = self._get_environment()
        lm_env = env.lm

        target_descriptor_path = self._get_project_tree().pushWorkspace().content().serviceDescriptor().descriptorFile()
        if os.path.exists(target_descriptor_path):
            descritor_content = descriptor_utils.DescriptorReader.readDictionary(target_descriptor_path)
            descriptor = descriptor_utils.DescriptorModel(descritor_content)
            project_id = descriptor.getName()        
        else:
            return self._return_failure('Could not establish service behaviour project id as no service descriptor was found at {0}'.format(target_descriptor_path))
            
        self._get_journal().add_text('Project: {0} at LM ({1})'.format(project_id, lm_env.getUrl()))
        scenarios_to_run = []
        tests_path = self._get_project_tree().pushWorkspace().content().serviceBehaviour().testsDirectory()
        if behaviour_tests != RunBehaviourTests.ALL_BEHAVIOUR_TESTS:
            behaviour_tests = behaviour_tests.split(',')
        if os.path.exists(tests_path):
            for root, dirs, files in os.walk(tests_path):  
                for filename in files:
                    if(filename.endswith(".json")):
                        file_path = os.path.join(root, filename)
                        with open(file_path, 'rt') as f:
                            scenario_content = json.loads(f.read())
                            if behaviour_tests == RunBehaviourTests.ALL_BEHAVIOUR_TESTS or scenario_content['name'] in behaviour_tests:
                                behaviour_driver = lm_env.getBehaviourDriver()
                                scenario = behaviour_driver.getScenarioByName(project_id, scenario_content['name'] )
                                scenarios_to_run.append({'id': scenario['id'], 'name': scenario['name']})
        else:
            return self._return_skipped('No tests found at {0}'.format(tests_path))

        total_scenarios = len(scenarios_to_run)
        total_passed = 0
        total_failed = 0
        self._get_journal().add_text('Found {0} tests to run'.format(total_scenarios))
        for scenario_ref in scenarios_to_run:
            passed = self.__executeScenario(lm_env, project_id, scenario_ref['id'], scenario_ref['name'])    
            if passed:
                total_passed += 1
            else:
                total_failed += 1
        self._get_journal().add_text('Test Results - Executed: {0}  Passed: {1}  Failed: {2}'.format(total_scenarios, total_passed, total_failed))        
        if total_failed == 0:
            return self._return_passed()
        else:
            return self._return_failure('There were test failures')

    def __executeScenario(self, lm_env, project_id, scenario_id, scenario_name):
        self._get_journal().add_text('Running test: {0} in project: {1}'.format(scenario_name, project_id))
        behaviour_driver = lm_env.getBehaviourDriver()
        execution_location = behaviour_driver.executeScenario(scenario_id)
        location_parts = execution_location.split('/')
        execution_id = location_parts[len(location_parts)-1]
        finished = False
        passed = False
        while not finished:
            execution = behaviour_driver.getExecution(execution_id)
            finished = self.__isExecFinished(execution)
            if finished:
                self._get_journal().add_text('Test {0} completed with result: {1}'.format(scenario_name, execution['status']))
                passed = execution['status'] == 'PASS'
                if execution['status'] == 'FAIL':
                    self._get_journal().add_text(self.__getFailReason(execution))
            else:
                stage_results = execution['stageReports']
                total_steps = self.__calcTotalSteps(stage_results)
                current_step = self.__calcCurrentStep(stage_results)
                step_str = 'step {1}/{2}'.format(scenario_name, current_step, total_steps) if current_step > 0 else 'pending...'
                self._get_journal().add_text('Test {0} in progress: {1}'.format(scenario_name, step_str))
                time.sleep(5)
        return passed

    def __isExecFinished(self, execution):
        finished_results = ['PASS', 'ABORTED', 'FAIL']
        if execution['status'] in finished_results:
            return True
        return False

    def __calcCurrentStep(self, stage_results):
        current_step = 0
        for stage_result in stage_results:
            steps = stage_result['steps']
            for step in steps:
                current_step += 1
                if step['status'] == 'IN_PROGRESS':
                    return current_step
        return 0

    def __calcTotalSteps(self, stage_results):
        total = 0
        for stage_result in stage_results:
            steps = stage_result['steps']
            for step in steps:
                total += 1
        return total

    def __getFailReason(self, execution):
        if execution['status'] == 'FAIL':
            return 'Step {0} failed with reason: {1}'.format(execution['name'], execution['error'])
        return 'Not given'
