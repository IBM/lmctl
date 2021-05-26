from pydantic.dataclasses import dataclass
from pydantic import constr

@dataclass
class SitePlannerEnvironment:
    address: constr(strip_whitespace=True, min_length=1) = None
    api_token: str = DEFAULT_SECURE
