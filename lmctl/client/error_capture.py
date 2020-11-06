from .exceptions import TNCOClientError

class TNCOErrorCapture:

    def __init__(self):
        self.error = None

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):
        if value and isinstance(value, TNCOClientError):
            self.error = value
            return True

def tnco_error_capture():
    return TNCOErrorCapture()
