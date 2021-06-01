ASSEMBLY_PROJECT_TYPE = 'Assembly'
RESOURCE_PROJECT_TYPE = 'Resource'
ETSI_VNF_PROJECT_TYPE = 'ETSI_VNF'
ETSI_NS_PROJECT_TYPE = 'ETSI_NS'
TYPE_PROJECT_TYPE = 'Type'
NS_PROJECT_TYPE = 'NS'
VNF_PROJECT_TYPE = 'VNF'

ANSIBLE_RM_TYPES = ['ansible-rm', 'ansiblerm']
BRENT_RM_TYPES = ['lm', 'brent', 'Brent']
BRENT_2_1_RM_TYPES = ['lm2.1', 'brent2.1', 'Brent2.1']

SUPPORTED_RM_TYPES = []
SUPPORTED_RM_TYPES.extend(ANSIBLE_RM_TYPES)
SUPPORTED_RM_TYPES.extend(BRENT_RM_TYPES)
SUPPORTED_RM_TYPES.extend(BRENT_2_1_RM_TYPES)

SUPPORTED_RM_TYPES_GROUPED = []
SUPPORTED_RM_TYPES_GROUPED.append(ANSIBLE_RM_TYPES)
SUPPORTED_RM_TYPES_GROUPED.append(BRENT_RM_TYPES)
SUPPORTED_RM_TYPES_GROUPED.append(BRENT_2_1_RM_TYPES)


def is_assembly_type(project_type):
    if project_type is None:
        return False
    return project_type.lower() in [ASSEMBLY_PROJECT_TYPE.lower(), NS_PROJECT_TYPE.lower(), VNF_PROJECT_TYPE.lower()]

def is_resource_type(project_type):
    if project_type is None:
        return False
    return project_type.lower() in [RESOURCE_PROJECT_TYPE.lower()]

def is_type_project_type(project_type):
    if project_type is None:
        return False
    return project_type.lower() in [TYPE_PROJECT_TYPE.lower()]

def is_etsi_vnf_type(project_type):
    if project_type is None:
        return False
    return project_type.lower() in [ETSI_VNF_PROJECT_TYPE.lower()]

def is_etsi_ns_type(project_type):
    if project_type is None:
        return False
    return project_type.lower() in [ETSI_NS_PROJECT_TYPE.lower()]