from typing import Dict, Any
from lmctl.environment.group import EnvironmentGroup

class Config:

    def __init__(self, environments: Dict[str, EnvironmentGroup] = None, raw_environments: Dict[str,Any] = None):
        if environments is None:
            environments = {}
        self.environments = environments
        if raw_environments is None:
            raw_environments = {}
        self.raw_environments = raw_environments
