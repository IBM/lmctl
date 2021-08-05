from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from tests.integration.client.sp.utils import TNCOAutomationSetup

class TestManagedEntityTypesAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.tnco_automation_setup = TNCOAutomationSetup('test-metypes', tester)
    
    @classmethod
    def after_test_case(cls, tester):
        cls.tnco_automation_setup.destroy()

    def _get_api(self, sp_client):
        return sp_client.nfvo_automation.managed_entity_types

    def _build_create_data(self):
        return {
            'descriptor': self.tnco_automation_setup.assembly_descriptor['name'],
            'comments': 'Test type',
            'tags': ['testing', 'lmctl']
        }

    def _build_update_data(self, obj):
        obj['comments'] = 'This is an updated lmctl test managed entity type'
        return obj
    