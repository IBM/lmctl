from typing import Optional
from pydantic.dataclasses import dataclass
from pydantic import constr
from lmctl.utils.dcutils.dc_capture import recordattrs


@recordattrs
@dataclass
class SitePlannerEnvironmentOverrides:
    address: Optional[constr(strip_whitespace=True)] = None
    api_token: Optional[str] = None
    secure: Optional[bool] = True
