import lmctl.project.handlers.assembly as assembly_handlers
import lmctl.project.handlers.etsi_ns as etsi_ns_handlers
import lmctl.project.handlers.etsi_vnf as etsi_vnf_handlers
import lmctl.project.handlers.resource as resource_handlers
import lmctl.project.handlers.types as type_handlers

def source_creator_for(source_config):
    if source_config.is_assembly_project():
        return assembly_handlers.source_creator
    elif source_config.is_type_project():
        return type_handlers.source_creator
    elif source_config.is_etsi_ns_project():
        return etsi_ns_handlers.source_creator        
    elif source_config.is_etsi_vnf_project():
        return etsi_vnf_handlers.source_creator
    else:
        return resource_handlers.source_creator

def source_handler_for(source_config):
    if source_config.is_assembly_project():
        return assembly_handlers.source_handler
    elif source_config.is_type_project():
        return type_handlers.source_handler
    elif source_config.is_etsi_ns_project():
        return etsi_ns_handlers.source_handler        
    elif source_config.is_etsi_vnf_project():        
        return etsi_vnf_handlers.source_handler        
    else:
        return resource_handlers.source_handler

def content_handler_for(content_meta):
    if content_meta.is_assembly_content():
        return assembly_handlers.content_handler
    elif content_meta.is_type_content():
        return type_handlers.content_handler
    elif content_meta.is_etsi_vnf_content():
        return etsi_vnf_handlers.content_handler
    elif content_meta.is_etsi_ns_content():
        return etsi_ns_handlers.content_handler        
    else:
        return resource_handlers.content_handler

