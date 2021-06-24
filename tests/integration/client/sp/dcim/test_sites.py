from tests.integration.client.sp.common_tests import SitePlannerAPITests
from lmctl.client import SitePlannerClientError


class TestSitesAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.region = tester.default_sp_client.dcim.regions.create({'name': tester.short_exec_prepended_name('test-sites'), 'slug': tester.short_exec_prepended_name('test-sites')})
        cls.tenant = tester.default_sp_client.tenancy.tenants.create({'name': tester.short_exec_prepended_name('test-sites'), 'slug': tester.short_exec_prepended_name('test-sites')})

    @classmethod
    def after_test_case(cls, tester):
        tester.default_sp_client.dcim.regions.delete(cls.region['id'])
        tester.default_sp_client.tenancy.tenants.delete(cls.tenant['id'])

    def _get_api(self, sp_client):
        return sp_client.dcim.sites

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-sites-crud'), 
            'slug': self.tester.short_exec_prepended_name('test-sites-crud'),
            'status': 'active',
            'facility': '123',
            'asn': 12,
            'time_zone': 'GMT',
            'description': 'Test site',
            'physical_address': '1 Example Street',
            'shipping_address': '1 Example Street',
            'latitude': '90.000000',
            'longitude': '135.000000',
            'contact_name': 'Joe Bloggs',
            'contact_phone': '112233',
            'contact_email': 'joebloggs@example.com',
            'comments': 'This is an lmctl test site',
            'tags': ['testing', 'lmctl'],
            'region': self.region['id'],
            'tenant': self.tenant['id']
        }

    def _build_update_data(self, obj):
        obj['description'] = 'Updated description'
        return obj
