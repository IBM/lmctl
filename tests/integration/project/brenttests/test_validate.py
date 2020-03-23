import os
from tests.common.project_testing import (ProjectSimTestCase,
                                          PROJECT_CONTAINS_DIR, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR, BRENT_DESCRIPTOR_YML_FILE, 
                                          BRENT_INFRASTRUCTURE_DIR, BRENT_INFRASTRUCTURE_MANIFEST_FILE, BRENT_LIFECYCLE_DIR, BRENT_LIFECYCLE_MANIFEST_FILE)
from lmctl.project.source.core import Project, Options, ValidateOptions, BuildOptions
from lmctl.project.validation import ValidationResult
import tests.common.simulations.project_lab as project_lab

EXPECTED_AUTOCORRECT_DESCRIPTOR = '''\
description: descriptor
infrastructure:
  Openstack:
    template:
      file: example.yaml
      template-type: HEAT
  Kubernetes:
    template:
      file: k8s.yaml
  AWS:
    template:
      file: aws.yaml
lifecycle:
  Create: {}
  Install: {}
  Delete: {}
default-driver:
  ansible:
    infrastructure-type:
    - Openstack
    - Kubernetes
  shell:
    infrastructure-type:
    - AWS
'''

class TestValidateBrentProjects(ProjectSimTestCase):

    def test_validate_resource(self):
        project_sim = self.simlab.simulate_brent_basic()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.has_errors())
        self.assertFalse(result.has_warnings())

    def test_validate_resource_descriptor_name(self):
        project_sim = self.simlab.simulate_invalid_brent_mismatch_descriptor_name()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR, BRENT_DESCRIPTOR_YML_FILE)
        expected_errors = []
        expected_errors.append(
            'Descriptor [{0}]: name \'assembly::notvalid::5.4\' includes type \'assembly\' but this should be \'resource\' based on project configuration'.format(descriptor_path))
        expected_errors.append(
            'Descriptor [{0}]: name \'assembly::notvalid::5.4\' includes \'notvalid\' but this should be \'invalid_mismatch_lm_descriptor_name\' based on project configuration'.format(descriptor_path))
        expected_errors.append('Descriptor [{0}]: name \'assembly::notvalid::5.4\' includes version \'5.4\' but this should be \'1.0\' based on project configuration'.format(descriptor_path))
        self.assert_validation_errors(result, *expected_errors)

    def test_validate_resource_without_definitions(self):
        project_sim = self.simlab.simulate_invalid_brent_no_definitions()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR, BRENT_DESCRIPTOR_YML_FILE)
        self.assert_validation_errors(result, 'No descriptor found at: {0}'.format(descriptor_path))

    def test_validate_resource_without_infrastructure(self):
        project_sim = self.simlab.simulate_invalid_brent_no_infrastructure()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        inf_path = os.path.join(project_sim.path, BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
        self.assert_validation_errors(result, 'No Infrastructure definitions directory found at: {0}'.format(inf_path))

    def test_validate_resource_without_lm_definitions(self):
        project_sim = self.simlab.simulate_invalid_brent_no_lm_definitions()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR, BRENT_DESCRIPTOR_YML_FILE)
        self.assert_validation_errors(result, 'No descriptor found at: {0}'.format(descriptor_path))

    def test_validate_resource_without_lm_descriptor(self):
        project_sim = self.simlab.simulate_invalid_brent_no_lm_descriptor()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR, BRENT_DESCRIPTOR_YML_FILE)
        self.assert_validation_errors(result, 'No descriptor found at: {0}'.format(descriptor_path))

    def test_validate_resource_without_lifecycle(self):
        project_sim = self.simlab.simulate_invalid_brent_no_lifecycle()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        lifecycle_path = os.path.join(project_sim.path, BRENT_LIFECYCLE_DIR)
        self.assert_validation_errors(result, 'No Lifecycle directory found at: {0}'.format(lifecycle_path))

    def test_validate_errors_on_manifests(self):
        project_sim = self.simlab.simulate_brent_with_prealpha_style()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        inf_manifest_path = os.path.join(project_sim.path, BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR, BRENT_INFRASTRUCTURE_MANIFEST_FILE)
        lifeycle_manifest_path = os.path.join(project_sim.path, BRENT_LIFECYCLE_DIR, BRENT_LIFECYCLE_MANIFEST_FILE)
        self.assert_validation_errors(result, 'Found infrastructure manifest [{0}]: this file is no longer supported by the Brent Resource Manager. Add this information to the Resource descriptor instead or enable the autocorrect option'.format(inf_manifest_path), 'Found lifecycle manifest [{0}]: this file is no longer supported by the Brent Resource Manager. Add this information to the Resource descriptor instead or enable the autocorrect option'.format(lifeycle_manifest_path))

    def test_validate_allow_autocorrect_fixes_manifests(self):
        project_sim = self.simlab.simulate_brent_with_prealpha_style()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        validate_options.allow_autocorrect = True
        result = project.validate(validate_options)
        self.assertFalse(result.has_errors())
        self.assertFalse(result.has_warnings())
        project = Project(project_sim.path)
        tester = self.assert_project(project)
        inf_manifest_path = os.path.join(project_sim.path, BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR, BRENT_INFRASTRUCTURE_MANIFEST_FILE)
        tester.assert_has_no_file(inf_manifest_path)
        lifeycle_manifest_path = os.path.join(project_sim.path, BRENT_LIFECYCLE_DIR, BRENT_LIFECYCLE_MANIFEST_FILE)
        tester.assert_has_no_file(lifeycle_manifest_path)
        lm_dir = os.path.join(BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR)
        descriptor_path = os.path.join(lm_dir, BRENT_DESCRIPTOR_YML_FILE)
        tester.assert_has_file(descriptor_path, EXPECTED_AUTOCORRECT_DESCRIPTOR)

