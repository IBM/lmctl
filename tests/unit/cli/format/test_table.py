import unittest
from lmctl.cli.format import TableFormat, Table, Column

class DummyTable(Table):
    columns = [
        Column('name', header='Name'),
        Column('status', header='Status', accessor=lambda x: 'OK' if x.get('status', None) in ['Excellent', 'Good'] else 'Unhealthy'),
    ]

class DummyTableNoHeaders(Table):
    columns = [
        Column('name'),
        Column('status', accessor=lambda x: 'OK' if x.get('status', None) in ['Excellent', 'Good'] else 'Unhealthy'),
    ]

EXPECTED_LIST = '''\
| Name   | Status    |
|--------+-----------|
| A      | OK        |
| B      | Unhealthy |
| C      | OK        |
| D      | Unhealthy |'''

EXPECTED_ELEMENT = '''\
| Name   | Status   |
|--------+----------|
| A      | OK       |'''

EXPECTED_ELEMENT_NO_HEADER_SET = '''\
| name   | status   |
|--------+----------|
| A      | OK       |'''
class TestTableFormat(unittest.TestCase):
    
    def test_convert_list(self):
        test_list = [
            {'name': 'A', 'status': 'Good'},
            {'name': 'B', 'status': 'Bad'},
            {'name': 'C', 'status': 'Excellent'},
            {'name': 'D'}
        ]
        output = TableFormat(table=DummyTable()).convert_list(test_list)
        self.assertEqual(output, EXPECTED_LIST)
    
    def test_convert_element(self):
        element = {'name': 'A', 'status': 'Good'}
        output = TableFormat(table=DummyTable()).convert_element(element)
        self.assertEqual(output, EXPECTED_ELEMENT)

    def test_table_with_columns_with_no_headers(self):
        element = {'name': 'A', 'status': 'Good'}
        output = TableFormat(table=DummyTable()).convert_element(element)
        self.assertEqual(output, EXPECTED_ELEMENT)
