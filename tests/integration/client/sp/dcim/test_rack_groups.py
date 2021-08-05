from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from lmctl.client import SitePlannerClientError

class TestRackGroupsAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.site = tester.default_sp_client.dcim.sites.create({'name': tester.short_exec_prepended_name('test-rgroups'), 'slug': tester.short_exec_prepended_name('test-rgroups')})
        cls.parent_rack_group = tester.default_sp_client.dcim.rack_groups.create({
            'name': tester.short_exec_prepended_name('test-rgroups-parent'), 
            'slug': tester.short_exec_prepended_name('test-rgroups-parent'),
            'site': cls.site['id']
        })
    @classmethod
    def after_test_case(cls, tester):
        tester.default_sp_client.dcim.rack_groups.delete(cls.parent_rack_group['id'])
        tester.default_sp_client.dcim.sites.delete(cls.site['id'])

    def _get_api(self, sp_client):
        return sp_client.dcim.rack_groups

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-rgroups-crud'), 
            'slug': self.tester.short_exec_prepended_name('test-rgroups-crud'),
            'description': 'Test rack group',
            'site': self.site['id'],
            'parent': self.parent_rack_group['id']
        }

    def _build_update_data(self, obj):
        obj['description'] = 'Updated description'
        return obj
