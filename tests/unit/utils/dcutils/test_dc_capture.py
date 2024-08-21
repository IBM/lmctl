import unittest
from dataclasses import dataclass
import pydantic.dataclasses as pydanticdc
from lmctl.utils.dcutils.dc_capture import recordattrs, AttrRecord, attr_records, attr_records_dict, is_recording_attrs

@recordattrs
@dataclass
class Test:
    first: str
    second: int
    third: bool = False

@recordattrs
@pydanticdc.dataclass
class PydanticDataclass:
    first: str
    second: int
    third: bool = False

class TestRecordAttrs(unittest.TestCase):

    def test_record_init_args(self):
        inst = Test('A', 1)
        records = attr_records(inst)
        self.assertEqual(records, (
                AttrRecord(name='first', set_on='ON_INIT'),
                AttrRecord(name='second', set_on='ON_INIT'),
                AttrRecord(name='third', set_on='NOT_SET')
            )
        )

    def test_record_init_args_as_kwargs(self):
        inst = Test(first='A', second=1)
        records = attr_records(inst)
        self.assertEqual(records, (
                AttrRecord(name='first', set_on='ON_INIT'),
                AttrRecord(name='second', set_on='ON_INIT'),
                AttrRecord(name='third', set_on='NOT_SET')
            )
        )
    
    def test_record_init_kwargs(self):
        inst = Test('A', 1, third=True)
        records = attr_records(inst)
        self.assertEqual(records, (
                AttrRecord(name='first', set_on='ON_INIT'),
                AttrRecord(name='second', set_on='ON_INIT'),
                AttrRecord(name='third', set_on='ON_INIT')
            )
        )

    def test_record_init_kwargs_as_args(self):
        inst = Test('A', 1, True)
        records = attr_records(inst)
        self.assertEqual(records, (
                AttrRecord(name='first', set_on='ON_INIT'),
                AttrRecord(name='second', set_on='ON_INIT'),
                AttrRecord(name='third', set_on='ON_INIT')
            )
        )

    def test_record_on_set(self):
        inst = Test('A', 1)
        inst.first = 'B'
        inst.third = True
        
        records = attr_records(inst)

        self.assertEqual(records, (
                AttrRecord(name='first', set_on='ON_SET'),
                AttrRecord(name='second', set_on='ON_INIT'),
                AttrRecord(name='third', set_on='ON_SET')
            )
        )

    def test_record_on_init_value_set_to_default_still_recorded(self):
        # False is the default for "third" but we've explicitly set this value, so it is recorded as set_on=ON_INIT
        inst = Test('A', 1, third=False) 
        records = attr_records(inst)
        self.assertEqual(records, (
                AttrRecord(name='first', set_on='ON_INIT'),
                AttrRecord(name='second', set_on='ON_INIT'),
                AttrRecord(name='third', set_on='ON_INIT')
            )
        )

    def test_record_on_set_value_to_default_still_recorded(self):
        inst = Test('A', 1)
        # False is the default for "third" but we've explicitly set this value, so it is recorded as set_on=ON_SET
        inst.third = False
        records = attr_records(inst)
        self.assertEqual(records, (
                AttrRecord(name='first', set_on='ON_INIT'),
                AttrRecord(name='second', set_on='ON_INIT'),
                AttrRecord(name='third', set_on='ON_SET')
            )
        )
        
    def test_attr_records_dict(self):
        inst = Test('A', 1)
        records = attr_records_dict(inst)
        self.assertEqual(records, {
            'first': AttrRecord(name='first', set_on='ON_INIT'),
            'second': AttrRecord(name='second', set_on='ON_INIT'),
            'third': AttrRecord(name='third', set_on='NOT_SET')
        })

    def test_is_recording_attrs(self):
        inst = Test('A', 1)
        self.assertTrue(is_recording_attrs(inst))

        @dataclass
        class NotRecording:
            dummy: str = None

        self.assertFalse(is_recording_attrs(NotRecording()))

    def test_record_pydantic_dataclass(self):
        inst = PydanticDataclass(first='A', second=1)
        records = attr_records(inst)
        self.assertEqual(records, (
                AttrRecord(name='first', set_on='ON_INIT'),
                AttrRecord(name='second', set_on='ON_INIT'),
                AttrRecord(name='third', set_on='NOT_SET')
            )
        )

    def test_pydantic_from_dict(self):
        data = {'first': 'A', 'second': 1}
        inst = PydanticDataclass(**data)
        records = attr_records(inst)
        self.assertEqual(records, (
                AttrRecord(name='first', set_on='ON_INIT'),
                AttrRecord(name='second', set_on='ON_INIT'),
                AttrRecord(name='third', set_on='NOT_SET')
            )
        )
        data = {'first': 'A', 'second': 1, 'third': True}
        inst = PydanticDataclass(**data)
        records = attr_records(inst)
        self.assertEqual(records, (
                AttrRecord(name='first', set_on='ON_INIT'),
                AttrRecord(name='second', set_on='ON_INIT'),
                AttrRecord(name='third', set_on='ON_INIT')
            )
        )

class TestAttrRecord(unittest.TestCase):

    def test_is_set(self):
        record = AttrRecord('test', 'ON_INIT')
        self.assertTrue(record.is_set)
        record = AttrRecord('test', 'ON_SET')
        self.assertTrue(record.is_set)
        record = AttrRecord('test', 'NOT_SET')
        self.assertFalse(record.is_set)