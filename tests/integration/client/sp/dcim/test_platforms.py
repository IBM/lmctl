from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from lmctl.client import SitePlannerClientError

class TestPlatformsAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.manufacturer = tester.default_sp_client.dcim.manufacturers.create({'name': tester.short_exec_prepended_name('test-platforms'), 'slug': tester.short_exec_prepended_name('test-platforms')})
        
    @classmethod
    def after_test_case(cls, tester):
        tester.default_sp_client.dcim.manufacturers.delete(cls.manufacturer['id'])
        
    def _get_api(self, sp_client):
        return sp_client.dcim.platforms

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-platforms-crud'), 
            'slug': self.tester.short_exec_prepended_name('test-platforms-crud'),
            'manufacturer': self.manufacturer['id'],
            'description': 'Test platform'
        }

    def _build_update_data(self, obj):
        obj['description'] = 'Updated description'
        return obj
