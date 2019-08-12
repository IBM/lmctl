import os
import lmctllib.utils.descriptors as descriptor_utils
import lmctllib.drivers.exception as driver_exceptions
from ..tasks import ProjectLifecycleTask

class DeployServiceDescriptor(ProjectLifecycleTask):
    """
    Pushes the Assembly Descriptor from the push workspace to a target LM environment
    """
    def __init__(self):
        super().__init__("Deploy Service Descriptor")
    
    def execute_work(self, tools, products):
        journal = self._get_journal()
        env = self._get_environment()
        lm_env = env.lm
        target_descriptor_path = self._get_project_tree().pushWorkspace().content().serviceDescriptor().descriptorFile()
        if os.path.exists(target_descriptor_path):
            journal.add_text('Service descriptor found at {0}, pushing to LM ({1})'.format(target_descriptor_path, lm_env.getUrl()))
            raw_descriptor = descriptor_utils.DescriptorReader.readStr(target_descriptor_path)
            descriptor_content = descriptor_utils.DescriptorReader.strToDictionary(raw_descriptor)
            descriptor = descriptor_utils.DescriptorModel(descriptor_content)
            descriptor_name = descriptor.getName()
            descriptor_driver = lm_env.getDescriptorDriver()
            journal.add_text('Checking for Descriptor {0} in LM ({1})'.format(descriptor_name, lm_env.getUrl()))
            found = True
            try:
                descriptor_driver.getDescriptor(descriptor_name)
            except driver_exceptions.NotFoundException:
                found = False

            if found:
                journal.add_text('Descriptor {0} already exists, updating'.format(descriptor_name))
                descriptor_driver.updateDescriptor(descriptor_name, raw_descriptor)
            else:
                journal.add_text('Not found, creating Descriptor {0}'.format(descriptor_name))
                descriptor_driver.createDescriptor(raw_descriptor)
            return self._return_passed()
        else:
            return self._return_failure('No service descriptor was found at {0}'.format(target_descriptor_path))