import os
import json
import distutils.dir_util
import lmctllib.utils.descriptors as descriptor_utils 
import lmctllib.utils.file_helper as file_helper
import lmctllib.drivers.exception as driver_exceptions
from ..tasks import ProjectLifecycleTask, ProjectLifecycleTaskExecutionException

class PullServiceBehaviours(ProjectLifecycleTask):
    """
    Pulls Assembly Configurations and Scenarios from a target LM environment and saves them in-place of any existing sources
    """
    def __init__(self):
        super().__init__("Pull Service Behaviour Sources")

    def execute_work(self, tools, products):
        self.__backupExisting(tools, products)
        project_id = self.__getProjectId()
        if project_id:
            self.__pull(project_id)
        return self._return_passed()

    def __pull(self, project_id):
        env = self._get_environment()
        lm_env = env.lm
        behaviour_driver = lm_env.getBehaviourDriver()
        journal = self._get_journal()
        journal.add_text('Pulling project {0} from LM ({1})'.format(project_id, lm_env.getUrl()))
        try:
            behaviour_driver.getProject(project_id)
        except driver_exceptions.NotFoundException:
            return self._return_skipped('No project {0} found, skipping pull of service behaviour'.format(project_id))
        
        templates_path = self._get_project_tree().serviceBehaviour().templatesDirectory()
        assembly_templates = behaviour_driver.getAssemblyTemplates(project_id)
        journal.add_text('Found {0} Assembly Template(s) to pull'.format(len(assembly_templates)))
        discovered_templates_by_id = {}
        for assembly_template in assembly_templates:
            template_name = assembly_template['name']
            template_id = assembly_template['id']
            discovered_templates_by_id[template_id] = assembly_template
            file_name = "{0}.json".format(file_helper.safe_filename(template_name))
            file_path = os.path.join(templates_path, file_name)
            journal.add_text('Saving Assembly Template {0} to {1}'.format(template_name, file_path))
            del assembly_template['id']
            with open(file_path, 'w') as out:
                json.dump(assembly_template, out, indent=4)
        
        tests_path = self._get_project_tree().serviceBehaviour().testsDirectory()
        runtime_path = self._get_project_tree().serviceBehaviour().runtimeDirectory()
        scenarios = behaviour_driver.getScenarios(project_id)
        journal.add_text('Found {0} Scenario(s) to pull'.format(len(scenarios)))
        for scenario in scenarios:
            scenario_name = scenario['name']
            file_name = "{0}.json".format(file_helper.safe_filename(scenario_name))
            is_runtime = False
            for actor in scenario['assemblyActors']:
                if actor['provided']:
                    is_runtime = True
            if is_runtime:
                file_path = os.path.join(runtime_path, file_name)
            else:
                file_path = os.path.join(tests_path, file_name)
            self.__swapAssemblyConfigurationIdsForNames(scenario, discovered_templates_by_id)
            journal.add_text('Saving Scenario {0} to {1}'.format(scenario_name, file_path))
            del scenario['id']
            with open(file_path, 'w') as out:
                json.dump(scenario, out, indent=4)
        
    def __swapAssemblyConfigurationIdsForNames(self, scenario, discovered_templates_by_id):
        for actor in scenario['assemblyActors']:
            if not actor['provided']:
                configuration_id = actor["assemblyConfigurationId"]
                configuration_name = configuration_id
                if configuration_id in discovered_templates_by_id:
                    configuration_name = discovered_templates_by_id[configuration_id]["name"]
                actor.pop("assemblyConfigurationId", None)
                actor["assemblyConfigurationRef"] = configuration_name

    def __getProjectId(self):
        service_descriptor_path = self._get_project_tree().serviceDescriptor().descriptorFile()
        if os.path.exists(service_descriptor_path):
            descritor_content = descriptor_utils.DescriptorReader.readDictionary(service_descriptor_path)
            descriptor = descriptor_utils.DescriptorModel(descritor_content)
            project_id = descriptor.getName()
            return project_id     
        else:
            raise ProjectLifecycleTaskExecutionException('No Service descriptor was found at {0}'.format(service_descriptor_path))

    def __backupExisting(self, tools, products):
        service_behaviour_path = self._get_project_tree().serviceBehaviour().directory()
        if os.path.exists(service_behaviour_path):
            backup_dir = self._get_project_tree().backup().serviceBehaviour().directory()
            self._get_journal().add_text('Service behaviour found at {0}, copying to {1}'.format(service_behaviour_path, backup_dir))
            if not os.path.exists(backup_dir):
                self._get_journal().add_text('Creating directory: {0}'.format(backup_dir))
                os.makedirs(backup_dir)
            distutils.dir_util.copy_tree(service_behaviour_path, backup_dir)
        else:
            self._get_journal().add_text('No Service behaviour found at: {0}'.format(service_behaviour_path))