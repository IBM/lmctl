from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from lmctl.client import SitePlannerClientError

class TestRacksAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.site = tester.default_sp_client.dcim.sites.create({'name': tester.short_exec_prepended_name('test-racks'), 'slug': tester.short_exec_prepended_name('test-racks')})
        cls.rack_group = tester.default_sp_client.dcim.rack_groups.create({
            'name': tester.short_exec_prepended_name('test-racks'), 
            'slug': tester.short_exec_prepended_name('test-racks'),
            'site': cls.site['id']
        })
        cls.rack_role = tester.default_sp_client.dcim.rack_roles.create({
            'name': tester.short_exec_prepended_name('test-racks'), 
            'slug': tester.short_exec_prepended_name('test-racks'),
            'color': '000000'
        })
        cls.tenant = tester.default_sp_client.tenancy.tenants.create({'name': tester.short_exec_prepended_name('test-racks'), 'slug': tester.short_exec_prepended_name('test-racks')})

    @classmethod
    def after_test_case(cls, tester):
        tester.default_sp_client.dcim.rack_groups.delete(cls.rack_group['id'])
        tester.default_sp_client.dcim.rack_roles.delete(cls.rack_role['id'])
        tester.default_sp_client.dcim.sites.delete(cls.site['id'])
        tester.default_sp_client.tenancy.tenants.delete(cls.tenant['id'])

    def _get_api(self, sp_client):
        return sp_client.dcim.racks

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-racks'), 
            'facility_id': '123',
            'site': self.site['id'],
            'group': self.rack_group['id'],
            'tenant': self.tenant['id'],
            'status': 'active',
            'role': self.rack_role['id'],
            'serial': 'R123',
            'asset_tag': self.tester.short_exec_prepended_name('R1'),
            'type': '2-post-frame',
            'width': 10,
            'u_height': 42,
            'desc_units': True,
            'outer_width': 600,
            'outer_depth': 200,
            'outer_unit': 'mm',
            'comments': 'This is an lmctl test rack',
            'tags': ['testing', 'lmctl']
        }

    def _build_update_data(self, obj):
        obj['comments'] = 'This is an updated lmctl test rack'
        return obj
