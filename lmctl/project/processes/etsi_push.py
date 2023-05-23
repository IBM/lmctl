import lmctl.project.handlers.interface as handlers_api
import lmctl.project.handlers.etsi_ns as etsi_ns_handler_api
import lmctl.project.handlers.etsi_vnf as etsi_vnf_handler_api
import lmctl.utils.descriptors as descriptors
import lmctl.drivers.lm.base as lm_drivers

class EtsiPushProcessError(Exception):
    pass

class EtsiPushProcess:

    def __init__(self, pkg, pkg_meta, journal, env_sessions, push_workspace):
        self.pkg = pkg
        self.pkg_meta = pkg_meta
        self.journal = journal
        self.env_sessions = env_sessions
        self.push_workspace = push_workspace        

    def execute(self):
        self.journal.event('Pushing ETSI Package Content')
        lm_session = self.env_sessions.lm
        pkg_driver = lm_session.pkg_mgmt_driver
        if (self.pkg_meta.is_etsi_ns_content()):
            # Need to get the descriptor to determin the full ID (descriptor_name) as namein the pkg_meta is not full
            descriptor_path = etsi_ns_handler_api.EtsiNsPkgContentTree(self.push_workspace).descriptor_definitions_file_path
            descriptor, descriptor_yml_str = descriptors.DescriptorParser().read_from_file_with_raw(descriptor_path)
            descriptor_name = descriptor.get_name()            
            self.journal.event('Removing any existing ETSI_NS assembly package named {0} (version: {1}) from TNC-O: {2} ({3})'
                .format(descriptor_name, self.pkg_meta.version, lm_session.env.name, lm_session.env.address))
            try:
                pkg_driver.delete_nsd_package(descriptor_name)
            except lm_drivers.NotFoundException:
                self.journal.event('No package named {0} found'.format(descriptor_name))            
            pkg_driver.onboard_nsd_package(descriptor_name, self.pkg.path)
        elif (self.pkg_meta.is_etsi_vnf_content()):
            descriptor_path = etsi_vnf_handler_api.EtsiVnfPkgContentTree(self.push_workspace).definitions_descriptor_file_path
            descriptor, descriptor_yml_str = descriptors.DescriptorParser().read_from_file_with_raw(descriptor_path)
            descriptor_name = descriptor.get_name()
            self.journal.event('Removing any existing ETSI_NS assembly package named {0} (version: {1}) from TNC-O: {2} ({3})'
                .format(descriptor_name, self.pkg_meta.version, lm_session.env.name, lm_session.env.address))
            try:
                pkg_driver.delete_package(descriptor_name)
            except lm_drivers.NotFoundException:
                self.journal.event('No package named {0} found'.format(descriptor_name))
            pkg_driver.onboard_package(descriptor_name, self.pkg.path)
        else:
            raise EtsiPushProcessError('Not an ETSI package, Not pushing.')
