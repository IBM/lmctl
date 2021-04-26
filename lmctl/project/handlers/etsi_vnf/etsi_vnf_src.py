import lmctl.project.handlers.resource as resource_api

class EtsiVnfSourceHandler(resource_api.ResourceSourceHandler):
    def __init__(self, root_path, source_config):           
        super().__init__(root_path, source_config)

class EtsiVnfSourceCreator(resource_api.ResourceSourceCreator):
    def __init__(self):
        super().__init__()

    def _do_create_source(self, journal, source_request):
        super()._do_create_source(journal, source_request)    
