import lmctl.project.handlers.assembly as assembly_api

class EtsiNsContentHandler(assembly_api.AssemblyContentHandler):
    def __init__(self, root_path, meta):
        super().__init__(root_path, meta)
            