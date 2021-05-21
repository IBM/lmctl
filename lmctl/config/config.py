from typing import Dict, Any
from lmctl.environment.group import EnvironmentGroup
from pydantic.dataclasses import dataclass
from pydantic import Field
from dataclasses import asdict

@dataclass
class Config:
    environments: Dict[str, EnvironmentGroup] = Field(default_factory=dict)
    active_environment: str = Field(default=None)

    @property
    def raw_environments(self):
        raw = {}
        for k,v in self.environments.items():
            raw[k] = asdict(v)   
        return raw
