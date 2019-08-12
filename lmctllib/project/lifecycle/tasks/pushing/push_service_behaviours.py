import os
import json
import lmctllib.utils.descriptors as descriptor_utils
from ..tasks import ProjectLifecycleTask

class DeployServiceBehaviours(ProjectLifecycleTask):
    """
    Pushes Scenarios and Assembly Configurations from the push workspace to a target LM environment
    """
    def __init__(self):
        super().__init__("Deploy Service Behaviour")
    
    def execute_work(self, tools, products):
        env = self._get_environment()
        lm_env = env.lm
        target_descriptor_path = self._get_project_tree().pushWorkspace().content().serviceDescriptor().descriptorFile()
        if os.path.exists(target_descriptor_path):
            descritor_content = descriptor_utils.DescriptorReader.readDictionary(target_descriptor_path)
            descriptor = descriptor_utils.DescriptorModel(descritor_content)
            project_id = descriptor.getName()        
        else:
            return self._return_failure('No service descriptor was found at {0}'.format(target_descriptor_path))

        behaviour_path = self._get_project_tree().pushWorkspace().content().serviceBehaviour().directory()
        if os.path.exists(behaviour_path):
            existing_configurations = lm_env.getBehaviourDriver().getAssemblyTemplates(project_id)
            existing_scenarios = lm_env.getBehaviourDriver().getScenarios(project_id)
            self.__pushAssemblyTemplates(project_id, lm_env, existing_configurations)
            all_available_configurations = lm_env.getBehaviourDriver().getAssemblyTemplates(project_id)
            self.__pushTestScenarios(project_id, lm_env, existing_scenarios, all_available_configurations)
            existing_scenarios = lm_env.getBehaviourDriver().getScenarios(project_id)
            self.__pushRuntimeScenarios(project_id, lm_env, existing_scenarios, all_available_configurations)
        else:
            return self._return_skipped('No service behaviour directory found at {0}'.format(behaviour_path))
        return self._return_passed()

    def __pushAssemblyTemplates(self, project_id, lm_env, existing_configurations):
        templates_path = self._get_project_tree().pushWorkspace().content().serviceBehaviour().templatesDirectory()
        if os.path.exists(templates_path):
            for root, dirs, files in os.walk(templates_path):  
                for filename in files:
                    if(filename.endswith(".json")):
                        file_path = os.path.join(root, filename)
                        with open(file_path, 'rt') as f:
                            template_content = json.loads(f.read())
                            self.__pushAssemblyTemplate(project_id, lm_env, template_content, existing_configurations)
        else:
            self._get_journal().add_text('No templates found at {0}'.format(templates_path))

    def __pushTestScenarios(self, project_id, lm_env, existing_scenarios, all_available_configurations):
        tests_path = self._get_project_tree().pushWorkspace().content().serviceBehaviour().testsDirectory()
        if os.path.exists(tests_path):
            for root, dirs, files in os.walk(tests_path):  
                for filename in files:
                    if(filename.endswith(".json")):
                        file_path = os.path.join(root, filename)
                        with open(file_path, 'rt') as f:
                            scenario_content = json.loads(f.read())
                            self.__pushScenario(project_id, lm_env, scenario_content, existing_scenarios, all_available_configurations)
        else:
            self._get_journal().add_text('No tests found at {0}'.format(tests_path))

    def __pushRuntimeScenarios(self, project_id, lm_env, existing_scenarios, all_available_configurations):
        runtime_path = self._get_project_tree().pushWorkspace().content().serviceBehaviour().runtimeDirectory()
        if os.path.exists(runtime_path):
            for root, dirs, files in os.walk(runtime_path):  
                for filename in files:
                    if(filename.endswith(".json")):
                        file_path = os.path.join(root, filename)
                        with open(file_path, 'rt') as f:
                            scenario_content = json.loads(f.read())
                            self.__pushScenario(project_id, lm_env, scenario_content, existing_scenarios, all_available_configurations)
        else:
            self._get_journal().add_text('No runtime scenarios found at {0}'.format(runtime_path))

    def __pushAssemblyTemplate(self, project_id, lm_env, template, existing_configurations):
        template['projectId'] = project_id
        behaviour_driver = lm_env.getBehaviourDriver()
        self._get_journal().add_text('Checking for Assembly Configuration {0} in LM ({1}) project {2}'.format(template['name'], lm_env.getUrl(), project_id))
        matching_configuration = self.__findAssemblyConfigurationByName(existing_configurations, template['name'])
        if matching_configuration:
            self._get_journal().add_text('Assembly Template {0} already exists, updating'.format(template['name']))
            template['id'] = matching_configuration['id']
            behaviour_driver.updateAssemblyTemplate(template)
        else:
            self._get_journal().add_text('Not found, creating Assembly Template {0}'.format(template['name']))
            behaviour_driver.createAssemblyTemplate(template)

    def __pushScenario(self, project_id, lm_env, scenario, existing_scenarios, all_available_configurations):
        scenario['projectId'] = project_id
        behaviour_driver = lm_env.getBehaviourDriver()
        self.__replaceActorRefsWithIds(scenario, all_available_configurations)
        self._get_journal().add_text('Checking for Scenario {0} in LM ({1}) project {2}'.format(scenario['name'], lm_env.getUrl(), project_id))
        matching_scenario = next((x for x in existing_scenarios if x["name"] == scenario['name']), None)
        if matching_scenario:
            self._get_journal().add_text('Scenario {0} already exists, updating'.format(scenario['name']))
            scenario['id'] = matching_scenario['id']
            behaviour_driver.updateScenario(scenario)
        else:
            self._get_journal().add_text('Not found, creating Scenario {0}'.format(scenario['name']))
            behaviour_driver.createScenario(scenario)

    def __replaceActorRefsWithIds(self, scenario, all_available_configurations):
        for actor in scenario['assemblyActors']:
            if not actor['provided']:
                if "assemblyConfigurationRef" in actor:
                  configuration_ref = actor["assemblyConfigurationRef"]
                  configuration_id_to_use = configuration_ref

                  matching_configuration = self.__findAssemblyConfigurationByName(all_available_configurations, configuration_ref)
                  if matching_configuration is not None:
                      configuration_id_to_use = matching_configuration["id"]

                  actor.pop("assemblyConfigurationRef" ,None)
                  actor["assemblyConfigurationId"] = configuration_id_to_use

    def __findAssemblyConfigurationByName(self, all_available_configurations, assembly_name):
        return next((x for x in all_available_configurations if x["name"] == assembly_name), None)
