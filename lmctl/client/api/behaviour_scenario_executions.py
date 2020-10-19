from typing import List, Dict
from .resource_api_base import (ResourceAPIBase, 
                                json_response_handler, 
                                obj_json_request_builder, 
                                location_id_response_handler, 
                                APIArg,
                                ReadAPIMeta)

class BehaviourScenarioExecutionsAPI(ResourceAPIBase):
    endpoint = 'api/behaviour/executions'

    # Disable list, create (replaced with execute) and update
    # Keep read and delete
    enable_list_api = False
    enable_create_api = False
    enable_update_api = False

    read_meta = ReadAPIMeta(extra_request_params={
        'include_scenario': APIArg(param_name='includeScenario')
    })
    
    def execute(self, execution_request: Dict = None, scenario_id: str = None) -> str:
        if execution_request is None and scenario_id is None:
            raise ValueError('Must set either "execution_request" or "scenario_id" argument - both were None')
        elif execution_request is None:
            execution_request = {}
        if scenario_id is not None:
            execution_request['scenarioId'] = scenario_id
        request = self._build_request_kwargs('POST', self.endpoint, obj_json_request_builder(obj=execution_request))
        response = self.base_client.make_request(**request)
        return location_id_response_handler(response)
    
    def cancel(self, execution_id: str):
        endpoint = self._execution_cancel_endpoint(execution_id)
        response = self.base_client.make_request(method='POST', endpoint=endpoint)
        return json_response_handler(response)

    def all_in_project(self, project_id: str, include_scenario: bool = False) -> List:
        endpoint = self._by_project_endpoint(project_id)
        response = self.base_client.make_request(method='GET', endpoint=endpoint)
        return json_response_handler(response)

    def all_of_scenario(self, scenario_id: str, include_scenario: bool = False) -> List:
        endpoint = self._by_scenario_endpoint(scenario_id)
        response = self.base_client.make_request(method='GET', endpoint=endpoint)
        return json_response_handler(response)

    def get_progress(self, execution_id: str) -> Dict:
        endpoint = self._execution_progress_endpoint(execution_id)
        response = self.base_client.make_request(method='GET', endpoint=endpoint)
        return json_response_handler(response)

    def get_metrics(self, execution_id: str) -> List:
        endpoint = self._execution_metrics_endpoint(execution_id)
        response = self.base_client.make_request(method='GET', endpoint=endpoint)
        return json_response_handler(response)

    def get_metric(self, execution_id: str, metric_id: str) -> Dict:
        endpoint = self._execution_metric_endpoint(execution_id, metric_id)
        response = self.base_client.make_request(method='GET', endpoint=endpoint)
        return json_response_handler(response)

    def _by_project_endpoint(self, project_id: str) -> str:
        return f'{self.endpoint}?projectId={project_id}'

    def _by_scenario_endpoint(self, scenario_id: str) -> str:
        return f'{self.endpoint}?scenarioId={scenario_id}'

    def _execution_cancel_endpoint(self, execution_id: str) -> str:
        return f'{self.endpoint}/{execution_id}/cancel'

    def _execution_progress_endpoint(self, execution_id: str) -> str:
        return f'{self.endpoint}/{execution_id}/progress'

    def _execution_metrics_endpoint(self, execution_id: str) -> str:
        return f'{self.endpoint}/{execution_id}/metrics'

    def _execution_metric_endpoint(self, execution_id: str, metric_id: str) -> str:
        return f'{self.endpoint}/{execution_id}/metrics/{metric_id}'


