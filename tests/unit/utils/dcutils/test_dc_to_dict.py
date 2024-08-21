import unittest
from typing import List, Union, Tuple, Dict
from dataclasses import dataclass
from lmctl.utils.dcutils.dc_capture import recordattrs
from lmctl.utils.dcutils.dc_to_dict import asdict
from collections import namedtuple

@dataclass
class RegularDataclass:
    first: str
    second: int
    third: bool = False

@recordattrs
@dataclass
class RecordedDataclass:
    first: str
    second: int
    third: bool = False

@recordattrs
@dataclass
class DataclassWithNestedRegularDataclass:
    the_dc: RegularDataclass = None

@recordattrs
@dataclass
class DataclassWithNestedRecordedDataclass:
    the_dc: RecordedDataclass = None

@recordattrs
@dataclass
class DataclassWithList:
    the_list: List = None

@recordattrs
@dataclass
class DataclassWithListOfDataclass:
    the_list: List[Union[RegularDataclass, RecordedDataclass]] = None

@recordattrs
@dataclass
class DataclassWithTuple:
    the_tuple: Tuple = None

@recordattrs
@dataclass
class DataclassWithTupleOfDataclass:
    the_tuple: Tuple[Union[RegularDataclass, RecordedDataclass]] = None

@recordattrs
@dataclass
class DataclassWithDict:
    the_dict: Dict = None

@recordattrs
@dataclass
class DataclassWithDictOfDataclass:
    the_Dict: Dict[str, Union[RegularDataclass, RecordedDataclass]] = None

Point = namedtuple('Point', ['x', 'y'])

@recordattrs
@dataclass
class DataclassWithNamedTuple:
    point: Point = None

class TestAsDict(unittest.TestCase):

    def test_regular_dataclass_as_dict(self):
        dc = RegularDataclass('A', 1)
        self.assertEqual(asdict(dc), {
            'first': 'A',
            'second': 1
        })

    def test_recorded_dataclass_as_dict(self):
        dc = RecordedDataclass('A', 1)
        self.assertEqual(asdict(dc), {
            'first': 'A',
            'second': 1
        })

    def test_as_dict_on_nested_regular_dataclass(self):
        dc = DataclassWithNestedRegularDataclass(RegularDataclass('A', 1))
        self.assertEqual(asdict(dc), {
            'the_dc': {
                'first': 'A',
                'second': 1
            }
        })

    def test_as_dict_on_nested_recorded_dataclass(self):
        dc = DataclassWithNestedRecordedDataclass(RecordedDataclass('A', 1))
        self.assertEqual(asdict(dc), {
            'the_dc': {
                'first': 'A',
                'second': 1
            }
        })
        dc.the_dc.third = True
        self.assertEqual(asdict(dc), {
            'the_dc': {
                'first': 'A',
                'second': 1,
                'third': True
            }
        })
    
    def test_as_dict_on_list(self):
        dc = DataclassWithList(['A', 'B', 'C'])
        self.assertEqual(asdict(dc), {
            'the_list': ['A', 'B', 'C']
        })
        self.assertTrue(id(dc.the_list) != id(asdict(dc)['the_list']))

    def test_as_dict_on_list_not_set(self):
        dc = DataclassWithList()
        self.assertEqual(asdict(dc), {})

    def test_as_dict_on_list_of_regular_dataclass(self):
        dc = DataclassWithList([RegularDataclass('A', 1), RegularDataclass('B', 2, third=True)])
        self.assertEqual(asdict(dc), {
            'the_list': [
                {'first': 'A', 'second': 1},
                {'first': 'B', 'second': 2, 'third': True}
            ]
        })

    def test_as_dict_on_list_of_recorded_dataclass(self):
        dc = DataclassWithList([RecordedDataclass('A', 1), RecordedDataclass('B', 2, third=True)])
        self.assertEqual(asdict(dc), {
            'the_list': [
                {'first': 'A', 'second': 1},
                {'first': 'B', 'second': 2, 'third': True}
            ]
        })
    
    def test_as_dict_on_tuple(self):
        dc = DataclassWithTuple(('A', 'B', 'C'))
        self.assertEqual(asdict(dc), {
            'the_tuple': ('A', 'B', 'C')
        })
        self.assertTrue(id(dc.the_tuple) != id(asdict(dc)['the_tuple']))

    def test_as_dict_on_tuple_not_set(self):
        dc = DataclassWithTuple()
        self.assertEqual(asdict(dc), {})

    def test_as_dict_on_tuple_of_regular_dataclass(self):
        dc = DataclassWithTupleOfDataclass((RegularDataclass('A', 1), RegularDataclass('B', 2, third=True)))
        self.assertEqual(asdict(dc), {
            'the_tuple': (
                {'first': 'A', 'second': 1},
                {'first': 'B', 'second': 2, 'third': True}
            )
        })

    def test_as_dict_on_tuple_of_recorded_dataclass(self):
        dc = DataclassWithTupleOfDataclass((RecordedDataclass('A', 1), RecordedDataclass('B', 2, third=True)))
        self.assertEqual(asdict(dc), {
            'the_tuple': (
                {'first': 'A', 'second': 1},
                {'first': 'B', 'second': 2, 'third': True}
            )
        })

    def test_as_dict_on_dict(self):
        dc = DataclassWithDict({'A': 'test1', 'B': 'test2'})
        self.assertEqual(asdict(dc), {
            'the_dict': {'A': 'test1', 'B': 'test2'}
        })
        self.assertTrue(id(dc.the_dict) != id(asdict(dc)['the_dict']))

    def test_as_dict_on_dict_not_set(self):
        dc = DataclassWithDict()
        self.assertEqual(asdict(dc), {})

    def test_as_dict_on_dict_of_regular_dataclass(self):
        dc = DataclassWithDict({'A': RegularDataclass('A', 1), 'B': RegularDataclass('B', 2, third=True)})
        self.assertEqual(asdict(dc), {
            'the_dict': {
                'A': {'first': 'A', 'second': 1},
                'B': {'first': 'B', 'second': 2, 'third': True}
            }
        })

    def test_as_dict_on_dict_of_recorded_dataclass(self):
        dc = DataclassWithDict({'A': RecordedDataclass('A', 1), 'B': RecordedDataclass('B', 2, third=True)})
        self.assertEqual(asdict(dc), {
            'the_dict': {
                'A': {'first': 'A', 'second': 1},
                'B': {'first': 'B', 'second': 2, 'third': True}
            }
        })
    
    def test_as_dict_on_named_tuple(self):
        dc = DataclassWithNamedTuple(point=Point(11, 22))
        self.assertEqual(asdict(dc), {
            'point': Point(11, 22)
        })