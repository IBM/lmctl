import os
from tests.common.project_testing import (ProjectSimTestCase,
                                          PROJECT_CONTAINS_DIR,
                                          ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE, ASSEMBLY_DESCRIPTOR_YAML_FILE,
                                          ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, ASSEMBLY_RUNTIME_DIR, ASSEMBLY_TESTS_DIR)
from lmctl.project.source.core import Project, BuildValidationError, ValidateOptions, BuildOptions
from lmctl.project.validation import ValidationResult
import tests.common.simulations.project_lab as project_lab

class TestValidateAssemblyProjects(ProjectSimTestCase):

    def test_validate_assembly(self):
        project_sim = self.simlab.simulate_assembly_basic()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.has_errors())
        self.assertFalse(result.has_warnings())

    def test_validate_assembly_without_descriptor_file(self):
        project_sim = self.simlab.simulate_invalid_assembly_no_descriptor()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE)
        self.assert_validation_errors(result, 'No descriptor found at: {0}'.format(descriptor_path))

    def test_validate_assembly_descriptor_name(self):
        project_sim = self.simlab.simulate_invalid_assembly_mismatch_descriptor_name()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, ASSEMBLY_DESCRIPTOR_DIR, 'assembly.yml')
        expected_errors = []
        expected_errors.append('Descriptor [{0}]: name \'resource::notvalid::9.7\' includes type \'resource\' but this should be \'assembly\' based on project configuration'.format(descriptor_path))
        expected_errors.append(
            'Descriptor [{0}]: name \'resource::notvalid::9.7\' includes \'notvalid\' but this should be \'invalid_mismatch_descriptor_name\' based on project configuration'.format(descriptor_path))
        expected_errors.append('Descriptor [{0}]: name \'resource::notvalid::9.7\' includes version \'9.7\' but this should be \'1.0\' based on project configuration'.format(descriptor_path))
        self.assert_validation_errors(result, *expected_errors)

    def test_validate_assembly_descriptor_template_name(self):
        project_sim = self.simlab.simulate_invalid_assembly_mismatch_descriptor_template_name()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, ASSEMBLY_DESCRIPTOR_DIR, 'assembly-template.yml')
        expected_errors = []
        expected_errors.append('Descriptor [{0}]: name \'resource::notvalid::9.7\' includes type \'resource\' but this should be \'assembly-template\' based on project configuration'.format(descriptor_path))
        expected_errors.append(
            'Descriptor [{0}]: name \'resource::notvalid::9.7\' includes \'notvalid\' but this should be \'invalid_mismatch_descriptor_template_name\' based on project configuration'.format(descriptor_path))
        expected_errors.append('Descriptor [{0}]: name \'resource::notvalid::9.7\' includes version \'9.7\' but this should be \'1.0\' based on project configuration'.format(descriptor_path))
        self.assert_validation_errors(result, *expected_errors)

    def test_validate_assembly_with_non_json_configuration(self):
        project_sim = self.simlab.simulate_invalid_assembly_non_json_configuration()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        configuration_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'notjson.xml')
        self.assert_validation_errors(result, 'Configuration [{0}]: is not a json file (with a .json extension)'.format(configuration_path))

    def test_validate_assembly_with_non_json_runtime(self):
        project_sim = self.simlab.simulate_invalid_assembly_non_json_runtime()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        runtime_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'notjson.xml')
        self.assert_validation_errors(result, 'Runtime [{0}]: is not a json file (with a .json extension)'.format(runtime_path))

    def test_validate_assembly_with_non_json_test(self):
        project_sim = self.simlab.simulate_invalid_assembly_non_json_test()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        test_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'notjson.xml')
        self.assert_validation_errors(result, 'Test [{0}]: is not a json file (with a .json extension)'.format(test_path))

    def test_validate_assembly_with_invalid_json_configuration(self):
        project_sim = self.simlab.simulate_invalid_assembly_invalid_json_configuration()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        configuration_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'notvalid.json')
        self.assert_validation_errors(result, 'Configuration [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(configuration_path))

    def test_validate_assembly_with_invalid_json_runtime(self):
        project_sim = self.simlab.simulate_invalid_assembly_invalid_json_runtime()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        runtime_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'notvalid.json')
        self.assert_validation_errors(result, 'Runtime [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(runtime_path))

    def test_validate_assembly_with_invalid_json_test(self):
        project_sim = self.simlab.simulate_invalid_assembly_invalid_json_test()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        test_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'notvalid.json')
        self.assert_validation_errors(result, 'Test [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(test_path))


class TestValidateAssemblySubprojects(ProjectSimTestCase):

    def test_validate_assembly_subproject(self):
        project_sim = self.simlab.simulate_assembly_contains_assembly_basic()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        self.assertIsInstance(result, ValidationResult)
        self.assertFalse(result.has_errors())
        self.assertFalse(result.has_warnings())

    def test_validate_assembly_subproject_without_descriptor_file(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_no_descriptor()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_NO_DESCRIPTOR, ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE)
        self.assert_validation_errors(result, 'No descriptor found at: {0}'.format(descriptor_path))

    def test_validate_assembly_subproject_descriptor_name(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_mismatch_descriptor_name()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        descriptor_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_MISMATCH_DESCRIPTOR_NAME, ASSEMBLY_DESCRIPTOR_DIR, 'assembly.yml')
        expected_errors = []
        expected_errors.append('Descriptor [{0}]: name \'resource::notvalid::9.7\' includes type \'resource\' but this should be \'assembly\' based on project configuration'.format(descriptor_path))
        expected_errors.append(
            'Descriptor [{0}]: name \'resource::notvalid::9.7\' includes \'notvalid\' but this should be \'sub_invalid_mismatch_descriptor_name-contains_invalid_mismatch_descriptor_name\' based on project configuration'.format(descriptor_path))
        expected_errors.append('Descriptor [{0}]: name \'resource::notvalid::9.7\' includes version \'9.7\' but this should be \'1.0\' based on project configuration'.format(descriptor_path))
        self.assert_validation_errors(result, *expected_errors)

    def test_validate_assembly_subproject_with_non_json_configuration(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_non_json_configuration()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        configuration_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_NON_JSON_CONFIGURATION,
                                          ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'notjson.xml')
        self.assert_validation_errors(result, 'Configuration [{0}]: is not a json file (with a .json extension)'.format(configuration_path))

    def test_validate_assembly_subproject_with_non_json_runtime(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_non_json_runtime()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        runtime_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_NON_JSON_RUNTIME, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'notjson.xml')
        self.assert_validation_errors(result, 'Runtime [{0}]: is not a json file (with a .json extension)'.format(runtime_path))

    def test_validate_assembly_subproject_with_non_json_test(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_non_json_test()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        test_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_NON_JSON_TEST, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'notjson.xml')
        self.assert_validation_errors(result, 'Test [{0}]: is not a json file (with a .json extension)'.format(test_path))

    def test_validate_assembly_subproject_with_invalid_json_configuration(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_invalid_json_configuration()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        configuration_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_INVALID_JSON_CONFIGURATION,
                                          ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'notvalid.json')
        self.assert_validation_errors(result, 'Configuration [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(configuration_path))

    def test_validate_assembly_subproject_with_invalid_json_runtime(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_invalid_json_runtime()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        runtime_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_INVALID_JSON_RUNTIME,
                                    ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'notvalid.json')
        self.assert_validation_errors(result, 'Runtime [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(runtime_path))

    def test_validate_assembly_subproject_with_invalid_json_test(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_invalid_json_test()
        project = Project(project_sim.path)
        validate_options = ValidateOptions()
        result = project.validate(validate_options)
        test_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_INVALID_JSON_TEST, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'notvalid.json')
        self.assert_validation_errors(result, 'Test [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(test_path))


class TestBuildValidateAssemblyProjects(ProjectSimTestCase):

    def test_build_validate_assembly_without_descriptor_file(self):
        project_sim = self.simlab.simulate_invalid_assembly_no_descriptor()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        descriptor_path = os.path.join(project_sim.path, ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE)
        self.assert_validation_errors(context.exception.validation_result, 'No descriptor found at: {0}'.format(descriptor_path))

    def test_build_validate_assembly_descriptor_name(self):
        project_sim = self.simlab.simulate_invalid_assembly_mismatch_descriptor_name()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        descriptor_path = os.path.join(project_sim.path, ASSEMBLY_DESCRIPTOR_DIR, 'assembly.yml')
        expected_errors = []
        expected_errors.append('Descriptor [{0}]: name \'resource::notvalid::9.7\' includes type \'resource\' but this should be \'assembly\' based on project configuration'.format(descriptor_path))
        expected_errors.append(
            'Descriptor [{0}]: name \'resource::notvalid::9.7\' includes \'notvalid\' but this should be \'invalid_mismatch_descriptor_name\' based on project configuration'.format(descriptor_path))
        expected_errors.append('Descriptor [{0}]: name \'resource::notvalid::9.7\' includes version \'9.7\' but this should be \'1.0\' based on project configuration'.format(descriptor_path))
        self.assert_validation_errors(context.exception.validation_result, *expected_errors)

    def test_build_validate_assembly_with_non_json_configuration(self):
        project_sim = self.simlab.simulate_invalid_assembly_non_json_configuration()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        configuration_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'notjson.xml')
        self.assert_validation_errors(context.exception.validation_result, 'Configuration [{0}]: is not a json file (with a .json extension)'.format(configuration_path))

    def test_build_validate_assembly_with_non_json_runtime(self):
        project_sim = self.simlab.simulate_invalid_assembly_non_json_runtime()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        runtime_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'notjson.xml')
        self.assert_validation_errors(context.exception.validation_result, 'Runtime [{0}]: is not a json file (with a .json extension)'.format(runtime_path))

    def test_build_validate_assembly_with_non_json_test(self):
        project_sim = self.simlab.simulate_invalid_assembly_non_json_test()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        test_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'notjson.xml')
        self.assert_validation_errors(context.exception.validation_result, 'Test [{0}]: is not a json file (with a .json extension)'.format(test_path))

    def test_build_validate_assembly_with_invalid_json_configuration(self):
        project_sim = self.simlab.simulate_invalid_assembly_invalid_json_configuration()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        configuration_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'notvalid.json')
        self.assert_validation_errors(context.exception.validation_result, 'Configuration [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(configuration_path))

    def test_build_validate_assembly_with_invalid_json_runtime(self):
        project_sim = self.simlab.simulate_invalid_assembly_invalid_json_runtime()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        runtime_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'notvalid.json')
        self.assert_validation_errors(context.exception.validation_result, 'Runtime [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(runtime_path))

    def test_build_validate_assembly_with_invalid_json_test(self):
        project_sim = self.simlab.simulate_invalid_assembly_invalid_json_test()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        test_path = os.path.join(project_sim.path, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'notvalid.json')
        self.assert_validation_errors(context.exception.validation_result, 'Test [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(test_path))


class TestBuildValidateAssemblySubprojects(ProjectSimTestCase):

    def test_validate_assembly_subproject_without_descriptor_file(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_no_descriptor()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        descriptor_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_NO_DESCRIPTOR, ASSEMBLY_DESCRIPTOR_DIR, ASSEMBLY_DESCRIPTOR_YML_FILE)
        self.assert_validation_errors(context.exception.validation_result, 'No descriptor found at: {0}'.format(descriptor_path))

    def test_validate_assembly_subproject_descriptor_name(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_mismatch_descriptor_name()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        descriptor_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_MISMATCH_DESCRIPTOR_NAME, ASSEMBLY_DESCRIPTOR_DIR, 'assembly.yml')
        expected_errors = []
        expected_errors.append('Descriptor [{0}]: name \'resource::notvalid::9.7\' includes type \'resource\' but this should be \'assembly\' based on project configuration'.format(descriptor_path))
        expected_errors.append(
            'Descriptor [{0}]: name \'resource::notvalid::9.7\' includes \'notvalid\' but this should be \'sub_invalid_mismatch_descriptor_name-contains_invalid_mismatch_descriptor_name\' based on project configuration'.format(descriptor_path))
        expected_errors.append('Descriptor [{0}]: name \'resource::notvalid::9.7\' includes version \'9.7\' but this should be \'1.0\' based on project configuration'.format(descriptor_path))
        self.assert_validation_errors(context.exception.validation_result, *expected_errors)


    def test_validate_assembly_subproject_with_non_json_configuration(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_non_json_configuration()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        configuration_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_NON_JSON_CONFIGURATION,
                                          ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'notjson.xml')
        self.assert_validation_errors(context.exception.validation_result, 'Configuration [{0}]: is not a json file (with a .json extension)'.format(configuration_path))

    def test_validate_assembly_subproject_with_non_json_runtime(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_non_json_runtime()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        runtime_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_NON_JSON_RUNTIME, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'notjson.xml')
        self.assert_validation_errors(context.exception.validation_result, 'Runtime [{0}]: is not a json file (with a .json extension)'.format(runtime_path))

    def test_validate_assembly_subproject_with_non_json_test(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_non_json_test()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        test_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_NON_JSON_TEST, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'notjson.xml')
        self.assert_validation_errors(context.exception.validation_result, 'Test [{0}]: is not a json file (with a .json extension)'.format(test_path))

    def test_validate_assembly_subproject_with_invalid_json_configuration(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_invalid_json_configuration()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        configuration_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_INVALID_JSON_CONFIGURATION,
                                          ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_CONFIGURATIONS_DIR, 'notvalid.json')
        self.assert_validation_errors(context.exception.validation_result, 'Configuration [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(configuration_path))

    def test_validate_assembly_subproject_with_invalid_json_runtime(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_invalid_json_runtime()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        runtime_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_INVALID_JSON_RUNTIME,
                                    ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_RUNTIME_DIR, 'notvalid.json')
        self.assert_validation_errors(context.exception.validation_result, 'Runtime [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(runtime_path))

    def test_validate_assembly_subproject_with_invalid_json_test(self):
        project_sim = self.simlab.simulate_assembly_contains_invalid_assembly_invalid_json_test()
        project = Project(project_sim.path)
        build_options = BuildOptions()
        with self.assertRaises(BuildValidationError) as context:
            project.build(build_options)
        test_path = os.path.join(project_sim.path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_INVALID_ASSEMBLY_INVALID_JSON_TEST, ASSEMBLY_BEHAVIOUR_DIR, ASSEMBLY_TESTS_DIR, 'notvalid.json')
        self.assert_validation_errors(context.exception.validation_result, 'Test [{0}]: does not contain valid JSON: Expecting value: line 1 column 1 (char 0)'.format(test_path))
