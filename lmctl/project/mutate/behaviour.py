from .base import Mutator
import json
import lmctl.reference as refs


def deprecated_behaviour_descriptor_reference():
    return '$lmctl.descriptor_name'

def is_deprecated_behaviour_descriptor_reference(value):
    return value == deprecated_behaviour_descriptor_reference()


class BehaviourMutator(Mutator):

    def _set_project_id(self, source_element, project_id):
        source_element['projectId'] = project_id
        return source_element


class AssemblyConfigurationStagingMutator(BehaviourMutator):

    def __init__(self, project_config, config_references, journal):
        self.project_config = project_config
        self.config_references = config_references
        self.journal = journal

    def apply(self, original_content):
        orig_configuration = json.loads(original_content)
        new_configuration = self._set_project_id(orig_configuration, self.project_config.descriptor_name)
        new_configuration = self.__replace_descriptor_refs_with_name(new_configuration)
        return json.dumps(new_configuration, indent=2)

    def __replace_descriptor_refs_with_name(self, assembly_configuration):
        assembly_configuration = self.__replace_deprecated_descriptor_refs_with_name(assembly_configuration)
        if 'descriptorName' in assembly_configuration:
            current_name = assembly_configuration['descriptorName']
            if self.config_references.is_reference(current_name):
                try:
                    resolved_value = self.config_references.resolve(current_name)
                    if resolved_value is not None:
                        assembly_configuration['descriptorName'] = resolved_value
                except (refs.NotResolvableError, refs.BadReferenceError) as e:
                    self.journal.event('Cannot resolve reference: {0}'.format(current_name))
        return assembly_configuration

    def __replace_deprecated_descriptor_refs_with_name(self, assembly_configuration):
        if 'descriptorNameRef' in assembly_configuration:
            if is_deprecated_behaviour_descriptor_reference(assembly_configuration['descriptorNameRef']) is True:
                assembly_configuration.pop("descriptorNameRef", None)
                assembly_configuration['descriptorName'] = self.project_config.descriptor_name
        return assembly_configuration


class AssemblyConfigurationPullMutator(BehaviourMutator):

    def __init__(self, project_config, config_references, journal):
        self.project_config = project_config
        self.config_references = config_references
        self.journal = journal

    def apply(self, original_content):
        new_content = original_content
        if 'id' in new_content:
            del new_content['id']
        new_content['projectId'] = self.config_references.build_descriptor_reference(self.project_config)
        new_content = self.__replace_descriptor_name_with_ref(new_content)
        return new_content

    def __replace_descriptor_name_with_ref(self, assembly_configuration):
        if 'descriptorName' in assembly_configuration:
            current_descriptor_name = assembly_configuration['descriptorName']
            project_for_descriptor_reference = self.config_references.build_descriptor_to_project_mapping_reference(current_descriptor_name)
            try:
                resolved_project = self.config_references.resolve(project_for_descriptor_reference)
                if resolved_project is not None:
                    assembly_configuration['descriptorName'] = self.config_references.build_descriptor_reference(resolved_project)
            except (refs.NotResolvableError, refs.BadReferenceError) as e:
                self.journal.event('Cannot resolve reference: {0}'.format(project_for_descriptor_reference))
        return assembly_configuration

class ScenarioStagingMutator(BehaviourMutator):

    def __init__(self, project_config):
        self.project_config = project_config

    def apply(self, original_scenario_content):
        orig_scenario = json.loads(original_scenario_content)
        new_scenario = self._set_project_id(orig_scenario, self.project_config.descriptor_name)
        return json.dumps(new_scenario, indent=2)


class ScenarioPushMutator(BehaviourMutator):

    def __init__(self, available_configurations):
        self.available_configurations = available_configurations

    def apply(self, original_scenario):
        return self.__replace_actor_refs_with_ids(original_scenario)

    def __replace_actor_refs_with_ids(self, scenario):
        for actor in scenario['assemblyActors']:
            if not actor['provided']:
                if "baseConfigurationRef" in actor:
                    configuration_ref = actor["baseConfigurationRef"]
                    configuration_id_to_use = configuration_ref

                    matching_configuration = self.__find_assembly_configuration_by_name(configuration_ref)
                    if matching_configuration is not None:
                        configuration_id_to_use = matching_configuration["id"]

                    actor.pop("baseConfigurationRef", None)
                    actor["baseConfigurationId"] = configuration_id_to_use
                if "assemblyConfigurationRef" in actor:
                    configuration_ref = actor["assemblyConfigurationRef"]
                    configuration_id_to_use = configuration_ref

                    matching_configuration = self.__find_assembly_configuration_by_name(configuration_ref)
                    if matching_configuration is not None:
                        configuration_id_to_use = matching_configuration["id"]

                    actor.pop("assemblyConfigurationRef", None)
                    actor["assemblyConfigurationId"] = configuration_id_to_use
        return scenario

    def __find_assembly_configuration_by_name(self, assembly_name):
        return next((x for x in self.available_configurations if x["name"] == assembly_name), None)


class ScenarioPullMutator(BehaviourMutator):

    def __init__(self, project_config, config_references, configurations_by_id):
        self.project_config = project_config
        self.config_references = config_references
        self.configurations_by_id = configurations_by_id

    def apply(self, original_scenario):
        new_scenario = original_scenario
        if 'id' in new_scenario:
            del new_scenario['id']
        new_scenario['projectId'] = self.config_references.build_descriptor_reference(self.project_config)
        return self.__swap_assembly_configuration_ids_for_names(new_scenario)

    def __swap_assembly_configuration_ids_for_names(self, scenario):
        for actor in scenario['assemblyActors']:
            if not actor['provided']:
                if 'baseConfigurationId' in actor and actor['baseConfigurationId'] != None:
                    configuration_id = actor["baseConfigurationId"]
                    configuration_name = configuration_id
                    if configuration_id in self.configurations_by_id:
                        configuration_name = self.configurations_by_id[configuration_id]["name"]
                    actor.pop("baseConfigurationId", None)
                    actor["baseConfigurationRef"] = configuration_name
                if 'assemblyConfigurationId' in actor and actor['assemblyConfigurationId'] != None:
                    configuration_id = actor["assemblyConfigurationId"]
                    configuration_name = configuration_id
                    if configuration_id in self.configurations_by_id:
                        configuration_name = self.configurations_by_id[configuration_id]["name"]
                    actor.pop("assemblyConfigurationId", None)
                    actor["assemblyConfigurationRef"] = configuration_name
        return scenario
