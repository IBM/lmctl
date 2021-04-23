import lmctl.project.handlers.assembly as assembly_api

class EtsiNsSourceHandler(assembly_api.AssemblySourceHandler):
    def __init__(self, root_path, source_config):        
        super().__init__(root_path, source_config)

class EtsiNsSourceCreator(assembly_api.AssemblySourceCreator):
    def __init__(self):        
        super().__init__()
