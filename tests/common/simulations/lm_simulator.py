from unittest.mock import MagicMock
from lmctl.environment.lmenv import LmSession, LmEnvironment
import lmctl.drivers.lm as lm_drivers
import lmctl.utils.descriptors as descriptor_utils
import uuid
import threading
import time
import tempfile
import shutil
import zipfile
import yaml
import os

class NotFoundError(Exception):
    pass

class DuplicateError(Exception):
    pass

class LmSimulator:

    def __init__(self):
        pass

    def start(self):
        return SimulatedLm()

class Trigger:

    def __init__(self, usage_expiration=-1):
        self.usage_expiration = usage_expiration

class StepFailureTrigger(Trigger):

    def __init__(self, project_id, scenario_name, stage_idx, step_idx, error, usage_expiration=-1):
        super().__init__(usage_expiration)
        self.project_id = project_id
        self.scenario_name = scenario_name
        self.stage_idx = stage_idx
        self.step_idx = step_idx
        self.error = error

    def is_match(self, project_id, scenario_name, stage_idx, step_idx):
        return project_id == self.project_id \
            and scenario_name == self.scenario_name \
            and stage_idx == self.stage_idx \
            and step_idx == self.step_idx

class ScenarioExecutionListener:

    def __init__(self):
        self.step_failure_triggers = []

    def add_step_failure_trigger(self, project_id, scenario_name, stage_idx, step_idx, error, usage_expiration=-1):
        self.step_failure_triggers.append(StepFailureTrigger(project_id, scenario_name, stage_idx, step_idx, error, usage_expiration))

    def execution_started(self, project_id, execution):
        return (True, None)

    def __find_step_failure_trigger(self, project_id, execution, stage_idx, step_idx):
        scenario_name = execution['scenarioSummary']['name']
        for trigger in self.step_failure_triggers:
            if trigger.is_match(project_id, scenario_name, stage_idx, step_idx):
                return trigger

    def step_execution(self, project_id, execution, stage, stage_idx, step, step_idx):
        failure_trigger = self.__find_step_failure_trigger(project_id, execution, stage_idx, step_idx)
        if failure_trigger:
            return (False, failure_trigger.error)
        time.sleep(0.1)
        return (True, None)

    def execution_finished(self, project_id, execution, passed):
        return (True, None)