class TestValidateBrentSubprojects(ProjectSimTestCase):

    def test_validate_resource(self):
        project_sim = self.simlab.simulate_assembly_contains_brent_basic()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.has_errors())
        self.assertFalse(result.has_warnings())

    def test_validate_resource_descriptor_name(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_brent_mismatch_descriptor_name()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_BRENT_MISMATCH_DESCRIPTOR_NAME, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR, BRENT_DESCRIPTOR_YML_FILE)
        expected_errors = []
        expected_errors.append(
            'Descriptor [{0}]: name \'assembly::notvalid::5.4\' includes type \'assembly\' but this should be \'resource\' based on project configuration'.format(descriptor_path))
        expected_errors.append(
            'Descriptor [{0}]: name \'assembly::notvalid::5.4\' includes \'notvalid\' but this should be \'sub_invalid_mismatch_descriptor_name-contains_invalid_mismatch_descriptor_name\' based on project configuration'.format(descriptor_path))
        expected_errors.append('Descriptor [{0}]: name \'assembly::notvalid::5.4\' includes version \'5.4\' but this should be \'1.0\' based on project configuration'.format(descriptor_path))
        self.assert_validation_errors(result, *expected_errors)

    def test_validate_resource_without_definitions(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_brent_no_definitions()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_BRENT_NO_DEFINITIONS, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR, BRENT_DESCRIPTOR_YML_FILE)
        self.assert_validation_errors(result, 'No descriptor found at: {0}'.format(descriptor_path))


    def test_validate_resource_without_infrastructure(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_brent_no_infrastructure()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        inf_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_BRENT_NO_INFRASTRUCTURE, BRENT_DEFINITIONS_DIR, BRENT_INFRASTRUCTURE_DIR)
        self.assert_validation_errors(result, 'No Infrastructure definitions directory found at: {0}'.format(inf_path))

    def test_validate_resource_without_lm_definitions(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_brent_no_lm_definitions()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_BRENT_NO_LM_DEFINITIONS, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR, BRENT_DESCRIPTOR_YML_FILE)
        self.assert_validation_errors(result, 'No descriptor found at: {0}'.format(descriptor_path))

    def test_validate_resource_without_lm_descriptor(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_brent_no_lm_descriptor()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_BRENT_NO_DESCRIPTOR, BRENT_DEFINITIONS_DIR, BRENT_DESCRIPTOR_DIR, BRENT_DESCRIPTOR_YML_FILE)
        self.assert_validation_errors(result, 'No descriptor found at: {0}'.format(descriptor_path))

    def test_validate_resource_without_lifecycle(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_brent_no_lifecycle()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        inf_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_BRENT_NO_LIFECYCLE, BRENT_LIFECYCLE_DIR)
        self.assert_validation_errors(result, 'No Lifecycle directory found at: {0}'.format(inf_path))
