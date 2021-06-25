import os
import json
import lmctl.files as files
import lmctl.project.handlers.interface as handlers_api
import lmctl.utils.descriptors as descriptors
import lmctl.drivers.lm.base as lm_drivers
import lmctl.project.mutate.behaviour as behaviour_mutations
import lmctl.project.mutate.descriptor as descriptor_mutations
from lmctl.project.validation import ValidationResult, ValidationViolation
from .type_content import TypePkgContentTree

class TypeSourceTree(files.Tree):

    DESCRIPTOR_FILE_YML = 'type.yml'
    DESCRIPTOR_FILE_YAML = 'type.yaml'
    DESCRIPTOR_DIR_NAME = 'Descriptor'
    BEHAVIOUR_DIR_NAME = 'Behaviour'
    BEHAVIOR_DIR_NAME = 'Behavior'
    BEHAVIOUR_CONFIGURATIONS_DIR_NAME = 'Configurations'
    BEHAVIOUR_TEMPLATES_DIR_NAME = 'Templates'
    BEHAVIOUR_TESTS_DIR_NAME = 'Tests'

    def __init__(self, root_path=None):
        super().__init__(root_path)

    @property
    def descriptor_file_path(self):
        yml_path = self.resolve_relative_path(TypeSourceTree.DESCRIPTOR_DIR_NAME, TypeSourceTree.DESCRIPTOR_FILE_YML)
        yaml_path = self.resolve_relative_path(TypeSourceTree.DESCRIPTOR_DIR_NAME, TypeSourceTree.DESCRIPTOR_FILE_YAML)
        if os.path.exists(yaml_path):
            if os.path.exists(yml_path):
                raise handlers_api.InvalidSourceError('Project has both a {0} file and a {1} file when there should only be one'.format(
                    TypeSourceTree.DESCRIPTOR_FILE_YML, TypeSourceTree.DESCRIPTOR_FILE_YAML))
            return yaml_path
        else:
            return yml_path

    @property
    def service_behaviour_path(self):
        uk_path = self.resolve_relative_path(TypeSourceTree.BEHAVIOUR_DIR_NAME)
        us_path = self.resolve_relative_path(TypeSourceTree.BEHAVIOR_DIR_NAME)
        if os.path.exists(us_path):
            if os.path.exists(uk_path):
                raise handlers_api.InvalidSourceError('Project has both a {0} directory and a {1} directory when there should only be one'.format(
                    TypeSourceTree.BEHAVIOUR_DIR_NAME, TypeSourceTree.BEHAVIOR_DIR_NAME))
            return us_path
        else:
            return uk_path

    @property
    def service_behaviour_name(self):
        full_path = self.service_behaviour_path
        return os.path.basename(full_path)

    @property
    def service_behaviour_configurations_path(self):
        return self.resolve_relative_path(self.service_behaviour_name, TypeSourceTree.BEHAVIOUR_CONFIGURATIONS_DIR_NAME)

    def gen_service_behaviour_configuration_path(self, configuration_name):
        safe_file_name = '{0}.json'.format(files.safe_file_name(configuration_name))
        return self.resolve_relative_path(self.service_behaviour_name, TypeSourceTree.BEHAVIOUR_CONFIGURATIONS_DIR_NAME, safe_file_name)
    @property
    def service_behaviour_tests_path(self):
        return self.resolve_relative_path(self.service_behaviour_name, TypeSourceTree.BEHAVIOUR_TESTS_DIR_NAME)

    def gen_service_behaviour_tests_path(self, test_name):
        safe_file_name = '{0}.json'.format(files.safe_file_name(test_name))
        return self.resolve_relative_path(self.service_behaviour_name, TypeSourceTree.BEHAVIOUR_TESTS_DIR_NAME, safe_file_name)

class TypeSourceCreator(handlers_api.SourceCreator):

    def __init__(self):
        super().__init__()

    def _do_create_source(self, journal, source_request):
        source_tree = TypeSourceTree()
        file_ops = []
        descriptor_content = 'description: descriptor for {0}'.format(source_request.source_config.name)
        file_ops.append(handlers_api.CreateFileOp(source_tree.descriptor_file_path, descriptor_content, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.service_behaviour_path, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.service_behaviour_configurations_path, handlers_api.EXISTING_IGNORE))
        file_ops.append(handlers_api.CreateDirectoryOp(source_tree.service_behaviour_tests_path, handlers_api.EXISTING_IGNORE))
        self._execute_file_ops(file_ops, source_request.target_path, journal)

