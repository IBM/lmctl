import time
import os
import json
import lmctl.files as files
import lmctl.utils.descriptors as descriptors
import lmctl.drivers.lm.base as lm_drivers
import lmctl.project.mutate.behaviour as behaviour_mutations
import lmctl.project.handlers.interface as handlers_api
import lmctl.project.testing as project_testing
from lmctl.project.validation import ValidationResult, ValidationViolation

DEFAULT_POLLING_PERIOD = 2
POLLING_PERIOD = DEFAULT_POLLING_PERIOD

def set_polling_period(new_period):
    global POLLING_PERIOD
    POLLING_PERIOD = new_period

def reset_polling_period():
    global POLLING_PERIOD
    POLLING_PERIOD = DEFAULT_POLLING_PERIOD


class AssemblyPkgContentTree(files.Tree):

    DESCRIPTOR_FILE_YML = 'assembly.yml'
    DESCRIPTOR_TEMPLATE_FILE_YML = 'assembly-template.yml'
    DESCRIPTOR_DIR_NAME = 'Descriptor'
    BEHAVIOUR_DIR_NAME = 'Behaviour'
    BEHAVIOUR_CONFIGURATIONS_DIR_NAME = 'Configurations'
    BEHAVIOUR_TEMPLATES_DIR_NAME = 'Templates'
    BEHAVIOUR_RUNTIME_DIR_NAME = 'Runtime'
    BEHAVIOUR_TESTS_DIR_NAME = 'Tests'

    def __init__(self, root_path=None):
        super().__init__(root_path)

    @property
    def descriptor_path(self):
        return self.resolve_relative_path(AssemblyPkgContentTree.DESCRIPTOR_DIR_NAME)

    @property
    def descriptor_file_name(self):
        full_path = self.descriptor_file_path
        return os.path.basename(full_path)

    @property
    def descriptor_template_file_name(self):
        full_path = self.descriptor_template_file_path
        return os.path.basename(full_path)

    @property
    def descriptor_file_path(self):
        return self.resolve_relative_path(AssemblyPkgContentTree.DESCRIPTOR_DIR_NAME, AssemblyPkgContentTree.DESCRIPTOR_FILE_YML)
   
    @property
    def descriptor_template_file_path(self):
        return self.resolve_relative_path(AssemblyPkgContentTree.DESCRIPTOR_DIR_NAME, AssemblyPkgContentTree.DESCRIPTOR_TEMPLATE_FILE_YML)

    @property
    def service_behaviour_path(self):
        return self.resolve_relative_path(AssemblyPkgContentTree.BEHAVIOUR_DIR_NAME)

    @property
    def service_behaviour_name(self):
        return AssemblyPkgContentTree.BEHAVIOUR_DIR_NAME

    @property
    def service_behaviour_configurations_path(self):
        behaviour_dir_name = self.service_behaviour_name
        return self.resolve_relative_path(behaviour_dir_name, AssemblyPkgContentTree.BEHAVIOUR_CONFIGURATIONS_DIR_NAME)

    @property
    def service_behaviour_runtime_path(self):
        behaviour_dir_name = self.service_behaviour_name
        return self.resolve_relative_path(behaviour_dir_name, AssemblyPkgContentTree.BEHAVIOUR_RUNTIME_DIR_NAME)

    @property
    def service_behaviour_tests_path(self):
        behaviour_dir_name = self.service_behaviour_name
        return self.resolve_relative_path(behaviour_dir_name, AssemblyPkgContentTree.BEHAVIOUR_TESTS_DIR_NAME)