class SimulatedLm:

    def __init__(self):
        self.descriptors = {}
        self.descriptor_templates = {}
        self.projects = {}
        self.assembly_configurations = {}
        self.assembly_configurations_by_project = {}
        self.scenarios = {}
        self.scenarios_by_project = {}
        self.scenario_executions = {}
        self.executions_by_scenario = {}
        self.scenario_execution_threads = {}
        self.execution_listener = ScenarioExecutionListener()
        self.resource_packages = {}
        self.rms = {}
        self.deployment_locations = {}
        self.deployment_locations_by_rm = {}
        self.vim_drivers = {}
        self.lifecycle_drivers = {}
        self.resource_drivers = {}
        self.infrastructure_keys = {}
        self.mock = MagicMock()

    def __get(self, entity_map, entity_id):
        if entity_id in entity_map:
            return entity_map[entity_id]
        else:
            raise NotFoundError('{0} not found'.format(entity_id))

    def __add(self, entity_map, entity_id, entity):
        if entity_id in entity_map:
            raise DuplicateError('{0} exists'.format(entity_id))
        entity_map[entity_id] = entity

    def __delete(self, entity_map, entity_id):
        if entity_id in entity_map:
            del entity_map[entity_id]
        else:
            raise NotFoundError('{0} not found'.format(entity_id))

    def __update(self, entity_map, entity_id, entity):
        if entity_id in entity_map:
            entity_map[entity_id] = entity
        else:
            raise NotFoundError('{0} not found'.format(entity_id))

    def __add_relation(self, relation_map, parent_id, parent_map, other_entity_id, other_entity_map):
        if parent_id not in parent_map:
            raise NotFoundError('{0} not found'.format(parent_id))
        if other_entity_id not in other_entity_map:
            raise NotFoundError('{0} not found'.format(other_entity_id))
        if parent_id not in relation_map:
            relation_map[parent_id] = []
        if other_entity_id not in relation_map[parent_id]:
            relation_map[parent_id].append(other_entity_id)

    def __remove_from_relations(self, relation_map, target_entity_id):
        for relation_id, relation_values in relation_map.items():
            if target_entity_id in relation_values:
                relation_values.remove(target_entity_id)

    def __get_relations(self, relation_map, parent_id, entity_map):
        if parent_id not in relation_map:
            return []
        relations = []
        relation_ids = relation_map[parent_id]
        for relation_id in relation_ids:
            if relation_id in entity_map:
                relations.append(entity_map[relation_id])
        return relations

    def get_descriptor(self, descriptor_name):
        self.mock.get_descriptor(descriptor_name)
        descriptor = self.__get(self.descriptors, descriptor_name)
        return descriptor

    def add_descriptor(self, descriptor):
        self.mock.add_descriptor(descriptor)
        parsed_descriptor = descriptor_utils.DescriptorParser().read_from_str(descriptor)
        self.__add(self.descriptors, parsed_descriptor.get_name(), descriptor)
        if parsed_descriptor.get_name() not in self.projects:
            self.__add(self.projects, parsed_descriptor.get_name(), {'id': parsed_descriptor.get_name(), 'name': parsed_descriptor.get_name()})

    def delete_descriptor(self, descriptor_name):
        self.mock.delete_descriptor(descriptor_name)
        self.__delete(self.descriptors, descriptor_name)

    def update_descriptor(self, descriptor):
        self.mock.update_descriptor(descriptor)
        parsed_descriptor = descriptor_utils.DescriptorParser().read_from_str(descriptor)
        self.__update(self.descriptors, parsed_descriptor.get_name(), descriptor)

    def get_descriptor_template(self, descriptor_name):
        self.mock.get_descriptor_template(descriptor_name)
        descriptor = self.__get(self.descriptor_templates, descriptor_name)
        return descriptor

    def add_descriptor_template(self, descriptor_template):
        self.mock.add_descriptor_template(descriptor_template)
        parsed_descriptor = descriptor_utils.DescriptorParser().read_from_str(descriptor_template)
        self.__add(self.descriptor_templates, parsed_descriptor.get_name(), descriptor_template)
        if parsed_descriptor.get_name() not in self.projects:
            self.__add(self.projects, parsed_descriptor.get_name(), {'id': parsed_descriptor.get_name(), 'name': parsed_descriptor.get_name()})

    def delete_descriptor_template(self, descriptor_name):
        self.mock.delete_descriptor_template(descriptor_name)
        self.__delete(self.descriptor_templates, descriptor_name)

    def update_descriptor_template(self, descriptor_template):
        self.mock.update_descriptor_template(descriptor_template)
        parsed_descriptor = descriptor_utils.DescriptorParser().read_from_str(descriptor_template)
        self.__update(self.descriptor_templates, parsed_descriptor.get_name(), descriptor_template)

    def add_resource_package(self, package_name, package_content):
        self.mock.add_package(package_name, package_content)
        self.__add(self.resource_packages, package_name, package_content)

    def delete_resource_package(self, package_name):
        self.mock.delete_package(package_name)
        self.__delete(self.resource_packages, package_name)

    def add_rm(self, rm):
        self.mock.add_rm(rm)
        self.__add(self.rms, rm['name'], rm)

    def update_rm(self, rm):
        self.mock.update_rm(rm)
        self.__update(self.rms, rm['name'], rm)

    def delete_rm(self, rm_name):
        self.mock.delete_rm(rm_name)
        self.__delete(self.rms, rm_name)

    def get_rm(self, rm_name):
        self.mock.get_rm(rm_name)
        rm = self.__get(self.rms, rm_name)
        return rm

    def get_deployment_location(self, deployment_location_id):
        self.mock.get_deployment_location(deployment_location_id)
        dl = self.__get(self.deployment_locations, deployment_location_id)
        return dl

    def add_deployment_location(self, deployment_location):
        self.mock.add_deployment_location(deployment_location)
        if 'id' not in deployment_location:
            deployment_location = deployment_location.copy()
            deployment_location['id'] = str(uuid.uuid4())
        self.__add(self.deployment_locations, deployment_location['id'], deployment_location)
        self.__add_relation(self.deployment_locations_by_rm, deployment_location['resourceManager'], self.rms, deployment_location['id'], self.deployment_locations)
        return deployment_location

    def delete_deployment_location(self, deployment_location):
        self.mock.delete_deployment_location(deployment_location)
        self.__delete(self.deployment_locations, deployment_location)

    def get_deployment_locations(self):
        self.mock.get_deployment_locations()
        dl_list = []
        for dl_id, dl in self.deployment_locations.items():
            dl_list.append(dl)
        return dl_list

    def get_deployment_locations_by_name(self, dl_name):
        self.mock.get_deployment_locations_by_name(dl_name)
        dl_list = []
        for dl_id, dl in self.deployment_locations.items():
            if 'name' in dl:
                if dl['name'] == dl_name:
                    dl_list.append(dl)
        return dl_list

    def get_project(self, project_id):
        self.mock.get_project(project_id)
        project = self.__get(self.projects, project_id)
        return project

    def add_project(self, project):
        self.mock.add_project(project)
        self.__add(self.projects, project['id'], project)

    def update_project(self, project):
        self.mock.update_project(project)
        self.__update(self.projects, project['id'], project)

    def get_assembly_configuration(self, assembly_configuration_id):
        self.mock.get_assembly_configuration(assembly_configuration_id)
        config = self.__get(self.assembly_configurations, assembly_configuration_id)
        return config

    def add_assembly_configuration(self, assembly_configuration):
        self.mock.add_assembly_configuration(assembly_configuration)
        if 'id' not in assembly_configuration:
            assembly_configuration = assembly_configuration.copy()
            assembly_configuration['id'] = str(uuid.uuid4())
        self.__add(self.assembly_configurations, assembly_configuration['id'], assembly_configuration)
        self.__add_relation(self.assembly_configurations_by_project, assembly_configuration['projectId'], self.projects, assembly_configuration['id'], self.assembly_configurations)

    def update_assembly_configuration(self, assembly_configuration):
        self.mock.update_assembly_configuration(assembly_configuration)
        self.__remove_from_relations(self.assembly_configurations_by_project, assembly_configuration['id'])
        self.__update(self.assembly_configurations, assembly_configuration['id'], assembly_configuration)
        self.__add_relation(self.assembly_configurations_by_project, assembly_configuration['projectId'], self.projects, assembly_configuration['id'], self.assembly_configurations)

    def get_assembly_configurations_on_project(self, project_id):
        self.mock.get_assembly_configurations_on_project(project_id)
        self.get_project(project_id)
        relations = self.__get_relations(self.assembly_configurations_by_project, project_id, self.assembly_configurations)
        return relations

    def get_scenario(self, scenario_id):
        self.mock.get_scenario(scenario_id)
        scenario = self.__get(self.scenarios, scenario_id)
        return scenario

    def add_scenario(self, scenario):
        self.mock.add_scenario(scenario)
        if 'id' not in scenario:
            scenario = scenario.copy()
            scenario['id'] = str(uuid.uuid4())
        self.__add(self.scenarios, scenario['id'], scenario)
        self.__add_relation(self.scenarios_by_project, scenario['projectId'], self.projects, scenario['id'], self.scenarios)

    def update_scenario(self, scenario):
        self.mock.update_scenario(scenario)
        self.__remove_from_relations(self.scenarios_by_project, scenario['id'])
        self.__update(self.scenarios, scenario['id'], scenario)
        self.__add_relation(self.scenarios_by_project, scenario['projectId'], self.projects, scenario['id'], self.scenarios)

    def get_scenarios_on_project(self, project_id):
        self.mock.get_scenarios_on_project(project_id)
        self.get_project(project_id)
        relations = self.__get_relations(self.scenarios_by_project, project_id, self.scenarios)
        return relations

    def execute_scenario(self, scenario_id):
        self.mock.execute_scenario(scenario_id)
        scenario = self.get_scenario(scenario_id)
        execution = {
            'id': scenario['id'] + '-' + str(uuid.uuid4()),
            'scenarioId': scenario['id'],
            'name': 'MockExec',
            'scenarioSummary': {
                'name': scenario['name']
            },
            'status': 'PENDING',
            'error': None,
            'stageReports': self.__convert_stages_to_reports(scenario)}
        self.__add(self.scenario_executions, execution['id'], execution)
        self.__add_relation(self.executions_by_scenario, scenario_id, self.scenarios, execution['id'], self.scenario_executions)
        self.__start_execution_thread(scenario['projectId'], execution)
        return execution

    def get_executions_on_scenario(self, scenario_id):
        self.mock.get_executions_on_scenario(scenario_id)
        self.get_scenario(scenario_id)
        relations = self.__get_relations(self.executions_by_scenario, scenario_id, self.scenario_executions)
        return relations

    def __start_execution_thread(self, project_id, execution):
        if not self.execution_listener:
            self.execution_listener = ScenarioExecutionListener()
        exec_thread = threading.Thread(target=self.__execution, args=(project_id, execution, self.execution_listener), daemon=True)
        self.scenario_execution_threads[execution['id']] = exec_thread
        exec_thread.start()

    def __execution(self, project_id, execution, listener):
        try:
            execution_id = execution['id']
            (start_ok, detail) = listener.execution_started(project_id, execution)
            if not start_ok:
                execution['status'] = 'FAIL'
                execution['error'] = detail
            else:
                execution_passed = True
                execution_failure_reason = None
                execution['status'] = 'IN_PROGRESS'
                if 'stageReports' in execution:
                    stage_idx = 0
                    for stage in execution['stageReports']:
                        stage['status'] = 'IN_PROGRESS'
                        stage_passed = True
                        step_idx = 0
                        if 'steps' in stage:
                            for step in stage['steps']:
                                (step_passed, detail) = listener.step_execution(project_id, execution, stage, stage_idx, step, step_idx)
                                if not step_passed:
                                    step['status'] = 'FAIL'
                                    step['error'] = detail
                                    execution_failure_reason = detail
                                else:
                                    step['status'] = 'PASS'
                                stage_passed = stage_passed and step_passed
                                step_idx += 1
                        execution_passed = execution_passed and stage_passed
                        stage_idx += 1
            if execution_passed:
                execution['status'] = 'PASS'
            else:
                execution['status'] = 'FAIL'
                execution['error'] = execution_failure_reason
            listener.execution_finished(project_id, execution, execution_passed)
            if execution_id in self.scenario_execution_threads:
                del self.scenario_execution_threads[execution_id]
        except Exception as e:
            execution['status'] = 'FAIL'
            execution['error'] = str(e)
            raise e

    def get_execution(self, execution_id):
        self.mock.get_execution(execution_id)
        execution = self.__get(self.scenario_executions, execution_id)
        return execution

    def __convert_stages_to_reports(self, scenario):
        stage_reports = []
        if 'stages' in scenario:
            for stage in scenario['stages']:
                stage_report = stage.copy()
                stage_reports.append(stage_report)
                stage_report['status'] = 'PENDING'
                step_reports = []
                stage_report['steps'] = step_reports
                if 'steps' in stage:
                    for step in stage['steps']:
                        step_report = step.copy()
                        step_reports.append(step_report)
                        if 'properties' in step_report:
                            del step_report['properties']
                        step_report['status'] = 'PENDING'
        return stage_reports

    def get_resource_driver(self, driver_id):
        self.mock.get_resource_driver(driver_id)
        resource_driver = self.__get(self.resource_drivers, driver_id)
        return resource_driver

    def get_resource_driver_by_type(self, driver_type):
        self.mock.get_resource_driver_by_type(driver_type)
        for driver_id, driver in self.resource_drivers.items():
            if 'type' in driver:
                if driver['type'] == driver_type:
                    return driver

        raise NotFoundError('Resource driver with type {0} not found'.format(driver_type))

    def add_resource_driver(self, resource_driver):
        self.mock.add_resource_driver(resource_driver)
        if 'id' not in resource_driver:
            resource_driver = resource_driver.copy()
            resource_driver['id'] = str(uuid.uuid4())
        self.__add(self.resource_drivers, resource_driver['id'], resource_driver)
        return resource_driver
       
    def delete_resource_driver(self, resource_driver):
        self.mock.delete_resource_driver(resource_driver)
        self.__delete(self.resource_drivers, resource_driver)

    def get_vim_driver(self, driver_id):
        self.mock.get_vim_driver(driver_id)
        vim_driver = self.__get(self.vim_drivers, driver_id)
        return vim_driver

    def get_vim_driver_by_type(self, inf_type):
        self.mock.get_vim_driver_by_type(inf_type)
        for driver_id, driver in self.vim_drivers.items():
            if 'infrastructureType' in driver:
                if driver['infrastructureType'] == inf_type:
                    return driver
        raise NotFoundError('VIM driver with type {0} not found'.format(inf_type))

    def add_vim_driver(self, vim_driver):
        self.mock.add_vim_driver(vim_driver)
        if 'id' not in vim_driver:
            vim_driver = vim_driver.copy()
            vim_driver['id'] = str(uuid.uuid4())
        self.__add(self.vim_drivers, vim_driver['id'], vim_driver)
        return vim_driver

    def delete_vim_driver(self, vim_driver):
        self.mock.delete_vim_driver(vim_driver)
        self.__delete(self.vim_drivers, vim_driver)

    def get_lifecycle_driver(self, driver_id):
        self.mock.get_lifecycle_driver(driver_id)
        lifecycle_driver = self.__get(self.lifecycle_drivers, driver_id)
        return lifecycle_driver

    def get_lifecycle_driver_by_type(self, lifecycle_type):
        self.mock.get_lifecycle_driver_by_type(lifecycle_type)
        for driver_id, driver in self.lifecycle_drivers.items():
            if 'type' in driver:
                if driver['type'] == lifecycle_type:
                    return driver
        raise NotFoundError('Lifecycle driver with type {0} not found'.format(lifecycle_type))

    def add_lifecycle_driver(self, lifecycle_driver):
        self.mock.add_lifecycle_driver(lifecycle_driver)
        if 'id' not in lifecycle_driver:
            lifecycle_driver = lifecycle_driver.copy()
            lifecycle_driver['id'] = str(uuid.uuid4())
        self.__add(self.lifecycle_drivers, lifecycle_driver['id'], lifecycle_driver)
        return lifecycle_driver

    def delete_lifecycle_driver(self, lifecycle_driver):
        self.mock.delete_lifecycle_driver(lifecycle_driver)
        self.__delete(self.lifecycle_drivers, lifecycle_driver)

    def get_infrastructure_keys(self):
        self.mock.get_infrastructure_keys()
        ik_list = []
        for  ik_id, ik in self.infrastructure_keys.items():
            ik_list.append(ik)
        return ik_list

    def get_infrastructure_key_by_name(self, ik_name):
        self.mock.get_infrastructure_key_by_name(ik_name)
        for  ik_id, ik in self.infrastructure_keys.items():
            if 'name' in ik:
                if ik['name'] == ik_name:
                    return ik
                else:
                    return {}

    def add_infrastructure_key(self, infrastructure_key):
        self.mock.add_infrastructure_key(infrastructure_key)
        if 'id' not in infrastructure_key:
            infrastructure_key = infrastructure_key.copy()
            infrastructure_key['id'] = infrastructure_key['name']
        self.__add(self.infrastructure_keys, infrastructure_key['id'], infrastructure_key)
        return infrastructure_key

    def delete_infrastructure_key(self, infrastructure_key_name):
        self.mock.delete_infrastructure_key(infrastructure_key_name)
        self.__delete(self.infrastructure_keys, infrastructure_key_name)

    def as_mocked_session(self):
        return SimulatedLmSession(self)

