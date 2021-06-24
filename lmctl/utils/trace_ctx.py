import threading

TRACE_CTX_HEADER_PREFIX = 'x-tracectx-'
TRANSACTION_ID_KEY = 'transactionid'
TRANSACTION_ID_HEADER = f'{TRACE_CTX_HEADER_PREFIX}{TRANSACTION_ID_KEY}'

TRACE_CTX_LOG_PREFIX = 'tracectx.'

class ScopedContext:

    def __init__(self, trace_ctx, ctx_changes):
        self.trace_ctx = trace_ctx
        self.originals = {}
        self.ctx_changes = ctx_changes

    def __enter__(self):
        for k,v in self.ctx_changes.items():
            if self.trace_ctx.has(k):
                self.originals[k] = self.trace_ctx.get(k, default=None)
            self.trace_ctx.set(k, v)

    def __exit__(self, exc_type, exc_val, exc_tb):
        for k,v in self.ctx_changes.items():
            if k in self.originals:
                self.trace_ctx.set(k, self.originals[k])
            else:
                self.trace_ctx.remove(k)
        self.originals.clear()

class TracingContext(threading.local):

    def __init__(self):
        self.data = {}

    def set_transaction_id(self, value):
        f"""
        Util to add {TRANSACTION_ID_KEY} value
        """
        self.set(TRANSACTION_ID_KEY, value)

    def get_transaction_id(self, default=None):
        f"""
        Util to get {TRANSACTION_ID_KEY} value
        """
        return self.get(TRANSACTION_ID_KEY, default=default)

    def remove_transaction_id(self):
        f"""
        Util to remove {TRANSACTION_ID_KEY} value
        """
        self.remove(TRANSACTION_ID_KEY)

    def has_transaction_id(self):
        f"""
        Util to check for {TRANSACTION_ID_KEY} value
        """
        return self.has(TRANSACTION_ID_KEY)

    def has(self, key):
        return key in self.data

    def set(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)

    def remove(self, key):
        self.data.pop(key, None)

    def clear(self):
        self.data = {}

    def to_http_header_dict(self):
        f"""
        Produces a dict of HTTP headers based on the current ctx. Each key is prefixed with {TRACE_CTX_HEADER_PREFIX}
        """
        headers = {}
        for k,v in self.data.items():
            headers[f'{TRACE_CTX_HEADER_PREFIX}{k}'] = v
        return headers

    def to_log_dict(self):
        f"""
        Produces a dict suitable for a logging record. Each key is lowercased and prefixed with {TRACE_CTX_LOG_PREFIX}
        """
        log_dict = {}
        for k,v in self.data.items():
            log_dict[f'{TRACE_CTX_LOG_PREFIX}{k.lower()}'] = v
        return log_dict

    def scope(self, transaction_id = None, ctx_values = None, **kwargs):
        if ctx_values is not None:
            merged_changes = ctx_values.copy()
        else:
            merged_changes = {}
        merged_changes.update(kwargs)
        if transaction_id is not None:
            merged_changes[TRANSACTION_ID_KEY] = transaction_id
        return ScopedContext(self, merged_changes)

trace_ctx = TracingContext()