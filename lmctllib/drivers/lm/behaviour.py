import json
import requests
from ..exception import NotFoundException
from .exception import LmDriverExceptionBuilder

class LmBehaviourDriver:
    """
    Client for the LM Behaviour APIs
    """
    def __init__(self, lm_base, lm_security_ctrl=None):
        """
        Constructs a new instance of the driver

        Args:
            lm_base (str): the base URL of the target LM environment e.g. http://app.lm:32080
            lm_security_ctrl (:obj:`LmSecurityCtrl`): security controller to handle authentication with LM (leave empty if the target environment is insecure)
        """
        self.lm_base=lm_base
        self.lm_security_ctrl = lm_security_ctrl

    def __addAccessHeaders(self, headers=None):
        if headers is None:
            headers = {}
        if self.lm_security_ctrl:
            return self.lm_security_ctrl.addAccessHeaders(headers)
        return headers

    def __projectsApi(self):
        return '{0}/api/behaviour/projects'.format(self.lm_base)

    def __projectApi(self, project_id):
        return '{0}/{1}'.format(self.__projectsApi(), project_id)

    def __assemblyTemplatesInProjectApi(self, project_id):
        return '{0}/api/behaviour/assemblyConfigurations?projectId={1}'.format(self.lm_base, project_id)

    def __assemblyTemplatesApi(self):
        return '{0}/api/behaviour/assemblyConfigurations'.format(self.lm_base)

    def __assemblyTemplateApi(self, template_id):
        return '{0}/api/behaviour/assemblyConfigurations/{1}'.format(self.lm_base, template_id)

    def __scenariosInProjectApi(self, project_id):
        return '{0}/api/behaviour/scenarios?projectId={1}'.format(self.lm_base, project_id)

    def __scenariosApi(self):
        return '{0}/api/behaviour/scenarios'.format(self.lm_base)

    def __scenarioApi(self, scenario_id):
        return '{0}/api/behaviour/scenarios/{1}'.format(self.lm_base, scenario_id)

    def __scenarioExecsApi(self, scenario_id):
        return '{0}/api/behaviour/executions?scenarioId={1}'.format(self.lm_base, scenario_id)

    def __scenarioExecApi(self, exec_id):
        return '{0}/api/behaviour/executions/{1}'.format(self.lm_base, exec_id)

    def __scenarioExecutionApi(self):
        return  '{0}/api/behaviour/executions'.format(self.lm_base)

    def createProject(self, project):
        url = self.__projectsApi()
        headers = self.__addAccessHeaders()
        response = requests.post(url, json=project, headers=headers, verify=False)
        if response.status_code == 201:
            return True
        else:
            LmDriverExceptionBuilder.error(response)

    def updateProject(self, project):
        url = self.__projectApi(project['id'])
        headers = self.__addAccessHeaders()
        response = requests.put(url, json=project, headers=headers, verify=False)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            raise NotFoundException('Project does not exist: {0}'.format(project['id']))
        else:
            LmDriverExceptionBuilder.error(response)
    
    def getProject(self, project_id):
        url = self.__projectApi(project_id)
        headers = self.__addAccessHeaders()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            project = response.json()
            return project
        elif response.status_code == 404:
            raise NotFoundException('Project does not exist: {0}'.format(project_id))
        else:
            LmDriverExceptionBuilder.error(response)

    def createAssemblyTemplate(self, template):
        url = self.__assemblyTemplatesApi()
        headers = self.__addAccessHeaders()
        response = requests.post(url, json=template, headers=headers, verify=False)
        if response.status_code == 201:
            return True
        else:
            LmDriverExceptionBuilder.error(response)

    def updateAssemblyTemplate(self, template):
        url = self.__assemblyTemplateApi(template['id'])
        headers = self.__addAccessHeaders()
        response = requests.put(url, json=template, headers=headers, verify=False)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            raise NotFoundException('Assembly Template does not exist: {0}'.format(template['id']))
        else:
            LmDriverExceptionBuilder.error(response)

    def getAssemblyTemplate(self, template_id):
        url = self.__assemblyTemplateApi(template_id)
        headers = self.__addAccessHeaders()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            template = response.json()
            return template
        elif response.status_code == 404:
            raise NotFoundException('Assembly Template does not exist: {0}'.format(template_id))
        else: 
            LmDriverExceptionBuilder.error(response)

    def getAssemblyTemplates(self, project_id):
        url = self.__assemblyTemplatesInProjectApi(project_id)
        headers = self.__addAccessHeaders()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            templates = response.json()
            return templates
        elif response.status_code == 404:
            raise NotFoundException('Project does not exist: {0}'.format(project_id))
        else:
            LmDriverExceptionBuilder.error(response)  

    def createScenario(self, scenario):
        url = self.__scenariosApi()
        headers = self.__addAccessHeaders()
        response = requests.post(url, json=scenario, headers=headers, verify=False)
        if response.status_code == 201:
            return True
        else:
            LmDriverExceptionBuilder.error(response)

    def updateScenario(self, scenario):
        url = self.__scenarioApi(scenario['id'])
        headers = self.__addAccessHeaders()
        response = requests.put(url, json=scenario, headers=headers, verify=False)
        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            raise NotFoundException('Scenario does not exist: {0}'.format(scenario['id']))
        else:
            LmDriverExceptionBuilder.error(response)

    def getScenario(self, scenario_id):
        url = self.__scenarioApi(scenario_id)
        headers = self.__addAccessHeaders()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            scenario = response.json()
            return scenario
        elif response.status_code == 404:
            raise NotFoundException('Scenario does not exist: {0}'.format(scenario_id))
        else:
            LmDriverExceptionBuilder.error(response)

    def getScenarioByName(self, project_id, scenario_name):
        scenarios = self.getScenarios(project_id)
        for scenario in scenarios:
            if scenario['name'] == scenario_name:
                return scenario
        raise NotFoundException('Scenario: {0} does not exist in project: {1}'.format(scenario_name, project_id)) 

    def getScenarios(self, project_id):
        url = self.__scenariosInProjectApi(project_id)
        headers = self.__addAccessHeaders()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            scenarios = response.json()
            return scenarios
        elif response.status_code == 404:
            raise NotFoundException('Project does not exist: {0}'.format(project_id))
        else:
            LmDriverExceptionBuilder.error(response)


    def executeScenario(self, scenario_id):
        url = self.__scenarioExecutionApi()
        headers = self.__addAccessHeaders()
        
        body = {}
        body['scenarioId'] = '{0}'.format(scenario_id)
        
        response = requests.post(url, json=body, headers=headers, verify=False)
        if response.status_code == 201:
            return response.headers['location']
        elif response.status_code == 404:
            raise NotFoundException('Scenario does not exist: {0}'.format(scenario_id))
        else:
            LmDriverExceptionBuilder.error(response)

    def getExecution(self, exec_id):
        url = self.__scenarioExecApi(exec_id)
        headers = self.__addAccessHeaders()
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            execution = response.json()
            return execution
        elif response.status_code == 404:
            raise NotFoundException('Execution does not exist: {0}'.format(exec_id))
        else:
            LmDriverExceptionBuilder.error(response)

class DuplicateEntityException(Exception):
    pass