class SimulatedLmSession(LmSession):

    def __init__(self, lm_sim):
        self.env = LmEnvironment(address='LmSim', name='sim')
        self.username = None
        self.password = None
        self.sim = lm_sim
        self.__descriptor_driver = MagicMock()
        self.__descriptor_driver_sim = SimDescriptorDriver(self.sim)
        self.__descriptor_template_driver = MagicMock()
        self.__descriptor_template_driver_sim = SimDescriptorTemplateDriver(self.sim)
        self.__onboard_rm_driver = MagicMock()
        self.__onboard_rm_driver_sim = SimOnboardRmDriver(self.sim)
        self.__topology_driver = MagicMock()
        self.__behaviour_driver = MagicMock()
        self.__behaviour_driver_sim = SimBehaviourDriver(self.sim)
        self.__deployment_location_driver = MagicMock()
        self.__deployment_location_driver_sim = SimDeploymentLocationDriver(self.sim)
        self.__resource_pkg_driver = MagicMock()
        self.__resource_pkg_driver_sim = SimResourcePkgDriver(self.sim)
        self.__vim_driver_mgmt_driver = MagicMock()
        self.__vim_driver_mgmt_driver_sim = SimVimDriverMgmtDriver(self.sim)
        self.__lifecycle_driver_mgmt_driver = MagicMock()
        self.__lifecycle_driver_mgmt_driver_sim = SimLifecycleDriverMgmtDriver(self.sim)
        self.__resource_driver_mgmt_driver = MagicMock()
        self.__resource_driver_mgmt_driver_sim = SimResourceDriverMgmtDriver(self.sim)
        self.__infrastructure_keys_driver = MagicMock()
        self.__infrastructure_keys_driver_sim = SimInfrastructureKeysDriver(self.sim)
        self.__configure_mocks()

    def __configure_mocks(self):
        self.__descriptor_driver.delete_descriptor.side_effect = self.__descriptor_driver_sim.delete_descriptor
        self.__descriptor_driver.get_descriptor.side_effect = self.__descriptor_driver_sim.get_descriptor
        self.__descriptor_driver.create_descriptor.side_effect = self.__descriptor_driver_sim.create_descriptor
        self.__descriptor_driver.update_descriptor.side_effect = self.__descriptor_driver_sim.update_descriptor
        self.__descriptor_template_driver.delete_descriptor_template.side_effect = self.__descriptor_template_driver_sim.delete_descriptor_template
        self.__descriptor_template_driver.get_descriptor_template.side_effect = self.__descriptor_template_driver_sim.get_descriptor_template
        self.__descriptor_template_driver.create_descriptor_template.side_effect = self.__descriptor_template_driver_sim.create_descriptor_template
        self.__descriptor_template_driver.update_descriptor_template.side_effect = self.__descriptor_template_driver_sim.update_descriptor_template
        self.__behaviour_driver.create_project.side_effect = self.__behaviour_driver_sim.create_project
        self.__behaviour_driver.update_project.side_effect = self.__behaviour_driver_sim.update_project
        self.__behaviour_driver.get_project.side_effect = self.__behaviour_driver_sim.get_project
        self.__behaviour_driver.create_assembly_configuration.side_effect = self.__behaviour_driver_sim.create_assembly_configuration
        self.__behaviour_driver.update_assembly_configuration.side_effect = self.__behaviour_driver_sim.update_assembly_configuration
        self.__behaviour_driver.get_assembly_configuration.side_effect = self.__behaviour_driver_sim.get_assembly_configuration
        self.__behaviour_driver.get_assembly_configurations.side_effect = self.__behaviour_driver_sim.get_assembly_configurations
        self.__behaviour_driver.create_scenario.side_effect = self.__behaviour_driver_sim.create_scenario
        self.__behaviour_driver.update_scenario.side_effect = self.__behaviour_driver_sim.update_scenario
        self.__behaviour_driver.get_scenario.side_effect = self.__behaviour_driver_sim.get_scenario
        self.__behaviour_driver.get_scenario_by_name.side_effect = self.__behaviour_driver_sim.get_scenario_by_name
        self.__behaviour_driver.get_scenarios.side_effect = self.__behaviour_driver_sim.get_scenarios
        self.__behaviour_driver.execute_scenario.side_effect = self.__behaviour_driver_sim.execute_scenario
        self.__behaviour_driver.get_execution.side_effect = self.__behaviour_driver_sim.get_execution
        self.__resource_pkg_driver.onboard_package.side_effect = self.__resource_pkg_driver_sim.onboard_package
        self.__resource_pkg_driver.delete_package.side_effect = self.__resource_pkg_driver_sim.delete_package
        self.__onboard_rm_driver.update_rm.side_effect = self.__onboard_rm_driver_sim.update_rm
        self.__onboard_rm_driver.get_rm_by_name.side_effect = self.__onboard_rm_driver_sim.get_rm_by_name
        self.__deployment_location_driver.get_locations.side_effect = self.__deployment_location_driver_sim.get_locations
        self.__deployment_location_driver.get_locations_by_name.side_effect = self.__deployment_location_driver_sim.get_locations_by_name
        self.__deployment_location_driver.add_location.side_effect = self.__deployment_location_driver_sim.add_location
        self.__deployment_location_driver.delete_location.side_effect = self.__deployment_location_driver_sim.delete_location
        self.__vim_driver_mgmt_driver.add_vim_driver.side_effect = self.__vim_driver_mgmt_driver_sim.add_vim_driver
        self.__vim_driver_mgmt_driver.delete_vim_driver.side_effect = self.__vim_driver_mgmt_driver_sim.delete_vim_driver
        self.__vim_driver_mgmt_driver.get_vim_driver.side_effect = self.__vim_driver_mgmt_driver_sim.get_vim_driver
        self.__vim_driver_mgmt_driver.get_vim_driver_by_type.side_effect = self.__vim_driver_mgmt_driver_sim.get_vim_driver_by_type
        self.__lifecycle_driver_mgmt_driver.add_lifecycle_driver.side_effect = self.__lifecycle_driver_mgmt_driver_sim.add_lifecycle_driver
        self.__lifecycle_driver_mgmt_driver.delete_lifecycle_driver.side_effect = self.__lifecycle_driver_mgmt_driver_sim.delete_lifecycle_driver
        self.__lifecycle_driver_mgmt_driver.get_lifecycle_driver.side_effect = self.__lifecycle_driver_mgmt_driver_sim.get_lifecycle_driver
        self.__lifecycle_driver_mgmt_driver.get_lifecycle_driver_by_type.side_effect = self.__lifecycle_driver_mgmt_driver_sim.get_lifecycle_driver_by_type
        self.__resource_driver_mgmt_driver.add_resource_driver.side_effect = self.__resource_driver_mgmt_driver_sim.add_resource_driver
        self.__resource_driver_mgmt_driver.delete_resource_driver.side_effect = self.__resource_driver_mgmt_driver_sim.delete_resource_driver
        self.__resource_driver_mgmt_driver.get_resource_driver.side_effect = self.__resource_driver_mgmt_driver_sim.get_resource_driver
        self.__resource_driver_mgmt_driver.get_resource_driver_by_type.side_effect = self.__resource_driver_mgmt_driver_sim.get_resource_driver_by_type
        self.__infrastructure_keys_driver.get_infrastructure_keys.side_effect = self.__infrastructure_keys_driver_sim.get_infrastructure_keys
        self.__infrastructure_keys_driver.get_infrastructure_key_by_name.side_effect = self.__infrastructure_keys_driver_sim.get_infrastructure_key_by_name
        self.__infrastructure_keys_driver.add_infrastructure_key.side_effect = self.__infrastructure_keys_driver_sim.add_infrastructure_key
        self.__infrastructure_keys_driver.delete_infrastructure_key.side_effect = self.__infrastructure_keys_driver_sim.delete_infrastructure_key

    @property
    def descriptor_driver(self):
        return self.__descriptor_driver

    @property
    def descriptor_template_driver(self):
        return self.__descriptor_template_driver

    @property
    def onboard_rm_driver(self):
        return self.__onboard_rm_driver

    @property
    def topology_driver(self):
        return self.__topology_driver

    @property
    def behaviour_driver(self):
        return self.__behaviour_driver

    @property
    def deployment_location_driver(self):
        return self.__deployment_location_driver

    @property
    def resource_pkg_driver(self):
        return self.__resource_pkg_driver

    @property
    def vim_driver_mgmt_driver(self):
        return self.__vim_driver_mgmt_driver

    @property
    def lifecycle_driver_mgmt_driver(self):
        return self.__lifecycle_driver_mgmt_driver

    @property
    def resource_driver_mgmt_driver(self):
        return self.__resource_driver_mgmt_driver

    @property
    def infrastructure_keys_driver(self):
        return self.__infrastructure_keys_driver
        
