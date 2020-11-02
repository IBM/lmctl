import os
from tests.common.project_testing import (ProjectSimTestCase,
                                          PROJECT_CONTAINS_DIR,
                                          ARM_DESCRIPTOR_DIR, ARM_LIFECYCLE_DIR, ARM_METAINF_DIR, ARM_MANIFEST_FILE)
from lmctl.project.source.core import Project, Options, ValidateOptions, BuildOptions
from lmctl.project.validation import ValidationResult
import tests.common.simulations.project_lab as project_lab


class TestValidateAnsibleRmProjects(ProjectSimTestCase):

    def test_validate_resource(self):
        project_sim = self.simlab.simulate_arm_basic()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.has_errors())
        self.assertFalse(result.has_warnings())

    def test_validate_resource_descriptor_name(self):
        project_sim = self.simlab.simulate_invalid_arm_mismatch_descriptor_name()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, ARM_DESCRIPTOR_DIR, 'invalid_mismatch_descriptor_name.yml')
        expected_errors = []
        expected_errors.append(
            'Descriptor [{0}]: name \'assembly::notvalid::9.7\' includes type \'assembly\' but this should be \'resource\' based on project configuration'.format(descriptor_path))
        expected_errors.append(
            'Descriptor [{0}]: name \'assembly::notvalid::9.7\' includes \'notvalid\' but this should be \'invalid_mismatch_descriptor_name\' based on project configuration'.format(descriptor_path))
        expected_errors.append('Descriptor [{0}]: name \'assembly::notvalid::9.7\' includes version \'9.7\' but this should be \'1.0\' based on project configuration'.format(descriptor_path))
        self.assert_validation_errors(result, *expected_errors)

    def test_validate_resource_without_descriptor(self):
        project_sim = self.simlab.simulate_invalid_arm_no_descriptor()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, ARM_DESCRIPTOR_DIR, 'invalid_no_descriptor.yml')
        self.assert_validation_errors(result, 'No descriptor found at: {0}'.format(descriptor_path))

    def test_validate_resource_without_lifecycle(self):
        project_sim = self.simlab.simulate_invalid_arm_no_lifecycle()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        lifecycle_path = os.path.join(project_sim.path, ARM_LIFECYCLE_DIR)
        self.assert_validation_errors(result, 'No lifecycle sources found at: {0}'.format(lifecycle_path))

    def test_validate_resource_without_manifest(self):
        project_sim = self.simlab.simulate_invalid_arm_no_manifest()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        manifest_path = os.path.join(project_sim.path, ARM_METAINF_DIR, ARM_MANIFEST_FILE)
        self.assert_validation_errors(result, 'No manifest found at: {0}'.format(manifest_path))


class TestValidateAnsibleRmSubprojects(ProjectSimTestCase):

    def test_validate_resource_subproject(self):
        project_sim = self.simlab.simulate_assembly_contains_arm_basic()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.has_errors())
        self.assertFalse(result.has_warnings())

    def test_validate_resource_descriptor_name(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_arm_mismatch_descriptor_name()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ARM_MISMATCH_DESCRIPTOR_NAME,
                                       ARM_DESCRIPTOR_DIR, 'sub_invalid_mismatch_descriptor_name.yml')
        expected_errors = []
        expected_errors.append(
            'Descriptor [{0}]: name \'assembly::notvalid::9.7\' includes type \'assembly\' but this should be \'resource\' based on project configuration'.format(descriptor_path))
        expected_errors.append(
            'Descriptor [{0}]: name \'assembly::notvalid::9.7\' includes \'notvalid\' but this should be \'sub_invalid_mismatch_descriptor_name-contains_invalid_mismatch_descriptor_name\' based on project configuration'.format(descriptor_path))
        expected_errors.append('Descriptor [{0}]: name \'assembly::notvalid::9.7\' includes version \'9.7\' but this should be \'1.0\' based on project configuration'.format(descriptor_path))
        self.assert_validation_errors(result, *expected_errors)

    def test_validate_subproject_without_descriptor(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_arm_no_descriptor()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ARM_NO_DESCRIPTOR, ARM_DESCRIPTOR_DIR, 'sub_invalid_no_descriptor.yml')
        self.assert_validation_errors(result, 'No descriptor found at: {0}'.format(descriptor_path))

    def test_validate_subproject_without_lifecycle(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_arm_no_lifecycle()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        lifecycle_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ARM_NO_LIFECYCLE, ARM_LIFECYCLE_DIR)
        self.assert_validation_errors(result, 'No lifecycle sources found at: {0}'.format(lifecycle_path))

    def test_validate_subproject_without_manifest(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_arm_no_manifest()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        manifest_path = os.path.join(project_sim.path,  PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ARM_NO_MANIFEST, ARM_METAINF_DIR, ARM_MANIFEST_FILE)
        self.assert_validation_errors(result, 'No manifest found at: {0}'.format(manifest_path))
