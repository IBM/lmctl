from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from lmctl.client import SitePlannerClientError


class TestClusterGroupsAPI(SitePlannerAPITests.CRUDTest):

    def _get_api(self, sp_client):
        return sp_client.virtualization.cluster_groups

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-clugroup-crud'), 
            'slug': self.tester.short_exec_prepended_name('test-clugroup-crud'),
            'description': 'Test cluster group'
        }

    def _build_update_data(self, obj):
        obj['description'] = 'Updated description'
        return obj
