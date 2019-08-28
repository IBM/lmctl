ASSEMBLY_PROJECT_TYPE = 'Assembly'
RESOURCE_PROJECT_TYPE = 'Resource'
NS_PROJECT_TYPE = 'NS'
VNF_PROJECT_TYPE = 'VNF'

ANSIBLE_RM_TYPES = ['ansible-rm', 'ansiblerm']
BRENT_RM_TYPES = ['lm', 'brent', 'Brent']

SUPPORTED_RM_TYPES = []
SUPPORTED_RM_TYPES.extend(ANSIBLE_RM_TYPES)
SUPPORTED_RM_TYPES.extend(BRENT_RM_TYPES)

SUPPORTED_RM_TYPES_GROUPED = []
SUPPORTED_RM_TYPES_GROUPED.append(ANSIBLE_RM_TYPES)
SUPPORTED_RM_TYPES_GROUPED.append(BRENT_RM_TYPES)


def is_assembly_type(project_type):
    if project_type is None:
        return False
    return project_type.lower() in [ASSEMBLY_PROJECT_TYPE.lower(), NS_PROJECT_TYPE.lower(), VNF_PROJECT_TYPE.lower()]

def is_resource_type(project_type):
    if project_type is None:
        return False
    return project_type.lower() in [RESOURCE_PROJECT_TYPE.lower()]
