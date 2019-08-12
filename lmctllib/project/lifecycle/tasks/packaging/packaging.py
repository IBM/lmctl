import os
import lmctllib.utils.descriptors as descriptor_utils

def establishPackageVersion(descriptor_file):
    if os.path.exists(descriptor_file):
        raw_descriptor = descriptor_utils.DescriptorReader.readStr(descriptor_file)
        descriptor_content = descriptor_utils.DescriptorReader.strToDictionary(raw_descriptor)
        descriptor = descriptor_utils.DescriptorModel(descriptor_content)
        descriptor_version = descriptor.getVersion()
    else:
        descriptor_version = "0.0.0"
    return descriptor_version

def establishBuiltPackageName(project_name, project_tree):
    pkg_version = establishPackageVersion(project_tree.build().packaging().serviceDescriptor().descriptorFile())
    pkg_name = '{0}-{1}'.format(project_name, pkg_version)
    return pkg_name

