import unittest
from lmctl.cli.format import JsonFormat, BadFormatError

TEST_JSON_LIST = '''\
{
  "items": [
    "abc",
    123,
    {
      "someObject": {
        "data": "some data"
      }
    }
  ]
}'''

TEST_JSON_ELEMENT='''\
{
  "someObject": {
    "data": "some data"
  }
}'''

class TestJsonFormat(unittest.TestCase):

    def test_convert_list(self):
        test_list = ['abc', 123, {'someObject': {'data': 'some data'}}]
        output = JsonFormat().convert_list(test_list)
        self.assertEqual(output, TEST_JSON_LIST)
    
    def test_convert_element(self):
        element = {'someObject': {'data': 'some data'}}
        output = JsonFormat().convert_element(element)
        self.assertEqual(output, TEST_JSON_ELEMENT)

    def test_read(self):
        result = JsonFormat().read(TEST_JSON_ELEMENT)
        self.assertEqual(result, {'someObject': {'data': 'some data'}})

    def test_read_invalid(self):
        with self.assertRaises(BadFormatError) as context:
            JsonFormat().read('notJson')
        self.assertTrue('Failed to read content as JSON: ' in str(context.exception))