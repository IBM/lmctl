from tests.integration.client.sp.sp_test_base import SitePlannerAPITests
from lmctl.client import SitePlannerClientError


class TestClustersAPI(SitePlannerAPITests.CRUDTest):

    @classmethod
    def before_test_case(cls, tester):
        cls.cluster_group = tester.default_sp_client.virtualization.cluster_groups.create({'name': tester.short_exec_prepended_name('test-clusters'), 'slug': tester.short_exec_prepended_name('test-clusters')})
        cls.cluster_type = tester.default_sp_client.virtualization.cluster_types.create({'name': tester.short_exec_prepended_name('test-clusters'), 'slug': tester.short_exec_prepended_name('test-clusters')})
        cls.tenant = tester.default_sp_client.tenancy.tenants.create({'name': tester.short_exec_prepended_name('test-clusters'), 'slug': tester.short_exec_prepended_name('test-clusters')})
        cls.site = tester.default_sp_client.dcim.sites.create({'name': tester.short_exec_prepended_name('test-clusters'), 'slug': tester.short_exec_prepended_name('test-clusters')})

    @classmethod
    def after_test_case(cls, tester):
        tester.default_sp_client.virtualization.cluster_types.delete(cls.cluster_type['id'])
        tester.default_sp_client.virtualization.cluster_groups.delete(cls.cluster_group['id'])
        tester.default_sp_client.tenancy.tenants.delete(cls.tenant['id'])
        tester.default_sp_client.dcim.sites.delete(cls.site['id'])

    def _get_api(self, sp_client):
        return sp_client.virtualization.clusters

    def _build_create_data(self):
        return {
            'name': self.tester.short_exec_prepended_name('test-cluster-crud'), 
            'type': self.cluster_type['id'],
            'group': self.cluster_group['id'],
            'tenant': self.tenant['id'],
            'site': self.site['id'],
            'comments': 'Test comment',
            'tags': ['lmctl', 'testing']
        }

    def _build_update_data(self, obj):
        obj['comments'] = 'Updated comment'
        return obj
