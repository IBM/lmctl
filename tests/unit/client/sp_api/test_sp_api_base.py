import unittest
from unittest.mock import patch, MagicMock
from lmctl.client.sp_apis import SitePlannerCrudAPI
from pynetbox.core.response import Record, RecordSet

class DeviceAPI(SitePlannerCrudAPI):
    _endpoint_chain = 'dcim.devices'

class TestSitePlannerAPI(unittest.TestCase):

    def setUp(self):
        self.sp_client = MagicMock()

    def _build_record_set(self, endpoint, *records):
        endpoint.return_obj = Record
        mock_request = MagicMock()
        mock_request.get.return_value = iter([r for r in records])
        rs = RecordSet(endpoint=endpoint, request=mock_request)
        return rs

    def _build_record(self, endpoint, values):
        return Record(values=values, api=MagicMock(), endpoint=endpoint)

    def test_all(self):
        api = DeviceAPI(self.sp_client)
        endpoint = self.sp_client.pynb_api.dcim.devices

        endpoint.all.return_value = self._build_record_set(endpoint,
            {'id': '123', 'name': 'DeviceA'},
            {'id': '456', 'name': 'DeviceB'}
        )
        
        result = api.all()
        self.assertEqual(result, [
           {'id': '123', 'name': 'DeviceA'},
           {'id': '456', 'name': 'DeviceB'} 
        ])
        endpoint.all.assert_called_once()

    def test_all_with_filter(self):
        api = DeviceAPI(self.sp_client)
        endpoint = self.sp_client.pynb_api.dcim.devices

        endpoint.filter.return_value = self._build_record_set(endpoint,
            {'id': '123', 'name': 'DeviceA'},
            {'id': '456', 'name': 'DeviceB'}
        )
        
        result = api.all(q='Device')
        self.assertEqual(result, [
           {'id': '123', 'name': 'DeviceA'},
           {'id': '456', 'name': 'DeviceB'} 
        ])
        endpoint.filter.assert_called_once_with(limit=0, q='Device')

    def test_get(self):
        api = DeviceAPI(self.sp_client)
        endpoint = self.sp_client.pynb_api.dcim.devices

        endpoint.get.return_value = self._build_record(endpoint, {'id': '123', 'name': 'DeviceA'})
        
        result = api.get('123')
        self.assertEqual(result, {'id': '123', 'name': 'DeviceA'})
        endpoint.get.assert_called_once_with('123')

    def test_create(self):
        api = DeviceAPI(self.sp_client)
        endpoint = self.sp_client.pynb_api.dcim.devices

        endpoint.create.return_value = self._build_record(endpoint, {'id': '123', 'name': 'DeviceA'})
        result = api.create({'name': 'DeviceA'})
        self.assertEqual(result, {'id': '123', 'name': 'DeviceA'})
        endpoint.create.assert_called_once_with({'name': 'DeviceA'})

    def test_update(self):
        api = DeviceAPI(self.sp_client)
        endpoint = self.sp_client.pynb_api.dcim.devices

        endpoint.get.return_value = MagicMock()
        api.update({'id': '123', 'model': 'm1'})

        endpoint.get.return_value.update.assert_called_once_with({'id': '123', 'model': 'm1'})

    def test_delete(self):
        api = DeviceAPI(self.sp_client)
        endpoint = self.sp_client.pynb_api.dcim.devices

        endpoint.get.return_value = MagicMock()
        api.delete('123')

        endpoint.get.return_value.delete.assert_called_once()
