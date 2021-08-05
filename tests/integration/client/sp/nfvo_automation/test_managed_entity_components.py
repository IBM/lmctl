from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from tests.integration.client.sp.utils import ManagedEntitySetup

class TestManagedEntityComponentsAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.automation_setup = ManagedEntitySetup('test-mecomps', tester)
    
    @classmethod
    def after_test_case(cls, tester):
        cls.automation_setup.destroy()

    def _get_api(self, sp_client):
        return sp_client.nfvo_automation.managed_entity_components

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-mecomps-crud'),
            'enabled': 'enabled',
            'properties': {
                'compPropA': 'test'
            },
            'managed_entity': self.automation_setup.managed_entity['id'],
            'parent_property_name': 'dummyComp'
        }

    def _build_update_data(self, obj):
        obj['enabled'] = 'disabled'
        return obj
    