import lmctl.project.handlers.resource as resource_api

class EtsiVnfContentHandler(resource_api.ResourceContentHandler):
    def __init__(self, root_path, meta):          
        super().__init__(root_path, meta)
            