class AssemblyContentHandler(handlers_api.PkgContentHandler):

    def __init__(self, root_path, meta):
        super().__init__(root_path, meta)
        self.tree = AssemblyPkgContentTree(self.root_path)

    def validate_content(self, journal, env_sessions, validation_options):
        errors = []
        warnings = []
        self.__validate_descriptor(journal, errors, warnings)
        return ValidationResult(errors, warnings)

    def __validate_descriptor(self, journal, errors, warnings):
        journal.stage('Validating assembly descriptor for {0}'.format(self.meta.name))
        descriptor_path = self.tree.descriptor_file_path
        if not os.path.exists(descriptor_path):
            msg = 'No descriptor found at: {0}'.format(descriptor_path)
            journal.error_event(msg)
            errors.append(ValidationViolation(msg))

    def push_content(self, journal, env_sessions):
        project_id = self.__push_descriptor(journal, env_sessions)
        self.__push_descriptor_template(journal, env_sessions)
        self.__push_service_behaviour(journal, env_sessions, project_id)

    def __push_descriptor(self, journal, env_sessions):
        lm_session = env_sessions.lm
        descriptor_path = self.tree.descriptor_file_path
        descriptor, descriptor_yml_str = descriptors.DescriptorParser().read_from_file_with_raw(descriptor_path)
        descriptor_name = descriptor.get_name()
        descriptor_driver = lm_session.descriptor_driver
        journal.event('Checking for Descriptor {0} in CP4NA orchestration ({1})'.format(descriptor_name, lm_session.env.address))
        found = True
        try:
            descriptor_driver.get_descriptor(descriptor_name)
        except lm_drivers.NotFoundException:
            found = False
        if found:
            journal.event('Descriptor {0} already exists, updating'.format(descriptor_name))
            descriptor_driver.update_descriptor(descriptor_name, descriptor_yml_str)
        else:
            journal.event('Not found, creating Descriptor {0}'.format(descriptor_name))
            descriptor_driver.create_descriptor(descriptor_yml_str)
        env_sessions.mark_lm_updated()
        return descriptor_name

    def __push_descriptor_template(self, journal, env_sessions):
        lm_session = env_sessions.lm
        descriptor_template_path = self.tree.descriptor_template_file_path
        if os.path.exists(descriptor_template_path):
            descriptor, descriptor_yml_str = descriptors.DescriptorParser().read_from_file_with_raw(descriptor_template_path)
            descriptor_name = descriptor.get_name()
            descriptor_template_driver = lm_session.descriptor_template_driver
            journal.event('Checking for Descriptor Template {0} in CP4NA orchestration ({1})'.format(descriptor_name, descriptor_template_driver.lm_base))
            found = True
            try:
                descriptor_template_driver.get_descriptor_template(descriptor_name)
            except lm_drivers.NotFoundException:
                found = False
            if found:
                journal.event('Descriptor Template {0} already exists, updating'.format(descriptor_name))
                descriptor_template_driver.update_descriptor_template(descriptor_name, descriptor_yml_str)
            else:
                journal.event('Not found, creating Descriptor Template {0}'.format(descriptor_name))
                descriptor_template_driver.create_descriptor_template(descriptor_yml_str)

    def __push_service_behaviour(self, journal, env_sessions, project_id):
        lm_session = env_sessions.lm
        behaviour_path = self.tree.service_behaviour_path
        if not os.path.exists(behaviour_path):
            journal.event('Skipping Service Behaviour - nothing to push at {0}'.format(behaviour_path))
            return
        journal.stage('Pushing Service Behaviour for {0} at {1}'.format(self.meta.name, behaviour_path))
        existing_configurations = lm_session.behaviour_driver.get_assembly_configurations(project_id)
        self.__push_configurations(journal, env_sessions, project_id, existing_configurations)
        existing_scenarios = lm_session.behaviour_driver.get_scenarios(project_id)
        all_available_configurations = lm_session.behaviour_driver.get_assembly_configurations(project_id)
        self.__push_runtime_scenarios(journal, env_sessions, project_id, existing_scenarios, all_available_configurations)
        self.__push_test_scenarios(journal, env_sessions, project_id, existing_scenarios, all_available_configurations)

    def __push_configurations(self, journal, env_sessions, project_id, existing_configurations):
        lm_session = env_sessions.lm
        existing_configurations = lm_session.behaviour_driver.get_assembly_configurations(project_id)
        configurations_path = self.tree.service_behaviour_configurations_path
        if os.path.exists(configurations_path):
            walk_and_find_json(configurations_path, 'Assembly Configuration', self.__push_configuration, journal, env_sessions, project_id, existing_configurations)

    def __push_configuration(self, file_path, configuration, journal, env_sessions, project_id, existing_configurations):
        lm_session = env_sessions.lm
        configuration['projectId'] = project_id
        project_descriptor_name = project_id
        behaviour_driver = lm_session.behaviour_driver
        journal.event('Checking for assembly configuration {0} in CP4NA orchestration ({1}) project {2}'.format(configuration['name'], lm_session.env.address, project_id))
        matching_configuration = self.__find_assembly_configuration_by_name(existing_configurations, configuration['name'])
        if matching_configuration:
            journal.event('Assembly Configuration {0} already exists, updating'.format(configuration['name']))
            configuration['id'] = matching_configuration['id']
            behaviour_driver.update_assembly_configuration(configuration)
        else:
            journal.event('Not found, creating assembly configuration {0}'.format(configuration['name']))
            behaviour_driver.create_assembly_configuration(configuration)
        env_sessions.mark_lm_updated()

    def __push_runtime_scenarios(self, journal, env_sessions, project_id, existing_scenarios, available_configurations):
        runtimes_path = self.tree.service_behaviour_runtime_path
        if os.path.exists(runtimes_path):
            walk_and_find_json(runtimes_path, 'Runtime', self.__push_scenario, journal, env_sessions, project_id, existing_scenarios, available_configurations)

    def __push_test_scenarios(self, journal, env_sessions, project_id, existing_scenarios, available_configurations):
        tests_path = self.tree.service_behaviour_tests_path
        if os.path.exists(tests_path):
            walk_and_find_json(tests_path, 'Test', self.__push_scenario, journal, env_sessions, project_id, existing_scenarios, available_configurations)

    def __push_scenario(self, file_path, scenario, journal, env_sessions, project_id, existing_scenarios, available_configurations):
        lm_session = env_sessions.lm
        scenario['projectId'] = project_id
        behaviour_driver = lm_session.behaviour_driver
        scenario = behaviour_mutations.ScenarioPushMutator(available_configurations).apply(scenario)
        journal.event('Checking for Scenario {0} in CP4NA orchestration ({1}) project {2}'.format(scenario['name'], lm_session.env.address, project_id))
        matching_scenario = next((x for x in existing_scenarios if x["name"] == scenario['name']), None)
        if matching_scenario:
            journal.event('Scenario {0} already exists, updating'.format(scenario['name']))
            scenario['id'] = matching_scenario['id']
            behaviour_driver.update_scenario(scenario)
        else:
            journal.event('Not found, creating Scenario {0}'.format(scenario['name']))
            behaviour_driver.create_scenario(scenario)
        env_sessions.mark_lm_updated()

    def __find_assembly_configuration_by_name(self, all_available_configurations, assembly_name):
        return next((x for x in all_available_configurations if x["name"] == assembly_name), None)

    def execute_tests(self, journal, env_sessions, selected_tests):
        return AssemblyTestManager(self.root_path, self.meta).execute_tests(journal, env_sessions, selected_tests)


