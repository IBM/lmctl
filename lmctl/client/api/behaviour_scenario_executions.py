from typing import List, Dict
from lmctl.client.client_request import TNCOClientRequest
from .tnco_api_base import TNCOAPI
class BehaviourScenarioExecutionsAPI(TNCOAPI):
    endpoint = 'api/behaviour/executions'

    def get(self, id: str, include_scenario: bool = None) -> Dict:
        query_params = {}
        if include_scenario is not None:
            query_params['includeScenario'] = include_scenario
        return self._get(id_value=id, query_params=query_params)

    def delete(self, id: str):
        self._delete(id_value=id)
    
    def execute(self, execution_request: Dict = None, scenario_id: str = None) -> str:
        if execution_request is None and scenario_id is None:
            raise ValueError('Must set either "execution_request" or "scenario_id" argument - both were None')
        elif execution_request is None:
            execution_request = {}
        if scenario_id is not None:
            execution_request['scenarioId'] = scenario_id
        request = TNCOClientRequest(method='POST', endpoint=self.endpoint).add_json_body(execution_request)
        return self._exec_request_and_get_location_header(request)
    
    def cancel(self, execution_id: str):
        endpoint = self._execution_cancel_endpoint(execution_id)
        request = TNCOClientRequest.build_request_for_json(method='POST', endpoint=endpoint)
        return self._exec_request_and_parse_json(request)
    
    def all_in_project(self, project_id: str, include_scenario: bool = None) -> List:
        query_params = {'projectId': project_id}
        if include_scenario is not None:
            query_params['includeScenario'] = include_scenario
        return self._get_json(
            endpoint=self.endpoint, 
            query_params=query_params
        )

    def all_of_scenario(self, scenario_id: str, include_scenario: bool = None) -> List:
        query_params = {'scenarioId': scenario_id}
        if include_scenario is not None:
            query_params['includeScenario'] = include_scenario
        return self._get_json(
            endpoint=self.endpoint, 
            query_params=query_params
        )

    def get_progress(self, execution_id: str) -> Dict:
        endpoint = self._execution_progress_endpoint(execution_id)
        return self._get_json(endpoint=endpoint)

    def get_metrics(self, execution_id: str) -> List:
        endpoint = self._execution_metrics_endpoint(execution_id)
        return self._get_json(endpoint=endpoint)

    def get_metric(self, execution_id: str, metric_id: str) -> Dict:
        endpoint = self._execution_metric_endpoint(execution_id, metric_id)
        return self._get_json(endpoint=endpoint)

    def _execution_cancel_endpoint(self, execution_id: str) -> str:
        return f'{self.endpoint}/{execution_id}/cancel'

    def _execution_progress_endpoint(self, execution_id: str) -> str:
        return f'{self.endpoint}/{execution_id}/progress'

    def _execution_metrics_endpoint(self, execution_id: str) -> str:
        return f'{self.endpoint}/{execution_id}/metrics'

    def _execution_metric_endpoint(self, execution_id: str, metric_id: str) -> str:
        return f'{self.endpoint}/{execution_id}/metrics/{metric_id}'