class TypeSourceHandler(handlers_api.SourceHandler):

    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)
        self.tree = TypeSourceTree(self.root_path)

    def list_elements(self, journal, element_type):
        if element_type == handlers_api.ELEMENT_TYPE_TESTS:
            tests_path = self.tree.service_behaviour_tests_path
            if not os.path.exists(tests_path):
                return []
            else:
                all_tests = []
                for root, dirs, files in os.walk(tests_path):
                    for file_name in files:
                        if file_name.endswith(".json"):
                            file_path = os.path.join(root, file_name)
                            with open(file_path, 'rt') as f:
                                try:
                                    content = json.loads(f.read())
                                    if 'name' in content:
                                        all_tests.append(content['name'])
                                except IOError as e:
                                    pass
                                except json.JSONDecodeError as e:
                                    pass
                return all_tests
        else:
            return []

    def build_staged_source_handler(self, staging_path):
        return TypeStagedSourceHandler(staging_path, self.source_config)

    def validate_sources(self, journal, source_validator, validation_options):
        errors = []
        warnings = []
        self.__validate_descriptor(journal, source_validator, errors, warnings)
        self.__validate_service_behaviour(journal, source_validator, errors, warnings)
        return ValidationResult(errors, warnings)

    def __validate_descriptor(self, journal, source_validator, errors, warnings):
        journal.stage('Validating type descriptor for {0}'.format(self.source_config.name))
        descriptor_path = self.tree.descriptor_file_path
        source_validator.validate_descriptor(descriptor_path, errors, warnings)

    def __validate_service_behaviour(self, journal, source_validator, errors, warnings):
        journal.stage('Validating service behaviour for {0}'.format(self.source_config.name))
        behaviour_path = self.tree.service_behaviour_path
        if not os.path.exists(behaviour_path):
            journal.event('No service behaviour found at: {0}'.format(behaviour_path))
            return
        else:
            configurations_path = self.tree.service_behaviour_configurations_path
            if os.path.exists(configurations_path):
                journal.event('Checking configurations at: {0}'.format(configurations_path))
                self.__walk_and_check_json_files(configurations_path, 'Configuration', journal, errors, warnings)
            else:
                journal.event('No configurations found at: {0}'.format(configurations_path))
            tests_path = self.tree.service_behaviour_tests_path
            if os.path.exists(tests_path):
                journal.event('Checking tests at: {0}'.format(tests_path))
                self.__walk_and_check_json_files(tests_path, 'Test', journal, errors, warnings)
            else:
                journal.event('No tests found at: {0}'.format(configurations_path))

    def __walk_and_check_json_files(self, path, type_name, journal, errors, warnings):
        for root, dirs, files in os.walk(path):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                if not file_name.endswith(".json"):
                    msg = '{0} [{1}]: is not a json file (with a .json extension)'.format(type_name, file_path)
                    journal.error_event(msg)
                    errors.append(ValidationViolation(msg))
                else:
                    with open(file_path, 'rt') as f:
                        try:
                            json.loads(f.read())
                        except IOError as e:
                            msg = '{0} [{1}]: does not contain valid JSON: {2}'.format(type_name, file_path, str(e))
                            journal.error_event(msg)
                            errors.append(ValidationViolation(msg))
                        except json.JSONDecodeError as e:
                            msg = '{0} [{1}]: does not contain valid JSON: {2}'.format(type_name, file_path, str(e))
                            journal.error_event(msg)
                            errors.append(ValidationViolation(msg))

    def stage_sources(self, journal, source_stager):
        staging_tree = TypePkgContentTree()
        project_descriptor_name = self.__stage_descriptor(journal, source_stager, staging_tree)
        self.__stage_service_behaviour(journal, source_stager, staging_tree, project_descriptor_name)

    def __stage_descriptor(self, journal, source_stager, staging_tree):
        descriptor_path = self.tree.descriptor_file_path
        journal.stage('Staging type descriptor for {0} at {1}'.format(self.source_config.name, descriptor_path))
        staged_descriptor_path = source_stager.stage_descriptor(descriptor_path, staging_tree.descriptor_file_path)
        descriptor = descriptors.DescriptorParser().read_from_file(staged_descriptor_path)
        return descriptor.get_name()

    def __stage_service_behaviour(self, journal, source_stager, staging_tree, project_descriptor_name):
        behaviour_path = self.tree.service_behaviour_path
        journal.stage('Staging service behaviour for {0} at {1}'.format(self.source_config.name, behaviour_path))
        if not os.path.exists(behaviour_path):
            journal.event('Skipping - nothing to compile at {0}'.format(behaviour_path))
            return
        configurations_path = self.tree.service_behaviour_configurations_path
        if os.path.exists(configurations_path):
            journal.event('Staging configurations at: {0}'.format(configurations_path))
            walk_and_find_json(configurations_path, self.__stage_behaviour_configuration, staging_tree, source_stager, journal)
        else:
            journal.event('Skipping - no configurations found at: {0}'.format(configurations_path))
        tests_path = self.tree.service_behaviour_tests_path
        if os.path.exists(tests_path):
            journal.event('Staging tests at: {0}'.format(tests_path))
            walk_and_find_json(tests_path, self.__stage_behaviour_test, staging_tree, source_stager)
        else:
            journal.event('Skipping - no tests found at: {0}'.format(tests_path))

    def __stage_behaviour_configuration(self, configuration_path, configuration, staging_tree, source_stager, journal):
        relative_staging_path = os.path.join(staging_tree.service_behaviour_configurations_path, os.path.basename(configuration_path))
        source_stager.stage_file(configuration_path, relative_staging_path, behaviour_mutations.AssemblyConfigurationStagingMutator(self.source_config, source_stager.references, journal))

    def __stage_behaviour_runtime(self, runtime_path, runtime, staging_tree, source_stager):
        relative_staging_path = os.path.join(staging_tree.service_behaviour_runtime_path, os.path.basename(runtime_path))
        source_stager.stage_file(runtime_path, relative_staging_path, behaviour_mutations.ScenarioStagingMutator(self.source_config))

    def __stage_behaviour_test(self, test_path, test, staging_tree, source_stager):
        relative_staging_path = os.path.join(staging_tree.service_behaviour_tests_path, os.path.basename(test_path))
        source_stager.stage_file(test_path, relative_staging_path, behaviour_mutations.ScenarioStagingMutator(self.source_config))

    def pull_sources(self, journal, backup_tool, env_sessions, references):
        lm_session = env_sessions.lm
        backup_tree = TypeSourceTree()
        self.__pull_descriptor(journal, backup_tool, backup_tree, lm_session, references)
        self.__pull_behaviour(journal, backup_tool, backup_tree, lm_session, references)

    def __pull_descriptor(self, journal, backup_tool, backup_tree, lm_session, references):
        journal.stage('Pulling descriptor for {0}'.format(self.source_config.name))
        descriptor_name = descriptors.descriptor_named(descriptors.TYPE_DESCRIPTOR_TYPE, self.source_config.full_name, self.source_config.version)
        descriptor_driver = lm_session.descriptor_driver
        journal.event('Pulling descriptor {0} from CP4NA orchestration ({1})'.format(descriptor_name, lm_session.env.address))
        try:
            raw_descriptor = descriptor_driver.get_descriptor(descriptor_name)
            descriptor = descriptors.DescriptorParser().read_from_str(raw_descriptor)
        except lm_drivers.NotFoundException:
            msg = 'Descriptor {0} not found'.format(descriptor_name)
            journal.error_event(msg)
            return
        descriptor_path = self.tree.descriptor_file_path
        if os.path.exists(descriptor_path):
            self.__backup_descriptor(journal, backup_tool, backup_tree, descriptor_path)
        journal.event('Saving pulled descriptor to {0}'.format(descriptor_path))
        descriptor = descriptor_mutations.DescriptorPullMutator(references, journal).apply(descriptor)
        descriptors.DescriptorParser().write_to_file(descriptor, descriptor_path)

    def __backup_descriptor(self, journal, backup_tool, backup_tree, descriptor_path):
        journal.event('Creating backup of descriptor {0}'.format(descriptor_path))
        backup_tool.backup_file(descriptor_path, backup_tree.descriptor_file_path)

    def __pull_behaviour(self, journal, backup_tool, backup_tree, lm_session, references):
        journal.stage('Pulling service behaviour for {0}'.format(self.source_config.name))
        project_id = descriptors.descriptor_named(descriptors.TYPE_DESCRIPTOR_TYPE, self.source_config.full_name, self.source_config.version)
        behaviour_driver = lm_session.behaviour_driver
        try:
            behaviour_driver.get_project(project_id)
        except lm_drivers.NotFoundException:
            journal.event('No Service Behaviour project with name {0} found in CP4NA orchestration {1}, skipping pull'.format(project_id, lm_session.env.address))
            return
        discovered_configurations_by_id = self.__pull_assembly_configurations(journal, backup_tool, backup_tree, lm_session, project_id, references)
        self.__pull_scenarios(journal, backup_tool, backup_tree, lm_session, project_id, discovered_configurations_by_id, references)

    def __pull_assembly_configurations(self, journal, backup_tool, backup_tree, lm_session, behaviour_project_id, references):
        behaviour_driver = lm_session.behaviour_driver
        assembly_configurations = behaviour_driver.get_assembly_configurations(behaviour_project_id)
        journal.event('Found {0} assembly configuration(s) to pull'.format(len(assembly_configurations)))
        discovered_configurations_by_id = {}
        for assembly_configuration in assembly_configurations:
            config_name = assembly_configuration['name']
            config_id = assembly_configuration['id']
            discovered_configurations_by_id[config_id] = assembly_configuration
            file_path = self.tree.gen_service_behaviour_configuration_path(config_name)
            if os.path.exists(file_path):
                backup_file_path = backup_tree.gen_service_behaviour_configuration_path(config_name)
                journal.event('Creating backup of assembly configuration {0}'.format(file_path))
                backup_tool.backup_file(file_path, backup_file_path)
            journal.event('Saving assembly configuration {0} to {1}'.format(config_name, file_path))
            assembly_configuration = behaviour_mutations.AssemblyConfigurationPullMutator(self.source_config, references, journal).apply(assembly_configuration)
            with open(file_path, 'w') as out:
                json.dump(assembly_configuration, out, indent=2)
        return discovered_configurations_by_id

    def __pull_scenarios(self, journal, backup_tool, backup_tree, lm_session, behaviour_project_id, discovered_configurations_by_id, references):
        behaviour_driver = lm_session.behaviour_driver
        scenarios = behaviour_driver.get_scenarios(behaviour_project_id)
        journal.event('Found {0} scenario(s) to pull'.format(len(scenarios)))
        for scenario in scenarios:
            scenario_name = scenario['name']
            file_path = self.tree.gen_service_behaviour_tests_path(scenario_name)
            if os.path.exists(file_path):
                backup_file_path = backup_tree.gen_service_behaviour_tests_path(scenario_name)
                journal.event('Creating backup of test {0}'.format(file_path))
                backup_tool.backup_file(file_path, backup_file_path)
            scenario = behaviour_mutations.ScenarioPullMutator(self.source_config, references, discovered_configurations_by_id).apply(scenario)
            journal.event('Saving scenario {0} to {1}'.format(scenario_name, file_path))
            with open(file_path, 'w') as out:
                json.dump(scenario, out, indent=2)