def walk_and_find_json(path, type_name, action, *action_args):
    for root, dirs, files in os.walk(path):
        for file_name in files:
            if file_name.endswith(".json"):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'rt') as f:
                    try:
                        content = json.loads(f.read())
                    except IOError as e:
                        raise handlers_api.ContentHandlerError(str(e)) from e
                    except json.JSONDecodeError as e:
                        raise handlers_api.ContentHandlerError(str(e)) from e
                    action(file_path, content, *action_args)


class AssemblyTestManager:

    def __init__(self, root_path, meta):
        self.root_path = root_path
        self.meta = meta
        self.tree = AssemblyPkgContentTree(self.root_path)

    def __determine_project_id(self):
        descriptor_path = self.tree.descriptor_file_path
        descriptor = descriptors.DescriptorParser().read_from_file(descriptor_path)
        descriptor_name = descriptor.get_name()
        return descriptor_name

    def get_tests(self):
        test_scenarios = []
        tests_path = self.tree.service_behaviour_tests_path
        if os.path.exists(tests_path):
            test_capture = TestCapture()
            walk_and_find_json(tests_path, 'Test', test_capture.action)
            test_scenarios.extend(test_capture.captives)
        return test_scenarios

    def execute_tests(self, journal, env_sessions, selected_tests):
        test_scenarios = self.__filter_scenarios_to_execute(self.get_tests(), selected_tests)
        if len(test_scenarios) == 0:
            journal.event('No matching tests found to execute at {0}'.format(self.tree.service_behaviour_tests_path))
            return project_testing.TestSuiteExecutionReport([])
        lm_session = env_sessions.lm
        project_id = self.__determine_project_id()
        report_entries = []
        for test_scenario in test_scenarios:
            report_entries.append(self.__execute_test(journal, lm_session, project_id, test_scenario))
        return project_testing.TestSuiteExecutionReport(report_entries)

    def __filter_scenarios_to_execute(self, test_scenarios, selected_test_names):
        scenarios_to_execute = []
        for test_scenario in test_scenarios:
            if '*' in selected_test_names or ('name' in test_scenario and (test_scenario['name'] in selected_test_names)):
                scenarios_to_execute.append(test_scenario)
        return scenarios_to_execute

    def __execute_test(self, journal, lm_session, project_id, test_scenario):
        scenario_name = test_scenario['name']
        journal.event('Executing test: {0}'.format(scenario_name))
        behaviour_driver = lm_session.behaviour_driver
        remote_scenario = behaviour_driver.get_scenario_by_name(project_id, scenario_name)
        execution_location = behaviour_driver.execute_scenario(remote_scenario['id'])
        location_parts = execution_location.split('/')
        execution_id = location_parts[len(location_parts) - 1]
        finished = False
        report_entries = []
        current_step = 0
        while not finished:
            execution = behaviour_driver.get_execution(execution_id)
            finished = self.__is_exec_finished(execution)
            if finished:
                journal.event('Test {0} completed with result: {1}'.format(scenario_name, execution['status']))
                if execution['status'] == 'FAIL':
                    journal.error_event('Execution failed with reason: {0}'.format(execution['error']))
                exec_report = self.__build_execution_report(scenario_name, execution)
                return exec_report
            else:
                stage_results = execution['stageReports']
                total_steps = self.__calc_total_steps(stage_results)
                prev_step = current_step
                current_step = self.__calc_current_step(stage_results)
                steps_difference = current_step - prev_step
                if steps_difference > 1:
                    for i in range(prev_step+1, current_step):
                        step_str = 'step {0}/{1}'.format(i, total_steps)
                        journal.event('Test \'{0}\' in progress: {1}'.format(scenario_name, step_str))
                step_str = 'step {0}/{1}'.format(current_step, total_steps) if current_step > 0 else 'pending...'
                journal.event('Test \'{0}\' in progress: {1}'.format(scenario_name, step_str))
                time.sleep(POLLING_PERIOD)

    def __calc_current_step(self, stage_results):
        current_step = 0
        for stage_result in stage_results:
            steps = stage_result['steps']
            for step in steps:
                current_step += 1
                if step['status'] == 'IN_PROGRESS':
                    return current_step
        return 0

    def __calc_total_steps(self, stage_results):
        total = 0
        for stage_result in stage_results:
            steps = stage_result['steps']
            for step in steps:
                total += 1
        return total

    def __is_exec_finished(self, execution):
        finished_results = ['PASS', 'ABORTED', 'FAIL']
        if execution['status'] in finished_results:
            return True
        return False

    def __build_execution_report(self, scenario_name, execution):
        status = execution['status']
        detail = None
        if status == 'PASS':
            result = project_testing.TEST_STATUS_PASSED
        else:
            result = project_testing.TEST_STATUS_FAILED
            detail = '{0} failed:'.format(scenario_name)
            if 'error' in execution:
                detail += ' {0}'.format(execution['error'])
            else:
                detail += ' no reason given'
        entry = project_testing.TestExecutionReportEntry(scenario_name, result, detail)
        return entry


class TestCapture:

    def __init__(self):
        self.captives = []

    def action(self, file_name, scenario):
        self.captives.append(scenario)
