from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from lmctl.client import SitePlannerClientError

class TestRegionsAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.parent_region = tester.default_sp_client.dcim.regions.create({'name': tester.short_exec_prepended_name('test-regions-parent'), 'slug': tester.short_exec_prepended_name('test-regions-parent')})

    @classmethod
    def after_test_case(cls, tester):
        tester.default_sp_client.dcim.regions.delete(cls.parent_region['id'])

    def _get_api(self, sp_client):
        return sp_client.dcim.regions

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-regions-crud'), 
            'slug': self.tester.short_exec_prepended_name('test-regions-crud'),
            'description': 'Test region',
            'parent': self.parent_region['id']
        }

    def _build_update_data(self, obj):
        obj['description'] = 'Updated description'
        return obj
