from typing import Dict, Optional
from .lmenv import TNCOEnvironment
from .armenv import ArmEnvironment
from pydantic.dataclasses import dataclass
from pydantic import constr, Field

@dataclass
class EnvironmentGroup:
    name: constr(strip_whitespace=True, min_length=1)
    description: Optional[str] = None
    tnco: Optional[TNCOEnvironment] = None
    arms: Optional[Dict[str, ArmEnvironment]] = Field(default_factory=dict)

    @property
    def lm(self):
        return self.tnco

    @property
    def has_lm(self):
        return self.has_tnco

    @property
    def has_tnco(self):
        return self.tnco is not None
