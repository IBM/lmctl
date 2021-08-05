from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from tests.integration.client.sp.utils import TNCOAutomationSetup
from lmctl.client.sp_apis.automation_context import AutomationContextAPIMixin
from lmctl.client.sp_apis.dcim import SitesAPI
from lmctl.client import SitePlannerClientError
import os

class TestAutomationContextAPIMixin(SitePlannerAPITests.BaseTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.tnco_automation_setup = TNCOAutomationSetup('test-autoctxmix', tester)

        cls.deployment_location = cls.tnco_automation_setup.deployment_location
        cls.res_pkg_id = cls.tnco_automation_setup.res_pkg_id
        cls.resource_descriptor = cls.tnco_automation_setup.resource_descriptor
        cls.assembly_descriptor = cls.tnco_automation_setup.assembly_descriptor
    
    @classmethod
    def after_test_case(cls, tester):
        cls.tnco_automation_setup.destroy()
    
    def _check_build_success(self, automation_process_id):
        automation_process = self.tester.default_sp_client.nfvi_automation.automation_context_processes.get(automation_process_id)
        assembly_process = self.tester.default_client.processes.get(automation_process['assembly_process_id'])
        status = assembly_process.get('status')
        if status in ['Completed']:
            return True
        elif status in ['Cancelled', 'Failed']:
            reason = assembly_process.get('statusReason')
            self.fail(f'Process failed with status {status}, reason: {reason}')
        else:
            return False

    def test_build_and_teardown(self):
        suffix = 'test-autoctxmix'
        # Create Automation Context
        automation_ctx = {
            'name': self.tester.short_exec_prepended_name(suffix), 
            'descriptorName': self.assembly_descriptor['name'],
            'object_type': 'dcim.site',
            'tags': [self.tester.short_exec_prepended_name(suffix)],
            'data_expressions': 'query site($id: String){site(pk: $id){id}}'
        }
        automation_ctx = self.tester.default_sp_client.nfvi_automation.automation_contexts.create(automation_ctx)

        # Create Site
        site = self.tester.default_sp_client.dcim.sites.create(
            {
                'name': self.tester.short_exec_prepended_name(suffix), 
                'slug': self.tester.short_exec_prepended_name(suffix),
                'tags': [self.tester.short_exec_prepended_name(suffix)]
            }
        )

        # Build Site
        build_process_id = self.tester.default_sp_client.dcim.sites.build(site['id'])
        self.tester.wait_until(self._check_build_success, build_process_id)

        # Teardown Site
        teardown_process_id = self.tester.default_sp_client.dcim.sites.teardown(site['id'])
        self.tester.wait_until(self._check_build_success, teardown_process_id)

class TestAutomationContextsAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        ## Add deployment location
        cls.deployment_location = tester.default_client.deployment_locations.create({
            'name': tester.exec_prepended_name('test-autoctx'),
            'infrastructureType': 'Other',
            'resourceManager': 'brent',
            'properties': {}
        })
        ## Upload Resource package
        res_pkg_path = tester.tmp_file('dummy_resource.zip')
        tester.build_resource_package_from(tester.test_file('dummy_resource'), res_pkg_path, suffix='test-autoctx')
        cls.res_pkg_id = tester.default_client.resource_packages.create(res_pkg_path)
        ## Get Resource descriptor 
        cls.resource_descriptor = tester.load_descriptor_from(tester.test_file(os.path.join('dummy_resource', 'Definitions', 'lm', 'resource.yaml')), suffix='test-autoctx')
        ## Add Assembly descriptor
        cls.assembly_descriptor = tester.load_descriptor_from(tester.test_file('dummy_assembly.yaml'), suffix='test-autoctx')
        cls.assembly_descriptor['properties']['resourceManager']['default'] = 'brent'
        cls.assembly_descriptor['properties']['deploymentLocation']['default'] = cls.deployment_location['name']
        tester.default_client.descriptors.create(cls.assembly_descriptor)

    @classmethod
    def after_test_case(cls, tester):
        tester.default_client.deployment_locations.delete(cls.deployment_location['id'])
        tester.default_client.resource_packages.delete(cls.res_pkg_id)
        tester.default_client.descriptors.delete(cls.resource_descriptor['name'])
        tester.default_client.descriptors.delete(cls.assembly_descriptor['name'])

    def _get_api(self, sp_client):
        return sp_client.nfvi_automation.automation_contexts

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-autoctx-crud'), 
            'descriptorName': self.assembly_descriptor['name'],
            'object_type': 'dcim.site',
            'tags': ['testing', 'lmctl'],
            'data_expressions': '{sites{id}}'
        }

    def _build_update_data(self, obj):
        obj['tags'] = ['testing', 'lmctl', 'updated']
        return obj

    def _check_build_success(self, automation_process_id):
        automation_process = self.tester.default_sp_client.nfvi_automation.automation_context_processes.get(automation_process_id)
        assembly_process = self.tester.default_client.processes.get(automation_process['assembly_process_id'])
        status = assembly_process.get('status')
        if status in ['Completed']:
            return True
        elif status in ['Cancelled', 'Failed']:
            reason = assembly_process.get('statusReason')
            self.fail(f'Process failed with status {status}, reason: {reason}')
        else:
            return False

    def test_build_and_teardown(self):
        self._execute_build_and_teardown(suffix='test-autoctx-build')

    def _execute_build_and_teardown(self, suffix):
        # Create Automation Context
        automation_ctx = {
            'name': self.tester.short_exec_prepended_name(suffix), 
            'descriptorName': self.assembly_descriptor['name'],
            'object_type': 'dcim.site',
            'tags': [self.tester.short_exec_prepended_name(suffix)],
            'data_expressions': 'query site($id: String){site(pk: $id){id}}'
        }
        api = self._get_api(self.tester.default_sp_client)
        automation_ctx = api.create(automation_ctx)

        # Create Site
        site = self.tester.default_sp_client.dcim.sites.create(
            {
                'name': self.tester.short_exec_prepended_name(suffix), 
                'slug': self.tester.short_exec_prepended_name(suffix),
                'tags': [self.tester.short_exec_prepended_name(suffix)]
            }
        )

        # Build Site
        build_process_id = api.build(object_type='dcim.site', object_pk=site['id'])
        self.tester.wait_until(self._check_build_success, build_process_id)

        # Teardown Site
        teardown_process_id = api.teardown(object_type='dcim.site', object_pk=site['id'])
        self.tester.wait_until(self._check_build_success, teardown_process_id)

        return {
            'build_process_id': build_process_id,
            'teardown_process_id': teardown_process_id,
            'site': site,
            'automation_ctx': automation_ctx
        }
      
    def test_build_dry_run(self):
        # Create Automation Context
        automation_ctx = {
            'name': self.tester.short_exec_prepended_name('test-autoctx-dry-run'), 
            'descriptorName': self.assembly_descriptor['name'],
            'object_type': 'dcim.site',
            'tags': [self.tester.short_exec_prepended_name('test-autoctx-dry-run')],
            'data_expressions': 'query site($id: String){site(pk: $id){id}}'
        }
        api = self._get_api(self.tester.default_sp_client)
        automation_ctx = api.create(automation_ctx)

        # Create Site
        site = self.tester.default_sp_client.dcim.sites.create(
            {
                'name': self.tester.short_exec_prepended_name('test-autoctx-dry-run'), 
                'slug': self.tester.short_exec_prepended_name('test-autoctx-dry-run'),
                'tags': [self.tester.short_exec_prepended_name('test-autoctx-dry-run')]
            }
        )

        # Build Site (Dry Run)
        dry_run_result = api.build_dry_run(object_type='dcim.site', object_pk=site['id'])
        self.assertEqual(dry_run_result, {
            'intent': {
                'assemblyName': 'dcim-site-' + str(site['id']),
                'descriptorName': self.assembly_descriptor['name'],
                'intendedState': 'Active',
                'properties': {
                    'site': {
                        'id': str(site['id'])
                    }
                },
                'tags': {
                    'objectType': 'dcim.site',
                    'objectPk': str(site['id'])
                }
            }
        })

    def test_automation_context_processes_api(self):
        exec_result = self._execute_build_and_teardown('test-autoctx-processes')

        processes_api = self.tester.default_sp_client.nfvi_automation.automation_context_processes

        # Get
        build_process_id = exec_result['build_process_id']
        build_process = processes_api.get(build_process_id)
        self.assertEqual(build_process['id'], build_process_id)
        self.assertEqual(build_process['action'], 'build')
        self.assertEqual(build_process['object_type'], 'dcim.site')
        self.assertEqual(build_process['object_pk'], str(exec_result['site']['id']))

        # All
        filter_result = processes_api.all(object_type='dcim.site', object_pk=exec_result['site']['id'])
        self.assertEqual(len(filter_result), 2)

        # Delete
        processes_api.delete(build_process_id)
        with self.assertRaises(SitePlannerClientError) as ctx:
            processes_api.get(build_process_id)
        self.assertEqual(str(ctx.exception), f'Could not find object with id: {build_process_id}')
        