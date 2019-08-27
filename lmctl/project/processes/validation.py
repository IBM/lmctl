import os
import lmctl.utils.descriptors as descriptor_utils
import lmctl.project.validation as validation
import lmctl.project.handlers.interface as handlers_api

class ValidationProcessError(Exception):
    pass

class SourceValidator:

    def __init__(self, journal, source_config):
        self.journal = journal
        self.source_config = source_config

    def validate_descriptor(self, descriptor_path, errors, warnings):
        if not os.path.exists(descriptor_path):
            msg = 'No descriptor found at: {0}'.format(descriptor_path)
            self.journal.error_event(msg)
            errors.append(validation.ValidationViolation(msg))
            return
        self.journal.event('Checking descriptor found at: {0}'.format(descriptor_path))
        valid_yml = False
        try:
            descriptor = descriptor_utils.DescriptorParser().read_from_file(descriptor_path)
            valid_yml = True
        except descriptor_utils.DescriptorParsingError as e:
            errors.append(validation.ValidationViolation('Descriptor [{0}]: could not be parsed: {1}'.format(descriptor_path, str(e))))
        if valid_yml and descriptor.has_name() is True:
            type_invalid = False
            name_invalid = False
            version_invalid = False
            descriptor_type, descriptor_name, descriptor_version = descriptor.get_split_name()
            expected_type = descriptor_utils.ASSEMBLY_DESCRIPTOR_TYPE
            if self.source_config.is_resource_project():
                expected_type = descriptor_utils.RESOURCE_DESCRIPTOR_TYPE
            if descriptor_type != expected_type:
                errors.append(validation.ValidationViolation('Descriptor [{0}]: name \'{1}\' includes type \'{2}\' but this should be \'{3}\' based on project configuration'.format(descriptor_path, descriptor.get_name(),
                                                                                                                                                                          descriptor_type, expected_type)))
            if descriptor_name != self.source_config.full_name:
                errors.append(validation.ValidationViolation('Descriptor [{0}]: name \'{1}\' includes \'{2}\' but this should be \'{3}\' based on project configuration'.format(descriptor_path, descriptor.get_name(),
                                                                                                                                                                     descriptor_name, self.source_config.full_name)))
            if descriptor_version != self.source_config.version:
                errors.append(validation.ValidationViolation('Descriptor [{0}]: name \'{1}\' includes version \'{2}\' but this should be \'{3}\' based on project configuration'.format(descriptor_path, descriptor.get_name(),
                                                                                                                                                                             descriptor_version, self.source_config.version)))
            if type_invalid or name_invalid or version_invalid:
                self.journal.error_event('Descriptor validation failed')

class ValidationProcess:
    def __init__(self, project, options, journal):
        self.project = project
        self.journal = journal
        self.options = options

    def execute(self):
        return ValidationWorker(self.project, self.options, self.journal).work()

class ValidationWorker:

    def __init__(self, project, options, journal):
        self.project = project
        self.journal = journal
        self.options = options

    def work(self):
        self.journal.section('Validate Sources')
        all_errors = []
        all_warnings = []
        source_validator = SourceValidator(self.journal, self.project.config)
        try:
            validate_sources_result = self.project.source_handler.validate_sources(self.journal, source_validator)
        except handlers_api.SourceHandlerError as e:
            raise ValidationProcessError(str(e)) from e
        all_errors.extend(validate_sources_result.errors)
        all_warnings.extend(validate_sources_result.warnings)
        self.__validate_child_projects(all_errors, all_warnings)
        return validation.ValidationResult(all_errors, all_warnings)

    def __validate_child_projects(self, errors, warnings):
        for subproject in self.project.subprojects:
            self.journal.subproject(subproject.config.name)
            validation_result = ValidationWorker(subproject, self.options, self.journal).work()
            errors.extend(validation_result.errors)
            warnings.extend(validation_result.warnings)
            self.journal.subproject_end(subproject.config.name)
