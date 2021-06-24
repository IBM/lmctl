import unittest
from lmctl.utils.trace_ctx import TracingContext

class TestTracingContext(unittest.TestCase):

    def test_set(self):
        trace_ctx = TracingContext()
        self.assertIsNone(trace_ctx.get('name'))
        trace_ctx.set('name', 'tester')
        self.assertEqual(trace_ctx.get('name'), 'tester')

    def test_get_returns_default_when_not_found(self):
        trace_ctx = TracingContext()
        self.assertEqual(trace_ctx.get('name', default='A default'), 'A default')

    def test_remove(self):
        trace_ctx = TracingContext()
        trace_ctx.set('name', 'tester')
        self.assertEqual(trace_ctx.get('name'), 'tester')
        trace_ctx.remove('name')
        self.assertIsNone(trace_ctx.get('name'))
    
    def test_has(self):
        trace_ctx = TracingContext()
        self.assertFalse(trace_ctx.has('name'))
        trace_ctx.set('name', 'tester')
        self.assertTrue(trace_ctx.has('name'))
        trace_ctx.remove('name')
        self.assertFalse(trace_ctx.has('name'))

    def test_set_and_get_transaction_id(self):
        trace_ctx = TracingContext()
        trace_ctx.set_transaction_id('123')
        self.assertEqual(trace_ctx.get_transaction_id(), '123')
        
    def test_remove_transaction_id(self):
        trace_ctx = TracingContext()
        trace_ctx.set_transaction_id('123')
        self.assertEqual(trace_ctx.get_transaction_id(), '123')
        trace_ctx.remove_transaction_id()
        self.assertIsNone(trace_ctx.get_transaction_id())

    def test_has_transaction_id(self):
        trace_ctx = TracingContext()
        self.assertFalse(trace_ctx.has_transaction_id())
        trace_ctx.set_transaction_id('123')
        self.assertTrue(trace_ctx.has_transaction_id())
        trace_ctx.remove_transaction_id()
        self.assertFalse(trace_ctx.has_transaction_id())
        
    def test_clear(self):
        trace_ctx = TracingContext()
        trace_ctx.set_transaction_id('123')
        trace_ctx.set('name', 'tester')
        self.assertEqual(trace_ctx.get('name'), 'tester')
        self.assertEqual(trace_ctx.get_transaction_id(), '123')

        trace_ctx.clear()
        
        self.assertIsNone(trace_ctx.get('name'))
        self.assertIsNone(trace_ctx.get_transaction_id())

    def test_to_http_header_dict(self):
        trace_ctx = TracingContext()
        trace_ctx.set_transaction_id('123')
        trace_ctx.set('processid', '456')
        self.assertEqual(trace_ctx.to_http_header_dict(), {
            'x-tracectx-transactionid': '123',
            'x-tracectx-processid': '456'
        })

    def test_to_log_dict(self):
        trace_ctx = TracingContext()
        trace_ctx.set_transaction_id('123')
        trace_ctx.set('processid', '456')
        self.assertEqual(trace_ctx.to_log_dict(), {
            'tracectx.transactionid': '123',
            'tracectx.processid': '456'
        })

    def test_scope(self):
        trace_ctx = TracingContext()
        trace_ctx.set_transaction_id('123')
        trace_ctx.set('dash-item', 'testing a dash item')
        trace_ctx.set('name', 'orig-name')
        trace_ctx.set('static', 'this value never changes')
        with trace_ctx.scope(transaction_id='789'):
            self.assertEqual(trace_ctx.get_transaction_id(), '789')
            self.assertEqual(trace_ctx.get('name'), 'orig-name')
            self.assertEqual(trace_ctx.get('dash-item'), 'testing a dash item')
            self.assertEqual(trace_ctx.get('static'), 'this value never changes')

        with trace_ctx.scope(transaction_id='789', name='new-name'):
            self.assertEqual(trace_ctx.get_transaction_id(), '789')
            self.assertEqual(trace_ctx.get('name'), 'new-name')
            self.assertEqual(trace_ctx.get('dash-item'), 'testing a dash item')
            self.assertEqual(trace_ctx.get('static'), 'this value never changes')

        with trace_ctx.scope(name='new-name'):
            self.assertEqual(trace_ctx.get_transaction_id(), '123')
            self.assertEqual(trace_ctx.get('name'), 'new-name')
            self.assertEqual(trace_ctx.get('dash-item'), 'testing a dash item')
            self.assertEqual(trace_ctx.get('static'), 'this value never changes')

        with trace_ctx.scope(ctx_values={'name': 'new-name-in-dict', 'dash-item': 'updated dash item'}):
            self.assertEqual(trace_ctx.get_transaction_id(), '123')
            self.assertEqual(trace_ctx.get('name'), 'new-name-in-dict')
            self.assertEqual(trace_ctx.get('dash-item'), 'updated dash item')
            self.assertEqual(trace_ctx.get('static'), 'this value never changes')

        with trace_ctx.scope(transaction_id='789', name='new-name', ctx_values={'dash-item': 'updated dash item'}):
            self.assertEqual(trace_ctx.get_transaction_id(), '789')
            self.assertEqual(trace_ctx.get('name'), 'new-name')
            self.assertEqual(trace_ctx.get('dash-item'), 'updated dash item')
            self.assertEqual(trace_ctx.get('static'), 'this value never changes')

        with trace_ctx.scope(name='new-name', ctx_values={'name': 'new-name-in-dict'}):
            self.assertEqual(trace_ctx.get_transaction_id(), '123')
            self.assertEqual(trace_ctx.get('name'), 'new-name') # Kwarg > ctx_values
            self.assertEqual(trace_ctx.get('dash-item'), 'testing a dash item')
            self.assertEqual(trace_ctx.get('static'), 'this value never changes')

        with trace_ctx.scope(transactionid='789'):
            self.assertEqual(trace_ctx.get_transaction_id(), '789')

        with trace_ctx.scope(transaction_id='789', ctx_values={'transactionid': '456'}):
            self.assertEqual(trace_ctx.get_transaction_id(), '789') # transaction_id arg > ctx_values
    
        self.assertEqual(trace_ctx.get_transaction_id(), '123')
        self.assertEqual(trace_ctx.get('name'), 'orig-name')
        self.assertEqual(trace_ctx.get('dash-item'), 'testing a dash item')
        self.assertEqual(trace_ctx.get('static'), 'this value never changes')

    def test_scope_replaces_orig_value_if_existed(self):
        trace_ctx = TracingContext()
        trace_ctx.set('name', 'orig-name')
        with trace_ctx.scope(name='new-name', extra='some-value'):
            self.assertEqual(trace_ctx.get('name'), 'new-name')
            self.assertEqual(trace_ctx.get('extra'), 'some-value')
        self.assertEqual(trace_ctx.get('name'), 'orig-name')
        self.assertIsNone(trace_ctx.get('extra'))
        self.assertFalse(trace_ctx.has('extra'))
