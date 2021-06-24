from typing import Optional
from pydantic.dataclasses import dataclass
from pydantic import constr, root_validator
from lmctl.utils.dcutils.dc_capture import recordattrs
from lmctl.client import SitePlannerClient, SitePlannerClientBuilder


@recordattrs
@dataclass
class SitePlannerEnvironment:
    address: constr(strip_whitespace=True, min_length=1) = None
    api_token: Optional[str] = None 

    def build_client(self) -> SitePlannerClient:
        builder = SitePlannerClientBuilder()
        builder.address(self.address)
        builder.api_token(self.api_token)
        return builder.build()
