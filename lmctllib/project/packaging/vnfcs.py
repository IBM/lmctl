from .ansiblerm import AnsibleRmPackageManager

def getPackageManager(packaging_type, package_id, package_def):
    if packaging_type == 'ansible-rm':
        return AnsibleRmPackageManager(package_id, package_def)
    else:
        return None