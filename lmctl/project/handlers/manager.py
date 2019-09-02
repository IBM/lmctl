import lmctl.project.handlers.assembly as assembly_handlers
import lmctl.project.handlers.resource as resource_handlers

def source_creator_for(source_config):
    if source_config.is_assembly_project():
        return assembly_handlers.source_creator
    else:
        return resource_handlers.source_creator

def source_handler_for(source_config):
    if source_config.is_assembly_project():
        return assembly_handlers.source_handler
    else:
        return resource_handlers.source_handler

def content_handler_for(content_meta):
    if content_meta.is_assembly_content():
        return assembly_handlers.content_handler
    else:
        return resource_handlers.content_handler

