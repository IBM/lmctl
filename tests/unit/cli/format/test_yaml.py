import unittest
from lmctl.cli.format import YamlFormat, BadFormatError

TEST_YAML_LIST = '''\
items:
- abc
- 123
- someObject:
    data: some data
'''

TEST_YAML_ELEMENT='''\
someObject:
  data: some data
'''

class TestYamlFormat(unittest.TestCase):

    def test_convert_list(self):
        test_list = ['abc', 123, {'someObject': {'data': 'some data'}}]
        output = YamlFormat().convert_list(test_list)
        self.assertEqual(output, TEST_YAML_LIST)
    
    def test_convert_element(self):
        element = {'someObject': {'data': 'some data'}}
        output = YamlFormat().convert_element(element)
        self.assertEqual(output, TEST_YAML_ELEMENT)

    def test_read(self):
        result = YamlFormat().read(TEST_YAML_ELEMENT)
        self.assertEqual(result, {'someObject': {'data': 'some data'}})

    def test_read_invalid(self):
        with self.assertRaises(BadFormatError) as context:
            YamlFormat().read(': anotYAML-{abc}')
        self.assertTrue('Failed to read content as YAML: ' in str(context.exception))