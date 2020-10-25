from typing import Dict
from lmctl.environment.group import EnvironmentGroup

class Config:

    def __init__(self, environments: Dict[str, EnvironmentGroup] = None):
        if environments is None:
            environments = {}
        self.environments = environments
