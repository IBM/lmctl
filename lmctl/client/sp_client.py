import pynetbox
from .sp_apis import (
    SitePlannerAPIGroup, 
    CircuitsGroup, 
    DCIMGroup, 
    ExtrasGroup, 
    IPAMGroup, 
    TenancyGroup, 
    VirtualizationGroup, 
    NFVIAutomationGroup,
    NFVIManagementGroup,
    NFVOAutomationGroup
)

class SitePlannerClient:
    
    def __init__(self, address: str, api_token: str = None):
        self.address = self._parse_address(address)
        self.api_token = api_token
        self.pynb_api = pynetbox.api(self.address, token=self.api_token)
        self.pynb_api.http_session.verify = False

    def _parse_address(self, address: str) -> str:
        if address is not None:
            while address.endswith('/'):
                address = address[:-1]
        return address

    @property
    def circuits(self) -> CircuitsGroup:
        return CircuitsGroup(self)

    @property
    def dcim(self) -> DCIMGroup:
        return DCIMGroup(self)

    @property
    def extras(self) -> ExtrasGroup:
        return ExtrasGroup(self)

    @property
    def ipam(self) -> IPAMGroup:
        return IPAMGroup(self)

    @property
    def tenancy(self) -> TenancyGroup:
        return TenancyGroup(self)

    @property
    def virtualization(self) -> VirtualizationGroup:
        return VirtualizationGroup(self)

    @property
    def nfvi_automation(self) -> NFVIAutomationGroup:
        return NFVIAutomationGroup(self)

    @property
    def nfvo_automation(self) -> NFVOAutomationGroup:
        return NFVOAutomationGroup(self)

    @property
    def nfvi_management(self) -> NFVIManagementGroup:
        return NFVIManagementGroup(self)