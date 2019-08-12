import zipfile
import os
import logging
import shutil
import lmctllib.drivers.exception as driver_exceptions
import lmctllib.project.model as project_model 
import lmctllib.utils.descriptors as descriptor_utils 
from .exception import PackageManagerException

ENV_SELECTOR_ARM_NAME = "ARM_NAME"

class AnsibleRmPackageManager:
    """
    Handles packaging and deploying VNFCs to an Ansible RM
    """
    def __init__(self, id, definition):
        self.id=id
        self.definition=definition

    def package(self, journal, package_execution: project_model.VnfcPackageExecution, vnfc_def: project_model.VnfcDefinition, source_dir: str, pkg_dir: str):
        """Package the given Vnfc defintion into a Csar"""
        return CsarBuilder(self.id, journal, source_dir, pkg_dir, vnfc_def).package(package_execution)

    def select_deploy_environment(self, environment, environment_selectors):
        if ENV_SELECTOR_ARM_NAME not in environment_selectors:
            raise PackageManagerException('ArmName must be provided to use this package type')
        arm_name = environment_selectors[ENV_SELECTOR_ARM_NAME]
        return {'arm': environment.getArm(arm_name), 'lm': environment.lm} 

    def deploy(self, journal, deployment_environment, package_execution: project_model.VnfcPackageExecution, vnfc_def: project_model.VnfcDefinition, pkg_dir: str):
        """Deploy a previously package Vnfc Csar to the Ansible RM"""
        return CsarDeployer(self.id, journal, pkg_dir, vnfc_def).deploy(deployment_environment, package_execution)

    def post_deploy(self, journal, deployment_environment):
        """Re-onboards the Ansible RM in the target LM environment so it is aware of new VNFCs deployed"""
        arm_env = deployment_environment['arm']
        lm_env = deployment_environment['lm']
        onboarding_driver = lm_env.getOnboardRmDriver()
        arm_onboarding_addr = '{0}/api/v1.0/resource-manager'.format(arm_env.getOnboardingUrl())
        journal.add_text('Refreshing LM ({0}) view of ansible-rm known as {1} with url {2}'.format(lm_env.getUrl(), arm_env.name, arm_onboarding_addr))
        onboarding_driver.updateRm(arm_env.name, arm_onboarding_addr)

class CsarDeployer:
    """
    Handles deployment of VNFC Csars
    """
    def __init__(self, id, journal, pkg_dir: str, vnfc_def: project_model.VnfcDefinition):
        self.id=id
        self.journal=journal
        self.pkg_dir=pkg_dir
        self.vnfc_def=vnfc_def

    def deploy(self, deployment_environment, package_execution):
        arm_env = deployment_environment['arm']
        driver = arm_env.getArmDriver()
        vnfc_identifier = self.vnfc_def.identifier
        descriptor_path = os.path.join(self.pkg_dir, '{0}.yml'.format(vnfc_identifier))
        descriptor_version = '0'
        if os.path.exists(descriptor_path):
            descriptor_content = descriptor_utils.DescriptorReader.readDictionary(descriptor_path)
            descriptor = descriptor_utils.DescriptorModel(descriptor_content)
            descriptor_name = descriptor.getName()
            descriptor_version = descriptor.getVersion()
            lm_env = deployment_environment['lm']
            self.journal.add_text('Removing descriptor {0} from LM ({1})'.format(descriptor_name, lm_env.getUrl()))
            descriptor_driver = lm_env.getDescriptorDriver()
            try:
                descriptor_driver.deleteDescriptor(descriptor_name)
            except driver_exceptions.NotFoundException:
                self.journal.add_text('Descriptor {0} not found'.format(descriptor_name))
        else:
            raise PackageManagerException('Could not find Resource Descriptor for VNFC {0} at {1}'.format(vnfc_identifier, descriptor_path))
        target_csar_file = os.path.join(self.pkg_dir, vnfc_identifier + '.csar')
        if os.path.exists(target_csar_file):
            self.journal.add_text('Pushing {0} (version: {1}) csar to ansible-rm: {2} ({3})'.format(vnfc_identifier, descriptor_version, arm_env.name, arm_env.getUrl()))
            driver.onboardType(vnfc_identifier, descriptor_version, target_csar_file)
            ##TODO error handling
        else:
            raise PackageManagerException('Could not find CSAR for VNFC {0} at {1}'.format(vnfc_identifier, target_csar_file))

class CsarBuilder:

    def __init__(self, id, journal, source_dir: str, pkg_dir: str, vnfc_def: project_model.VnfcDefinition):
        self.id=id
        self.journal=journal
        self.source_dir=source_dir
        self.pkg_dir=pkg_dir
        self.vnfc_def=vnfc_def

    def package(self, package_execution):
        vnfc_identifier = self.vnfc_def.identifier
        target_csar_file = os.path.join(self.pkg_dir, vnfc_identifier + '.csar')
        self.journal.add_text("Creating CSAR for VNFC {0}: {1}".format(vnfc_identifier, target_csar_file))
        with zipfile.ZipFile(target_csar_file, "w") as csar:
            included_items = [
                {'path': os.path.join(self.source_dir, 'lifecycle'), 'alias': 'lifecycle', 'required': True},
                {'path': os.path.join(self.source_dir, 'descriptor'), 'alias': 'descriptor', 'required': True},
                {'path': os.path.join(self.source_dir, 'tests'), 'alias': 'tests', 'required': False},
                {'path': os.path.join(self.source_dir, 'Meta-Inf'), 'alias': 'Meta-Inf', 'required': True}
            ]
            for included_item in included_items:
                self.__addDirectoryIfExists(csar, included_item)
        descriptor_path = os.path.join(self.source_dir, 'descriptor', '{0}.yml'.format(vnfc_identifier))
        target_descriptor_path = os.path.join(self.pkg_dir, '{0}.yml'.format(vnfc_identifier))
        if os.path.exists(descriptor_path):
            shutil.copy2(descriptor_path, target_descriptor_path)
        else:
            raise PackageManagerException("Required descriptor for VNFC CSAR not found: {0}".format(descriptor_path))

    def __addDirectoryIfExists(self, csar, included_item):
        path = included_item['path']
        if os.path.exists(path):
            self.journal.add_text("Adding directory to CSAR: {0}".format(path))
            csar.write(path, arcname=included_item['alias'])
            rootlen = len(path) + 1
            for root, dirs, files in os.walk(path):
              for filename in files:
                full_path = os.path.join(root, filename)
                csar.write(full_path, arcname=os.path.join(included_item['alias'], full_path[rootlen:]))
        else:
            if included_item['required']:
                raise PackageManagerException("Required directory for VNFC CSAR not found: {0}".format(path))
            else:
                self.journal.add_text("Skipping directory for VNFC CSAR as it was not found: {0}".format(path))
