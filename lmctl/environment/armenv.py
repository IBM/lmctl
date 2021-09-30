from .common import build_address
from typing import Union
import lmctl.drivers.arm as arm_drivers
from pydantic.dataclasses import dataclass
from pydantic import root_validator
from lmctl.utils.dcutils.dc_capture import recordattrs

DEFAULT_PROTOCOL = 'https'

@recordattrs
@dataclass
class ArmEnvironment:
    name: str = None
    address: str = None
    host: str = None
    port: Union[str,int] = None
    protocol: str = DEFAULT_PROTOCOL
    onboarding_addr: str = None

    @root_validator(pre=True)
    @classmethod
    def normalize_addresses(cls, values):
        address = values.get('address', None)
        if address is None:
            host = values.get('host', None)
            host = host.strip() if host is not None else None
            if not host:
                raise ValueError('AnsibleRM environment cannot be configured without "address" property or "host" property')
            protocol = values.get('protocol', DEFAULT_PROTOCOL)
            port = values.get('port', None)
            address = build_address(host, protocol=protocol, port=port)
            values['address'] = address
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
