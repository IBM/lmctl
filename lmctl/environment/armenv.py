from .common import build_address
from typing import Union, Optional
import lmctl.drivers.arm as arm_drivers
from pydantic.dataclasses import dataclass
from pydantic import model_validator
from lmctl.utils.dcutils.dc_capture import recordattrs

DEFAULT_PROTOCOL = 'https'

@recordattrs
@dataclass
class ArmEnvironment:
    name: Optional[str] = None
    address: Optional[str] = None
    host: Optional[str] = None
    port: Optional[Union[str,int]] = None
    protocol: str = DEFAULT_PROTOCOL
    onboarding_addr: str = None

    @model_validator(mode='before')
    @classmethod
    def normalize_addresses(cls, values):
        if hasattr(values, 'kwargs'):
            values_dict = values.kwargs
        else:
            values_dict = values
        address = values_dict.get('address', None)
        if address is None:
            host = values_dict.get('host', None)
            host = host.strip() if host is not None else None
            if not host:
                raise ValueError('AnsibleRM environment cannot be configured without "address" property or "host" property')
            protocol = values_dict.get('protocol', DEFAULT_PROTOCOL)
            port = values_dict.get('port', None)
            address = build_address(host, protocol=protocol, port=port)
            values_dict['address'] = address
        return values

    @property
    def api_address(self):
        return self.address

    def create_session_config(self):
        return ArmSessionConfig(self)

class ArmSessionConfig:

    def __init__(self, env):
        self.env = env

    def create(self):
        return ArmSession(self)

class ArmSession:

    def __init__(self, session_config):
        if not session_config:
            raise ValueError('config not provided to session')
        self.env = session_config.env
        self.__arm_driver = None

    @property
    def arm_driver(self):
        if not self.__arm_driver:
            self.__arm_driver = arm_drivers.AnsibleRmDriver(self.env.api_address)
        return self.__arm_driver
