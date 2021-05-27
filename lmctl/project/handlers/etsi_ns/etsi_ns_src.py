import os, json
import lmctl.project.handlers.assembly as assembly_api
import lmctl.project.handlers.interface as handlers_api
import lmctl.project.mutate.behaviour as behaviour_mutations
import lmctl.utils.descriptors as descriptors
import lmctl.files as files
from .etsi_ns_content import EtsiNsPkgContentTree

class EtsiNsSourceTree(assembly_api.AssemblySourceTree):
    def __init__(self, root_path=None):
        super().__init__(root_path)

    MANIFEST_FILE = 'MRF.mf'
    FILES_DIRECTORY = 'Files'
    DEFINITIONS_DIR = 'Definitions'
    TEST_CONFIG_DIRECTORY = os.path.join('Files', 'Tests', 'Configurations')
    TEST_RUNTIME_DIRECTORY = os.path.join('Files', 'Tests', 'Runtime Scenarios')
    TEST_SCENARIOS_DIRECTORY = os.path.join('Files', 'Tests', 'Test Scenarios')

    @property
    def manifest_file_path(self):
        mf_path = self.resolve_relative_path(EtsiNsSourceTree.MANIFEST_FILE)
        if os.path.exists(mf_path):
            return mf_path

    @property
    def files_dir_path(self):
        files_path = self.resolve_relative_path(EtsiNsSourceTree.FILES_DIRECTORY)
        if os.path.exists(files_path):
            return files_path

    @property
    def definitions_dir_path(self):
        definitions_dir = self.resolve_relative_path(EtsiNsSourceTree.DEFINITIONS_DIR)
        if os.path.exists(definitions_dir):
            return definitions_dir


    @property
    def descriptor_definitions_file_path(self):
        yml_path = self.resolve_relative_path(EtsiNsSourceTree.DEFINITIONS_DIR, EtsiNsSourceTree.DESCRIPTOR_FILE_YML)
        yaml_path = self.resolve_relative_path(EtsiNsSourceTree.DEFINITIONS_DIR, EtsiNsSourceTree.DESCRIPTOR_FILE_YAML)
        if os.path.exists(yaml_path):
            if os.path.exists(yml_path):
                raise handlers_api.InvalidSourceError('Project has both a {0} file and a {1} file when there should only be one'.format(
                    EtsiNsSourceTree.DESCRIPTOR_FILE_YML, EtsiNsSourceTree.DESCRIPTOR_FILE_YAML))
            return yaml_path
        else:
            return yml_path
            

    @property
    def etsi_test_config_dir_path(self):
        dir = self.resolve_relative_path(EtsiNsSourceTree.TEST_CONFIG_DIRECTORY)
        return dir

    @property
    def etsi_test_runtime_scenarios_dir_path(self):
        dir = self.resolve_relative_path(EtsiNsSourceTree.TEST_RUNTIME_DIRECTORY)
        return dir
    
    @property
    def etsi_test_scenarios_dir_path(self):
        dir = self.resolve_relative_path(EtsiNsSourceTree.TEST_SCENARIOS_DIRECTORY)
        return dir            

