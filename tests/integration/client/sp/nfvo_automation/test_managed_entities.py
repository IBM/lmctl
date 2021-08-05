from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from tests.integration.client.sp.utils import ManagedEntityTypeSetup

class TestManagedEntitiesAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.automation_setup = ManagedEntityTypeSetup('test-mgdents', tester)
    
    @classmethod
    def after_test_case(cls, tester):
        cls.automation_setup.destroy()

    def _get_api(self, sp_client):
        return sp_client.nfvo_automation.managed_entities

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-mgdents-crud'),
            'type': self.automation_setup.managed_entity_type['id'],
            'status': 'active',
            'properties': {
                'dummyProp': 'test'
            },
            'comments': 'Test',
            'tags': ['testing', 'lmctl']
        }

    def _build_update_data(self, obj):
        obj['properties'] = {
            'dummyProp': 'test',
            'dummyIntProp': 42
        }
        return obj

    def _check_build_success(self, automation_process_id):
        automation_process = self.tester.default_sp_client.nfvo_automation.managed_entity_automation_processes.get(automation_process_id)
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
        suffix = 'test-mgdents-build'
        managed_entity_api = self._get_api(self.tester.default_sp_client)
        # Create Managed Entity
        managed_entity = {
            'name': self.tester.short_exec_prepended_name('test-mgdents-build'),
            'type': self.automation_setup.managed_entity_type['id'],
            'status': 'active',
            'properties': {
                'dummyProp': 'test'
            },
            'comments': 'Test',
            'tags': ['testing', 'lmctl']
        }
        managed_entity = managed_entity_api.create(managed_entity)
        try:
            # Build Managed Entity
            build_process_id = managed_entity_api.build(managed_entity['id'])
            self.tester.wait_until(self._check_build_success, build_process_id)

            # Teardown Managed Entity
            teardown_process_id = managed_entity_api.teardown(managed_entity['id'])
            self.tester.wait_until(self._check_build_success, teardown_process_id)
        finally:
            # Delete Managed Entity
            managed_entity_api.delete(managed_entity['id'])
        