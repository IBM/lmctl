import json
import requests
from .base import LmDriver, NotFoundException


class LmBehaviourDriver(LmDriver):
    """
    Client for the CP4NA orchestration Behaviour APIs
    """

    def __init__(self, lm_base, lm_security_ctrl=None):
        super().__init__(lm_base, lm_security_ctrl)

    def __projects_api(self):
        return '{0}/api/behaviour/projects'.format(self.lm_base)

    def __project_api(self, project_id):
        return '{0}/{1}'.format(self.__projects_api(), project_id)

    def __assembly_configurations_in_project_api(self, project_id):
        return '{0}/api/behaviour/assemblyConfigurations?projectId={1}'.format(self.lm_base, project_id)

    def __assembly_configurations_api(self):
        return '{0}/api/behaviour/assemblyConfigurations'.format(self.lm_base)

    def __assembly_configuration_api(self, template_id):
        return '{0}/api/behaviour/assemblyConfigurations/{1}'.format(self.lm_base, template_id)

    def __scenarios_in_project_api(self, project_id):
        return '{0}/api/behaviour/scenarios?projectId={1}'.format(self.lm_base, project_id)

    def __scenarios_api(self):
        return '{0}/api/behaviour/scenarios'.format(self.lm_base)

    def __scenario_api(self, scenario_id):
        return '{0}/api/behaviour/scenarios/{1}'.format(self.lm_base, scenario_id)

    def __scenario_execs_api(self, scenario_id):
        return '{0}/api/behaviour/executions?scenarioId={1}'.format(self.lm_base, scenario_id)

    def __scenario_exec_api(self, exec_id):
        return '{0}/api/behaviour/executions/{1}'.format(self.lm_base, exec_id)

    def __scenario_execution_api(self):
        return '{0}/api/behaviour/executions'.format(self.lm_base)

    def create_project(self, project):
        url = self.__projects_api()
        headers = self._configure_access_headers()
        response = requests.post(url, json=project, headers=headers, verify=False)
        if response.status_code == 201:
            return True
        else:
            self._raise_unexpected_status_exception(response)

    def update_project(self, project):
        url = self.__project_api(project['id'])
        headers = self._configure_access_headers()
        response = requests.put(url, json=project, headers=headers, verify=False)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            raise NotFoundException('Project does not exist: {0}'.format(project['id']))
        else:
            self._raise_unexpected_status_exception(response)

    def get_project(self, project_id):
        url = self.__project_api(project_id)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            project = response.json()
            return project
        elif response.status_code == 404:
            raise NotFoundException('Project does not exist: {0}'.format(project_id))
        else:
            self._raise_unexpected_status_exception(response)

    def create_assembly_configuration(self, assembly_configuration):
        url = self.__assembly_configurations_api()
        headers = self._configure_access_headers()
        response = requests.post(url, json=assembly_configuration, headers=headers, verify=False)
        if response.status_code == 201:
            return True
        else:
            self._raise_unexpected_status_exception(response)

    def update_assembly_configuration(self, assembly_configuration):
        url = self.__assembly_configuration_api(assembly_configuration['id'])
        headers = self._configure_access_headers()
        response = requests.put(url, json=assembly_configuration, headers=headers, verify=False)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            raise NotFoundException('Assembly Configuration does not exist: {0}'.format(assembly_configuration['id']))
        else:
            self._raise_unexpected_status_exception(response)

    def get_assembly_configuration(self, assembly_configuration_id):
        url = self.__assembly_configuration_api(assembly_configuration_id)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            template = response.json()
            return template
        elif response.status_code == 404:
            raise NotFoundException('Assembly Configuration does not exist: {0}'.format(assembly_configuration_id))
        else:
            self._raise_unexpected_status_exception(response)

    def get_assembly_configurations(self, project_id):
        url = self.__assembly_configurations_in_project_api(project_id)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            templates = response.json()
            return templates
        elif response.status_code == 404:
            raise NotFoundException('Project does not exist: {0}'.format(project_id))
        else:
            self._raise_unexpected_status_exception(response)

    def create_scenario(self, scenario):
        url = self.__scenarios_api()
        headers = self._configure_access_headers()
        response = requests.post(url, json=scenario, headers=headers, verify=False)
        if response.status_code == 201:
            return True
        else:
            self._raise_unexpected_status_exception(response)

    def update_scenario(self, scenario):
        url = self.__scenario_api(scenario['id'])
        headers = self._configure_access_headers()
        response = requests.put(url, json=scenario, headers=headers, verify=False)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            raise NotFoundException('Scenario does not exist: {0}'.format(scenario['id']))
        else:
            self._raise_unexpected_status_exception(response)

    def get_scenario(self, scenario_id):
        url = self.__scenario_api(scenario_id)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            scenario = response.json()
            return scenario
        elif response.status_code == 404:
            raise NotFoundException('Scenario does not exist: {0}'.format(scenario_id))
        else:
            self._raise_unexpected_status_exception(response)

    def get_scenario_by_name(self, project_id, scenario_name):
        scenarios = self.get_scenarios(project_id)
        for scenario in scenarios:
            if scenario['name'] == scenario_name:
                return scenario
        raise NotFoundException('Scenario: {0} does not exist in project: {1}'.format(scenario_name, project_id))

    def get_scenarios(self, project_id):
        url = self.__scenarios_in_project_api(project_id)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            scenarios = response.json()
            return scenarios
        elif response.status_code == 404:
            raise NotFoundException('Project does not exist: {0}'.format(project_id))
        else:
            self._raise_unexpected_status_exception(response)

    def execute_scenario(self, scenario_id):
        url = self.__scenario_execution_api()
        headers = self._configure_access_headers()

        body = {}
        body['scenarioId'] = '{0}'.format(scenario_id)

        response = requests.post(url, json=body, headers=headers, verify=False)
        if response.status_code == 201:
            return response.headers['location']
        elif response.status_code == 404:
            raise NotFoundException('Scenario does not exist: {0}'.format(scenario_id))
        else:
            self._raise_unexpected_status_exception(response)

    def get_execution(self, exec_id):
        url = self.__scenario_exec_api(exec_id)
        headers = self._configure_access_headers()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            execution = response.json()
            return execution
        elif response.status_code == 404:
            raise NotFoundException('Execution does not exist: {0}'.format(exec_id))
        else:
            self._raise_unexpected_status_exception(response)


class DuplicateEntityException(Exception):
    pass
