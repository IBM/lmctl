from typing import Dict, Any
from lmctl.environment.group import EnvironmentGroup
from pydantic.dataclasses import dataclass
from pydantic import Field
from dataclasses import asdict

@dataclass
class Config:
    active_environment: str = Field(default=None)
    environments: Dict[str, EnvironmentGroup] = Field(default_factory=dict)

    @property
    def raw_environments(self):
        raw = {}
        for k,v in self.environments.items():
            raw[k] = asdict(v)   
        return raw
