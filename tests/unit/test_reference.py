import unittest
import unittest.mock as mock
from lmctl.reference import ReferenceSchema, BadReferenceError, ReferenceMachine, ReferenceBuilder, ReferenceResolver, NotResolvableError

ROOT_PREFIX = '$test'
SEPARATOR = ':'

ROOT_PREFIX_2 = '#'
SEPARATOR_2 = '/'

DOUBLE_CHAR_SEPARATOR = ':/'

class TestReferenceSchema(unittest.TestCase):

    def test_is_reference(self):
        schema = ReferenceSchema(ROOT_PREFIX, SEPARATOR)
        self.assertFalse(schema.is_reference('$test:'))
        self.assertFalse(schema.is_reference('$$test:a:b:c'))
        self.assertFalse(schema.is_reference('$testa.b.c'))
        self.assertTrue(schema.is_reference('$test:a.b.c'))
        self.assertTrue(schema.is_reference('$test:a:b:c'))

    def test_reference_value(self):
        schema = ReferenceSchema(ROOT_PREFIX, SEPARATOR)
        self.assertEqual(schema.reference_value('$test:a:b:c'), 'a:b:c')
        self.assertEqual(schema.reference_value('$test::a.b:c'), ':a.b:c')

    def test_reference_value_throws_error_when_invalid(self):
        schema = ReferenceSchema(ROOT_PREFIX, SEPARATOR)
        with self.assertRaises(BadReferenceError) as context:
            schema.reference_value('$$test:a:b:c')
        self.assertEqual(str(context.exception), '\'$$test:a:b:c\' is not a valid reference')
    
    def test_reference_breakdown(self):
        schema = ReferenceSchema(ROOT_PREFIX, SEPARATOR)
        self.assertEqual(schema.reference_breakdown('$test:a:b:c'), ['a', 'b', 'c'])
        self.assertEqual(schema.reference_breakdown('$test:a:b.c'), ['a', 'b.c'])
        self.assertEqual(schema.reference_breakdown('$test:partone:parttwo:partthree'), ['partone', 'parttwo', 'partthree'])
    
    def test_reference_breakdown_multi_char_separator(self):
        schema = ReferenceSchema(ROOT_PREFIX, DOUBLE_CHAR_SEPARATOR)
        self.assertEqual(schema.reference_breakdown('$test:/a:/b:/c'), ['a', 'b', 'c'])

    def test_reference_breakdown_throws_error_when_invalid(self):
        schema = ReferenceSchema(ROOT_PREFIX, SEPARATOR)
        with self.assertRaises(BadReferenceError) as context:
            schema.reference_breakdown('$$test:a:b:c')
        self.assertEqual(str(context.exception), '\'$$test:a:b:c\' is not a valid reference')

class TestReferenceMachine(unittest.TestCase):

    def test_builder(self):
        machine = ReferenceMachine(ROOT_PREFIX_2, SEPARATOR_2)
        builder = machine.builder()
        self.assertIsInstance(builder, ReferenceBuilder)
        self.assertEqual(builder.schema, machine.schema)

    def test_is_reference(self):
        machine = ReferenceMachine(ROOT_PREFIX_2, SEPARATOR_2)
        self.assertFalse(machine.is_reference('##/a/b/c'))
        self.assertFalse(machine.is_reference('#a.b.c'))
        self.assertTrue(machine.is_reference('#/a.b.c'))
        self.assertTrue(machine.is_reference('#/a/b/c'))

    @mock.patch('lmctl.reference.ReferenceResolver')
    def test_resolve(self, mock_resolver_init):
        machine = ReferenceMachine(ROOT_PREFIX_2, SEPARATOR_2)
        resolution_map = {}
        return_value = machine.resolve('#/a/b/c', resolution_map)
        mock_resolver_init.assert_called_once_with(machine.schema, resolution_map)
        mock_resolver_init.return_value.resolve.assert_called_once_with('#/a/b/c')
        self.assertEqual(return_value, mock_resolver_init.return_value.resolve.return_value)

class TestReferenceBuilder(unittest.TestCase):

    def test_add(self):
        builder = ReferenceBuilder(ReferenceSchema(ROOT_PREFIX_2, SEPARATOR_2))
        builder.add('testadd')
        builder.add('testadd2')
        self.assertEqual(builder.get(), '#/testadd/testadd2')
        
    def test_add_before(self):
        builder = ReferenceBuilder(ReferenceSchema(ROOT_PREFIX_2, SEPARATOR_2))
        builder.add_before('testadd')
        builder.add('testadd2')
        builder.add_before('testadd3')
        self.assertEqual(builder.get(), '#/testadd3/testadd/testadd2')

    def test_get_empty(self):
        builder = ReferenceBuilder(ReferenceSchema(ROOT_PREFIX_2, SEPARATOR_2))
        with self.assertRaises(BadReferenceError) as context:
            builder.get()
        self.assertEqual(str(context.exception), 'Cannot build a reference with no parts')

class TestReferenceResolver(unittest.TestCase):

    def test_resolve(self):
        schema = ReferenceSchema(ROOT_PREFIX, SEPARATOR)
        resolution_map = {
            'A': {
                'A': 'Route to A->A',
                'B': 'Route to A->B'
            },
            'B': {
                'A': 'Route to B->A',
                'B': {
                    'A': 'Route to B->B->A'
                }
            },
            'C': 'Route to C'
        }
        resolver = ReferenceResolver(schema, resolution_map)
        self.assertEqual(resolver.resolve('$test:C'), 'Route to C')
        self.assertEqual(resolver.resolve('$test:A:A'), 'Route to A->A')
        self.assertEqual(resolver.resolve('$test:B:A'), 'Route to B->A')
        self.assertEqual(resolver.resolve('$test:B:B:A'), 'Route to B->B->A')
    
    def test_resolve_throws_error_when_no_route(self):
        schema = ReferenceSchema(ROOT_PREFIX, SEPARATOR)
        resolution_map = { 'A': 'Route to A' }
        resolver = ReferenceResolver(schema, resolution_map)
        with self.assertRaises(NotResolvableError) as context:
            resolver.resolve('$test:D')
        self.assertEqual(str(context.exception), 'Cannot find \'D\' in reference: $test:D')
    
    def test_resolve_throws_error_when_invalid_route(self):
        schema = ReferenceSchema(ROOT_PREFIX, SEPARATOR)
        resolution_map = { 'A': 'Route to A' }
        resolver = ReferenceResolver(schema, resolution_map)
        with self.assertRaises(BadReferenceError) as context:
            resolver.resolve('$test:A:B')
        self.assertEqual(str(context.exception), 'Reference has invalid step from \'A\' to \'B\': $test:A:B')
    