class SimVimDriverMgmtDriver:
    def __init__(self, sim_lm):
        self.sim_lm = sim_lm

    def add_vim_driver(self, vim_driver):
        try:
            added_vim_driver = self.sim_lm.add_vim_driver(vim_driver)
            return added_vim_driver
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def delete_vim_driver(self, driver_id):
        try:
            self.sim_lm.delete_vim_driver(driver_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No VIM driver with id {0}'.format(driver_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_vim_driver(self, driver_id):
        try:
            return self.sim_lm.get_vim_driver(driver_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No VIM driver with id {0}'.format(driver_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_vim_driver_by_type(self, inf_type):
        try:
            return self.sim_lm.get_vim_driver_by_type(inf_type)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No VIM driver with infrastructure type {0}'.format(inf_type))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

class SimLifecycleDriverMgmtDriver:
    def __init__(self, sim_lm):
        self.sim_lm = sim_lm

    def add_lifecycle_driver(self, lifecycle_driver):
        try:
            added_lifecycle_driver = self.sim_lm.add_lifecycle_driver(lifecycle_driver)
            return added_lifecycle_driver
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def delete_lifecycle_driver(self, driver_id):
        try:
            self.sim_lm.delete_lifecycle_driver(driver_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No lifecycle driver with id {0}'.format(driver_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_lifecycle_driver(self, driver_id):
        try:
            return self.sim_lm.get_lifecycle_driver(driver_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No lifecycle driver with id {0}'.format(driver_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_lifecycle_driver_by_type(self, lifecycle_type):
        try:
            return self.sim_lm.get_lifecycle_driver_by_type(lifecycle_type)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No lifecycle driver with type {0}'.format(lifecycle_type))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

class SimResourceDriverMgmtDriver:
    def __init__(self, sim_lm):
        self.sim_lm = sim_lm

    def add_resource_driver(self, resource_driver):
        try:
            added_resource_driver = self.sim_lm.add_resource_driver(resource_driver)
            return added_resource_driver
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def delete_resource_driver(self, driver_id):
        try:
            self.sim_lm.delete_resource_driver(driver_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No resource driver with id {0}'.format(driver_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_resource_driver(self, driver_id):
        try:
            return self.sim_lm.get_resource_driver(driver_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No resource driver with id {0}'.format(driver_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_resource_driver_by_type(self, driver_type):
        try:
            return self.sim_lm.get_resource_driver_by_type(driver_type)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No resource driver with type {0}'.format(driver_type))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

class SimDescriptorDriver:
    def __init__(self, sim_lm):
        self.sim_lm = sim_lm

    def delete_descriptor(self, descriptor_name):
        try:
            self.sim_lm.delete_descriptor(descriptor_name)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No descriptor with name {0}'.format(descriptor_name))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_descriptor(self, descriptor_name):
        try:
            return self.sim_lm.get_descriptor(descriptor_name)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No descriptor with name {0}'.format(descriptor_name))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def create_descriptor(self, descriptor_content, object_group_id = None):
        try:
            self.sim_lm.add_descriptor(descriptor_content)
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def update_descriptor(self, descriptor_name, descriptor_content):
        try:
            self.sim_lm.update_descriptor(descriptor_content)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No descriptor with name {0}'.format(descriptor_name))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

class SimDescriptorTemplateDriver:
    def __init__(self, sim_lm):
        self.sim_lm = sim_lm

    def delete_descriptor_template(self, descriptor_name):
        try:
            self.sim_lm.delete_descriptor_template(descriptor_name)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No descriptor template with name {0}'.format(descriptor_name))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_descriptor_template(self, descriptor_name):
        try:
            return self.sim_lm.get_descriptor_template(descriptor_name)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No descriptor template with name {0}'.format(descriptor_name))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def create_descriptor_template(self, descriptor_content):
        try:
            self.sim_lm.add_descriptor_template(descriptor_content)
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def update_descriptor_template(self, descriptor_name, descriptor_content):
        try:
            self.sim_lm.update_descriptor_template(descriptor_content)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No descriptor template with name {0}'.format(descriptor_name))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

class SimBehaviourDriver:
    def __init__(self, sim_lm):
        self.sim_lm = sim_lm

    def create_project(self, project):
        try:
            self.sim_lm.add_project(project)
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def update_project(self, project):
        try:
            self.sim_lm.update_project(project)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No project with id {0}'.format(project['id']))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_project(self, project_id):
        try:
            return self.sim_lm.get_project(project_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No project with id {0}'.format(project_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def create_assembly_configuration(self, assembly_configuration):
        try:
            self.sim_lm.add_assembly_configuration(assembly_configuration)
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def update_assembly_configuration(self, assembly_configuration):
        try:
            self.sim_lm.update_assembly_configuration(assembly_configuration)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No assembly_configuration with id {0}'.format(assembly_configuration['id']))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_assembly_configuration(self, assembly_configuration_id):
        try:
            return self.sim_lm.get_assembly_configuration(assembly_configuration_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No assembly_configuration with id {0}'.format(assembly_configuration_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_assembly_configurations(self, project_id):
        try:
            return self.sim_lm.get_assembly_configurations_on_project(project_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No project with id {0}'.format(project_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def create_scenario(self, scenario):
        try:
            self.sim_lm.add_scenario(scenario)
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def update_scenario(self, scenario):
        try:
            self.sim_lm.update_scenario(scenario)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No scenario with id {0}'.format(scenario['id']))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_scenario(self, scenario_id):
        try:
            return self.sim_lm.get_scenario(scenario_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No scenario with id {0}'.format(scenario_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_scenario_by_name(self, project_id, scenario_name):
        scenarios = self.get_scenarios(project_id)
        for scenario in scenarios:
            if scenario['name'] == scenario_name:
                return scenario
        raise lm_drivers.NotFoundException('Scenario: {0} does not exist in project: {1}'.format(scenario_name, project_id))

    def get_scenarios(self, project_id):
        try:
            return self.sim_lm.get_scenarios_on_project(project_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No project with id {0}'.format(project_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def execute_scenario(self, scenario_id):
        try:
            return self.sim_lm.execute_scenario(scenario_id)['id']
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No scenario with id {0}'.format(scenario_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_execution(self, exec_id):
        try:
            return self.sim_lm.get_execution(exec_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No execution with id {0}'.format(exec_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

class SimResourcePkgDriver:

    def __init__(self, sim_lm):
        self.sim_lm = sim_lm

    def __get_resource_type_name(self, resource_pkg_path):
        with open(resource_pkg_path, 'rb') as resource_pkg_contents:
            pkg_content = resource_pkg_contents.read()
        tmp_dir = tempfile.mkdtemp()
        try:
            tmp_pkg = os.path.join(tmp_dir, 'tmp.zip')
            with open(tmp_pkg, 'wb') as w:
                w.write(pkg_content)
            with zipfile.ZipFile(tmp_pkg, mode='r') as zip_reader:
                zip_reader.extractall(tmp_dir)
            descriptor_path = os.path.join(tmp_dir, 'Definitions', 'lm', 'resource.yaml')
            with open(descriptor_path, 'r') as descriptor_file:
                descriptor_content = yaml.safe_load(descriptor_file.read())
            return descriptor_content['name']
        finally:
            shutil.rmtree(tmp_dir)

    def onboard_package(self, resource_pkg_path, object_group_id = None):
        package_name = self.__get_resource_type_name(resource_pkg_path)
        try:
            self.sim_lm.add_resource_package(package_name, resource_pkg_path)
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def delete_package(self, resource_type_name):
        try:
            self.sim_lm.delete_resource_package(resource_type_name)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No resource package with name {0}'.format(resource_type_name))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

class SimOnboardRmDriver:

    def __init__(self, sim_lm):
        self.sim_lm = sim_lm

    def update_rm(self, rm_data):
        rm_name = rm_data['name']
        try:
            self.sim_lm.update_rm(rm_data)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No RM with name {0}'.format(rm_name))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_rm_by_name(self, rm_name):
        try:
            return self.sim_lm.get_rm(rm_name)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No RM with name {0}'.format(rm_name))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

class SimDeploymentLocationDriver:

    def __init__(self, sim_lm):
        self.sim_lm = sim_lm

    def get_locations(self):
        try:
            return self.sim_lm.get_deployment_locations()
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_locations_by_name(self, dl_name):
        try:
            return self.sim_lm.get_deployment_locations_by_name(dl_name)
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def add_location(self, deployment_location):
        try:
            return self.sim_lm.add_deployment_location(deployment_location)
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def delete_location(self, deployment_location_id):
        try:
            return self.sim_lm.delete_deployment_location(deployment_location_id)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No deployment location with id {0}'.format(deployment_location_id))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

class SimInfrastructureKeysDriver:

    def __init__(self, sim_lm):
        self.sim_lm = sim_lm

    def get_infrastructure_keys(self):
        try:
            return self.sim_lm.get_infrastructure_keys()
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def get_infrastructure_key_by_name(self, ik_name):
        try:
            return self.sim_lm.get_infrastructure_key_by_name(ik_name)
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def add_infrastructure_key(self, infrastructure_key):
        try:
            return self.sim_lm.add_infrastructure_key(infrastructure_key)
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e

    def delete_infrastructure_key(self, ik_name):
        try:
            return self.sim_lm.delete_infrastructure_key(ik_name)
        except NotFoundError as e:
            raise lm_drivers.NotFoundException('No infrastructure key with name {0}'.format(ik_name))
        except Exception as e:
            raise lm_drivers.LmDriverException('Error: {0}'.format(str(e))) from e
