from .resource_api_base import ResourceAPIBase, CreateAPIMeta, UpdateAPIMeta, json_response_handler

class ResourceManagersAPI(ResourceAPIBase):
    endpoint = 'api/resource-managers'
    id_attr = 'name'

    # Create/Update requests return an Onboarding Report as the body
    create_meta = CreateAPIMeta(response_handler=json_response_handler)
    update_meta = UpdateAPIMeta(response_handler=json_response_handler)