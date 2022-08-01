from typing import List, Callable, Tuple
from lmctl.client import TNCOClientHttpError

__all__ = (
    'IgnoreMissingSafetyNet',
    'DisableIgnoreMissingSafetyNet',
    'tnco_missing_detector',
)

class IgnoreMissingSafetyNet:
    
    def __init__(self, missing_detector: Callable):
        self.missing_detector = missing_detector
        self.is_missing = False
        self.reason = None

    def __enter__(self):
        return self

    def __exit__(self, etype, value, traceback):
        missing, reason = self.missing_detector(value)
        self.is_missing = missing
        self.reason = reason
        if self.is_missing:
            return True

class DisableIgnoreMissingSafetyNet(IgnoreMissingSafetyNet):

    def __exit__(self, etype, value, traceback):
        pass


def tnco_missing_detector(e: Exception) -> Tuple[bool, str]:
    if isinstance(e, TNCOClientHttpError) and e.status_code == 404:
        return True, e.detail_message
    return False, None
