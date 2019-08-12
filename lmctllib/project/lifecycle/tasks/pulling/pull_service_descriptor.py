import os
import oyaml as yaml
import shutil
import lmctllib.utils.descriptors as descriptor_utils
import lmctllib.drivers.exception as driver_exceptions
from ..tasks import ProjectLifecycleTask

class PullServiceDescriptor(ProjectLifecycleTask):
    """
    Pulls the Assembly Descriptor for this Project from a target LM environment, overwriting the existing local version
    """
    def __init__(self):
        super().__init__("Pull Service Descriptor Sources")

    def execute_work(self, tools, products):
        service_descriptor_path = self._get_project_tree().serviceDescriptor().descriptorFile()
        if os.path.exists(service_descriptor_path):
            descriptor_name = self.__backupExisting()
        else:
            return self._return_skipped('No Service descriptor found at: {0}'.format(service_descriptor_path))
        self.__pull(descriptor_name)
        return self._return_passed()

    def __pull(self, descriptor_name):
        env = self._get_environment()
        lm_env = env.lm
        descriptor_driver = lm_env.getDescriptorDriver()
        journal = self._get_journal()
        journal.add_text('Pulling descriptor {0} from LM ({1})'.format(descriptor_name, lm_env.getUrl()))
        try:
            raw_descriptor = descriptor_driver.getDescriptor(descriptor_name)
            descriptor_content = descriptor_utils.DescriptorReader.strToDictionary(raw_descriptor)
        except driver_exceptions.NotFoundException:
            return self._return_failure('Descriptor {0} not found'.format(descriptor_name))
        service_descriptor_path = self._get_project_tree().serviceDescriptor().descriptorFile()
        journal.add_text('Saving descriptor to {0}'.format(service_descriptor_path))
        with open(service_descriptor_path, 'w') as descriptor_file:
            yaml.dump(descriptor_content, descriptor_file, default_flow_style=False)

    def __backupExisting(self):
        backup_dir = self._get_project_tree().backup().serviceDescriptor().directory()
        backup_descriptor_path = self._get_project_tree().backup().serviceDescriptor().descriptorFile()
        service_descriptor_path = self._get_project_tree().serviceDescriptor().descriptorFile()
        self._get_journal().add_text('Service descriptor found at {0}, copying to {1}'.format(service_descriptor_path, backup_dir))
        if not os.path.exists(backup_dir):
            self._get_journal().add_text('Creating directory: {0}'.format(backup_dir))
            os.makedirs(backup_dir)
        shutil.copy2(service_descriptor_path, backup_descriptor_path)
        raw_descriptor = descriptor_utils.DescriptorReader.readStr(service_descriptor_path)
        descritor_content = descriptor_utils.DescriptorReader.strToDictionary(raw_descriptor)
        descriptor = descriptor_utils.DescriptorModel(descritor_content)
        descriptor_name = descriptor.getName()
        return descriptor_name
