from typing import List
from .resource_api_base import ResourceAPIBase, json_response_handler

class BehaviourScenariosAPI(ResourceAPIBase):
    endpoint = 'api/behaviour/scenarios'

    enabled_list_api = False
    
    def _by_project_endpoint(self, project_id: str) -> str:
        return f'{self.endpoint}?projectId={project_id}'

    def all_in_project(self, project_id: str) -> List:
        endpoint = self._by_project_endpoint(project_id)
        response = self.base_client.make_request(method='GET', endpoint=endpoint)
        return json_response_handler(response)