def walk_and_find_json(path, action, *action_args):
    for root, dirs, files in os.walk(path):
        for file_name in files:
            if file_name.endswith(".json"):
                file_path = os.path.join(root, file_name)
                with open(file_path, 'rt') as f:
                    try:
                        content = json.loads(f.read())
                    except IOError as e:
                        raise handlers_api.InvalidSourceError(str(e)) from e
                    except json.JSONDecodeError as e:
                        raise handlers_api.InvalidSourceError(str(e)) from e
                    action(file_path, content, *action_args)


class TypeStagedSourceHandler(handlers_api.StagedSourceHandler):

    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)
        self.tree = TypePkgContentTree(self.root_path)

    def compile_sources(self, journal, source_compiler):
        compile_tree = TypePkgContentTree()
        journal.event('Compiling descriptor for: {0}'.format(self.source_config.full_name))
        source_compiler.compile_tree(self.tree.descriptor_path, compile_tree.descriptor_path)
        behaviour_path = self.tree.service_behaviour_path
        if not os.path.exists(behaviour_path):
            journal.event('Skipping - nothing to compile at {0}'.format(behaviour_path))
        else:
            journal.event('Compiling Service Behaviour for: {0}'.format(self.source_config.full_name))
            source_compiler.compile_tree(behaviour_path, compile_tree.service_behaviour_path)