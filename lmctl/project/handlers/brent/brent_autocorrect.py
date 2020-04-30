import os
import yaml
import shutil
import lmctl.utils.descriptors as descriptor_utils
import lmctl.project.validation as project_validation

class BrentCorrectableValidation:

    def __init__(self):
        self.rename_inf_path = False

    def validate_and_autocorrect(self, journal, validation_options, errors, warnings, descriptor_path, inf_path, inf_manifest_path, lifecycle_path, lifecycle_manifest_path):
        self.validate_unsupported_lifecycle_manifest(journal, validation_options, errors, warnings, lifecycle_manifest_path, descriptor_path)
        self.validate_unsupported_infrastructure_manifest(journal, validation_options, errors, warnings, inf_manifest_path, descriptor_path)
        self.validate_unsupported_infrastructure(journal, validation_options, errors, warnings, descriptor_path, inf_path, lifecycle_path)
        if self.rename_inf_path:
            self.__rename_infrastructure_dir(journal, validation_options, errors, warnings, inf_path)
        self.validate_driver_types_missing_selectors(journal, validation_options, errors, warnings, descriptor_path)

    def __rename_infrastructure_dir(self, journal, validation_options, errors, warnings, inf_path):
        #Rename infrastructure directory to keep as a backup, rather than remove it
        if os.path.exists(inf_path):
            try:
                os.rename(inf_path, inf_path + '-bak')
            except Exception as e:
                msg = 'Failed to rename infrastructure directory {0} to {1}, this directory is no longer needed after correcting infrastructure validation errors, please remove. Rename error was: {2}'.format(inf_path, inf_path + '-bak', str(e))
                journal.error_event(msg)
                warnings.append(project_validation.ValidationViolation(msg))

    def validate_unsupported_infrastructure(self, journal, validation_options, errors, warnings, descriptor_path, inf_path, lifecycle_path):
        if os.path.exists(descriptor_path):
            descriptor = descriptor_utils.DescriptorParser().read_from_file(descriptor_path)
            if 'infrastructure' in descriptor.raw and isinstance(descriptor.infrastructure, dict):
                entry_needing_lifecycle_fix = []
                entry_needing_discover_fix = []
                for inf_type, inf_entry in descriptor.infrastructure.items():
                    if 'template' in inf_entry:
                        entry_needing_lifecycle_fix.append(inf_type)
                    if 'discover' in inf_entry:
                        entry_needing_discover_fix.append(inf_type)
                if (len(entry_needing_lifecycle_fix) + len(entry_needing_discover_fix)) > 0:
                    if validation_options.allow_autocorrect == True:
                        journal.event('Found unsupported infrastructure entries referencing templates [{0}], attempting to autocorrect by moving contents to Create/Delete/queries entries in descriptor'.format(descriptor_path))
                        managed_to_autocorrect = False
                        autocorrect_error = None
                        try:
                            entry_needing_fix = entry_needing_lifecycle_fix + entry_needing_discover_fix
                            for inf_type in entry_needing_fix:
                                driver_type = inf_type
                                if inf_type == 'Openstack':
                                    driver_type = 'openstack'
                                elif inf_type == 'Kubernetes':
                                    driver_type = 'kubernetes'
                                target_lifecycle_path = os.path.join(lifecycle_path, driver_type)
                                if not os.path.exists(target_lifecycle_path):
                                    os.makedirs(target_lifecycle_path)
                                inf_entry = descriptor.infrastructure[inf_type]
                                self.__move_template_files(inf_path, target_lifecycle_path, inf_type, inf_entry)
                                if inf_type in entry_needing_lifecycle_fix:
                                    create_properties = None
                                    if inf_type == 'Openstack' and inf_entry.get('template', {}).get('template-type') == 'TOSCA':
                                        create_properties = {
                                            'template-type': {
                                                'value': inf_entry.get('template', {}).get('template-type')
                                            }
                                        }
                                    self.__add_driver_to_lifecycle(descriptor, driver_type, inf_type, create_properties=create_properties)
                                if inf_type in entry_needing_discover_fix:
                                    self.__add_driver_to_queries(descriptor, driver_type, inf_type)
                                descriptor.infrastructure[inf_type] = {}
                            descriptor_utils.DescriptorParser().write_to_file(descriptor, descriptor_path)
                            self.rename_inf_path = True
                            managed_to_autocorrect = True
                        except Exception as e:
                            autocorrect_error = e
                            raise
                        if not managed_to_autocorrect:
                            msg = 'Found unsupported infrastructure entries referencing templates [{0}]: this format is no longer supported by the Brent Resource Manager. Unable to autocorrect this issue, please add this information to the Create/Delete lifecycle and/or queries manually instead'.format(descriptor_path)
                            if autocorrect_error is not None:
                                msg += ' (autocorrect error={0})'.format(str(autocorrect_error))
                            journal.error_event(msg)
                            errors.append(project_validation.ValidationViolation(msg))
                            return   
                    else:
                        msg = 'Found infrastructure entries referencing templates [{0}]: this format is no longer supported by the Brent Resource Manager. Add this information to the Create/Delete lifecycle and/or queries instead or enable the autocorrect option'.format(descriptor_path)
                        journal.error_event(msg)
                        errors.append(project_validation.ValidationViolation(msg))
                        return

    def validate_unsupported_infrastructure_manifest(self, journal, validation_options, errors, warnings, inf_manifest_path, descriptor_path):
        if os.path.exists(inf_manifest_path) and os.path.exists(descriptor_path):
            if validation_options.allow_autocorrect == True:
                journal.event('Found unsupported infrastructure manifest [{0}], attempting to autocorrect by moving contents to Resource descriptor'.format(inf_manifest_path))
                managed_to_autocorrect = False
                autocorrect_error = None
                try:
                    with open(inf_manifest_path, 'r') as f:
                        inf_manifest_content = yaml.safe_load(f.read())
                    descriptor = descriptor_utils.DescriptorParser().read_from_file(descriptor_path)
                    if 'templates' in inf_manifest_content:
                        for template_entry in inf_manifest_content['templates']:
                            if 'infrastructure_type' in template_entry:
                                infrastructure_type = template_entry['infrastructure_type']
                                template_file = template_entry.get('file', None)
                                template_type = template_entry.get('template_type', None)
                                descriptor.insert_infrastructure_template(infrastructure_type, template_file, template_type=template_type)
                    if 'discover' in inf_manifest_content:
                        for discover_entry in inf_manifest_content['discover']:
                            if 'infrastructure_type' in discover_entry:
                                infrastructure_type = discover_entry['infrastructure_type']
                                template_file = discover_entry.get('file', None)
                                template_type = discover_entry.get('template_type', None)
                                descriptor.insert_infrastructure_discover(infrastructure_type, template_file, template_type=template_type)
                    descriptor_utils.DescriptorParser().write_to_file(descriptor, descriptor_path)
                    os.rename(inf_manifest_path, inf_manifest_path + '.bak')
                    self.rename_inf_path = True
                    managed_to_autocorrect = True
                except Exception as e:
                    autocorrect_error = e
                if not managed_to_autocorrect:
                    msg = 'Found infrastructure manifest [{0}]: this file is no longer supported by the Brent Resource Manager. Unable to autocorrect this issue, please add this information to the Resource descriptor manually instead'.format(inf_manifest_path)
                    if autocorrect_error is not None:
                        msg += ' (autocorrect error={0})'.format(str(autocorrect_error))
                    journal.error_event(msg)
                    errors.append(project_validation.ValidationViolation(msg))
                    return    
            else:
                msg = 'Found infrastructure manifest [{0}]: this file is no longer supported by the Brent Resource Manager. Add this information to the Resource descriptor instead or enable the autocorrect option'.format(inf_manifest_path)
                journal.error_event(msg)
                errors.append(project_validation.ValidationViolation(msg))
                return

    def validate_unsupported_lifecycle_manifest(self, journal, validation_options, errors, warnings, lifecycle_manifest_path, descriptor_path):
        if os.path.exists(lifecycle_manifest_path) and os.path.exists(descriptor_path):
            if validation_options.allow_autocorrect == True:
                journal.event('Found unsupported lifecycle manifest [{0}], attempting to autocorrect by moving contents to Resource descriptor'.format(lifecycle_manifest_path))
                managed_to_autocorrect = False
                autocorrect_error = None
                try:
                    with open(lifecycle_manifest_path, 'r') as f:
                        lifecycle_manifest_content = yaml.safe_load(f.read())
                    descriptor = descriptor_utils.DescriptorParser().read_from_file(descriptor_path)
                    if 'types' in lifecycle_manifest_content:
                        for entry in lifecycle_manifest_content['types']:
                            if 'lifecycle_type' in entry and 'infrastructure_type' in entry:
                                lifecycle_type = entry['lifecycle_type']
                                infrastructure_type = entry['infrastructure_type']
                                if lifecycle_type in descriptor.default_driver:
                                    if 'selector' not in descriptor.default_driver[lifecycle_type]:
                                        descriptor.default_driver[lifecycle_type]['selector'] = {}
                                    if 'infrastructure-type' not in descriptor.default_driver[lifecycle_type]['selector']:
                                        descriptor.default_driver[lifecycle_type]['selector']['infrastructure-type'] = []
                                    descriptor.default_driver[lifecycle_type]['selector']['infrastructure-type'].append(infrastructure_type)
                                else:
                                    descriptor.insert_default_driver(lifecycle_type, [infrastructure_type])
                    descriptor_utils.DescriptorParser().write_to_file(descriptor, descriptor_path)
                    os.rename(lifecycle_manifest_path, lifecycle_manifest_path + '.bak')
                    managed_to_autocorrect = True
                except Exception as e:
                    autocorrect_error = e
                if not managed_to_autocorrect:
                    msg = 'Found lifecycle manifest [{0}]: this file is no longer supported by the Brent Resource Manager. Unable to autocorrect this issue, please add this information to the Resource descriptor manually instead'.format(lifecycle_manifest_path)
                    if autocorrect_error is not None:
                        msg += ' (autocorrect error={0})'.format(str(autocorrect_error))
                    journal.error_event(msg)
                    errors.append(project_validation.ValidationViolation(msg))
                    return 
            else:
                msg = 'Found lifecycle manifest [{0}]: this file is no longer supported by the Brent Resource Manager. Add this information to the Resource descriptor instead or enable the autocorrect option'.format(lifecycle_manifest_path)
                journal.error_event(msg)
                errors.append(project_validation.ValidationViolation(msg))
                return

    def validate_driver_types_missing_selectors(self, journal, validation_options, errors, warnings, descriptor_path):
        if os.path.exists(descriptor_path):
            descriptor = descriptor_utils.DescriptorParser().read_from_file(descriptor_path)
            driver_entries_needing_fix = self.__gather_driver_types_missing_selector_key(journal, validation_options, errors, warnings, descriptor, 'lifecycle')
            driver_entries_needing_fix.extend(self.__gather_driver_types_missing_selector_key(journal, validation_options, errors, warnings, descriptor, 'operations'))
            if 'default-driver' in descriptor.raw and isinstance(descriptor.default_driver, dict):
                for driver_type, driver_entry in descriptor.default_driver.items():
                    if 'infrastructure-type' in driver_entry:
                        driver_entries_needing_fix.append(driver_entry)
            if len(driver_entries_needing_fix) > 0:
                if validation_options.allow_autocorrect == True:
                    journal.event('Found lifecycle/operation/default-driver entries missing \'selector\' key before \'infrastructure-type\' [{0}], attempting to autocorrect by moving contents under a selector key'.format(descriptor_path))
                    managed_to_autocorrect = False
                    autocorrect_error = None
                    try:
                        for entry_needing_fix in driver_entries_needing_fix:
                            entry_needing_fix['selector'] = {'infrastructure-type': entry_needing_fix['infrastructure-type']}
                            entry_needing_fix.pop('infrastructure-type')
                        descriptor_utils.DescriptorParser().write_to_file(descriptor, descriptor_path)
                        managed_to_autocorrect = True
                    except Exception as e:
                        autocorrect_error = e
                    if not managed_to_autocorrect:
                        msg = 'Found lifecycle/operation/default-driver entries missing \'selector\' key before \'infrastructure-type\' [{0}]: Unable to autocorrect this issue, please add this information to the Resource descriptor manually instead'.format(descriptor_path)
                        if autocorrect_error is not None:
                            msg += ' (autocorrect error={0})'.format(str(autocorrect_error))
                        journal.error_event(msg)
                        errors.append(project_validation.ValidationViolation(msg))
                        return   
                else:
                    msg = 'Found lifecycle/operation/default-driver entries missing \'selector\' key before \'infrastructure-type\' [{0}]: this format is no longer supported by the Brent Resource Manager. Move infrastructure-type information under the selector key or enable the autocorrect option'.format(descriptor_path)
                    journal.error_event(msg)
                    errors.append(project_validation.ValidationViolation(msg))
                    return

    def __gather_driver_types_missing_selector_key(self, journal, validation_options, errors, warnings, descriptor, entry_key):
        driver_entries_needing_fix = []
        if entry_key in descriptor.raw and isinstance(descriptor.raw[entry_key], dict):
            lifecycle = descriptor.raw[entry_key]
            for lifecycle_name, lifecycle_entry in lifecycle.items():
                if lifecycle_entry is not None:
                    if 'drivers' in lifecycle_entry:
                        drivers = lifecycle_entry['drivers']
                        if isinstance(drivers, dict):
                            for driver_type, driver_entry in drivers.items():
                                if 'infrastructure-type' in driver_entry:
                                    driver_entries_needing_fix.append(driver_entry)
        return driver_entries_needing_fix

    def __move_template_files(self, inf_path, target_lifecycle_path, inf_type, inf_entry):
        if 'template' in inf_entry:
            orig_template_file = inf_entry['template'].get('file')
            orig_template_type = inf_entry['template'].get('template-type')
            if inf_type == 'Openstack':
                if orig_template_type == 'TOSCA':
                    target_file_path = os.path.join(target_lifecycle_path, 'tosca.yaml')
                else:
                    target_file_path = os.path.join(target_lifecycle_path, 'heat.yaml')
            else:
                target_file_path = os.path.join(target_lifecycle_path, os.path.basename(orig_template_file))
            self.__move_file_and_backup_original(os.path.join(inf_path, orig_template_file), target_file_path)
        if 'discover' in inf_entry:
            orig_template_file = inf_entry['discover'].get('file')
            orig_template_type = inf_entry['discover'].get('template-type')
            if inf_type == 'Openstack':
                target_file_path = os.path.join(target_lifecycle_path, 'discover.yaml')
            else:
                target_file_path = os.path.join(target_lifecycle_path, os.path.basename(orig_template_file))
            self.__move_file_and_backup_original(os.path.join(inf_path, orig_template_file), target_file_path)

    def __refactor_lifecycle_to_map(self, descriptor):
        lifecycle = descriptor.lifecycle
        new_lifecycle = {}
        for lifecycle_name in lifecycle:
            new_lifecycle[lifecycle_name] = {}
        descriptor.lifecycle = new_lifecycle
        return descriptor.lifecycle

    def __add_driver_to_lifecycle(self, descriptor, driver_type, inf_type, create_properties=None):
        lifecycle = descriptor.lifecycle
        if isinstance(lifecycle, list):
            lifecycle = self.__refactor_lifecycle_to_map(descriptor)
        if 'Create' not in lifecycle or lifecycle['Create'] == None:
            lifecycle['Create'] = {}
        self.__add_driver_to_lifecycle_entry(lifecycle['Create'], driver_type, inf_type, properties=create_properties)
        if 'Delete' not in lifecycle or lifecycle['Delete'] == None:
            lifecycle['Delete'] = {}
        self.__add_driver_to_lifecycle_entry(lifecycle['Delete'], driver_type, inf_type)

    def __add_driver_to_queries(self, descriptor, driver_type, inf_type, properties=None):
        queries = descriptor.queries
        self.__add_driver_to_lifecycle_entry(queries, driver_type, inf_type, properties=properties)
    
    def __add_driver_to_lifecycle_entry(self, lifecycle_entry, driver_type, inf_type, properties=None):
        if 'drivers' not in lifecycle_entry:
            lifecycle_entry['drivers'] = {}
        drivers = lifecycle_entry['drivers']
        if driver_type not in drivers:
            drivers[driver_type] = {}
        driver_type_entry = drivers[driver_type]
        if 'selector' not in driver_type_entry:
            driver_type_entry['selector'] = {}
        selector = driver_type_entry['selector']
        if 'infrastructure-type' not in selector:
            selector['infrastructure-type'] = []
        inf_types = selector['infrastructure-type']
        if inf_type not in inf_types:
            inf_types.append(inf_type)
        if properties is not None:
            if 'properties' not in driver_type_entry:
                driver_type_entry['properties'] = properties.copy()

    def __move_file_and_backup_original(self, orignal_path, target_path):
        if os.path.exists(orignal_path):
            shutil.copyfile(orignal_path, target_path)
            os.rename(orignal_path, orignal_path + '.bak')