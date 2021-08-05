from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from lmctl.client import SitePlannerClientError

class TestVirtualInfrastructureTypesAPI(SitePlannerAPITests.CRUDTest):

    def _get_api(self, sp_client):
        return sp_client.nfvi_management.virtual_infrastructure_types

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-virtinf-crud'), 
            'comments': 'Test comments'
        }

    def _build_update_data(self, obj):
        obj['comments'] = 'Updated comments'
        return obj