class EtsiNsSourceHandler(assembly_api.AssemblySourceHandler):
    def __init__(self, root_path, source_config):        
        super().__init__(root_path, source_config)
        self.tree = EtsiNsSourceTree(self.root_path)        

    def stage_sources(self, journal, source_stager):
        staging_tree = EtsiNsSourceTree()
        # add assembly descriptor to Definitions dir
        project_descriptor_name = self.__stage_descriptor(journal, source_stager, staging_tree)
        # tests
        self.__stage_service_behaviour(journal, source_stager, staging_tree, project_descriptor_name)
        # etsi stock files (changelog, License etc.)
        self.__stage_etsi_files(journal, source_stager, staging_tree)

    def __stage_descriptor(self, journal, source_stager, staging_tree):
        descriptor_path = self.tree.descriptor_file_path
        journal.stage('Staging assembly descriptor for {0} at {1}'.format(self.source_config.name, descriptor_path))
        staged_descriptor_path = source_stager.stage_descriptor(descriptor_path, staging_tree.descriptor_definitions_file_path)
        descriptor = descriptors.DescriptorParser().read_from_file(staged_descriptor_path)
        return descriptor.get_name()

    def __stage_etsi_files(self, journal, source_stager, staging_tree):
        manifest_path = self.tree.manifest_file_path
        journal.stage('Staging Manifest file for {0} at {1}'.format(self.source_config.name, manifest_path))
        source_stager.stage_file(manifest_path, staging_tree.manifest_file_path)
        # contents of Files directory
        files_dir = self.tree.files_dir_path
        journal.stage('Staging Files Directory for {0} at {1}'.format(self.source_config.name, files_dir))
        source_stager.stage_tree(files_dir, staging_tree.files_dir_path)
        # add Definitions dir content (MRF.yml etc.)
        definitions_dir = self.tree.definitions_dir_path
        source_stager.stage_tree(definitions_dir, staging_tree.definitions_dir_path)        
        

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
        runtimes_path = self.tree.service_behaviour_runtime_path
        if os.path.exists(runtimes_path):
            journal.event('Staging runtime tests at: {0}'.format(runtimes_path))
            walk_and_find_json(runtimes_path, self.__stage_behaviour_runtime, staging_tree, source_stager)
        else:
            journal.event('Skipping - no runtime tests found at: {0}'.format(runtimes_path))
        tests_path = self.tree.service_behaviour_tests_path
        if os.path.exists(tests_path):
            journal.event('Staging tests at: {0}'.format(tests_path))
            walk_and_find_json(tests_path, self.__stage_behaviour_test, staging_tree, source_stager)
        else:
            journal.event('Skipping - no tests found at: {0}'.format(tests_path))

    def __stage_behaviour_configuration(self, configuration_path, configuration, staging_tree, source_stager, journal):
        relative_staging_path = os.path.join(staging_tree.etsi_test_config_dir_path, os.path.basename(configuration_path))
        source_stager.stage_file(configuration_path, relative_staging_path, behaviour_mutations.AssemblyConfigurationStagingMutator(self.source_config, source_stager.references, journal))

    def __stage_behaviour_runtime(self, runtime_path, runtime, staging_tree, source_stager):
        relative_staging_path = os.path.join(staging_tree.etsi_test_runtime_scenarios_dir_path, os.path.basename(runtime_path))
        source_stager.stage_file(runtime_path, relative_staging_path, behaviour_mutations.ScenarioStagingMutator(self.source_config))

    def __stage_behaviour_test(self, test_path, test, staging_tree, source_stager):
        relative_staging_path = os.path.join(staging_tree.etsi_test_scenarios_dir_path, os.path.basename(test_path))
        source_stager.stage_file(test_path, relative_staging_path, behaviour_mutations.ScenarioStagingMutator(self.source_config))


    def build_staged_source_handler(self, staging_path):
        return EtsiStagedSourceHandler(staging_path, self.source_config)

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


class EtsiNsSourceCreator(assembly_api.AssemblySourceCreator):
    def __init__(self):        
        super().__init__()

    def _do_create_source(self, journal, source_request):
        super()._do_create_source(journal, source_request)

class EtsiStagedSourceHandler(assembly_api.AssemblyStagedSourceHandler):
    def __init__(self, root_path, source_config):
        super().__init__(root_path, source_config)
        self.tree = EtsiNsPkgContentTree(self.root_path)


    def compile_sources(self, journal, source_compiler):
        compile_tree = EtsiNsPkgContentTree()

        journal.event('Compiling additional ETSI files for: {0}'.format(self.source_config.full_name))
        source_compiler.compile_tree(self.tree.files_dir_path, compile_tree.files_dir_path)
        source_compiler.compile_file(self.tree.manifest_file_path, compile_tree.manifest_file_path)
        source_compiler.compile_tree(self.tree.definitions_dir_path, compile_tree.definitions_dir_path)
