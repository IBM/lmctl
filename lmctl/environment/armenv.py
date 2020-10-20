from .common import Environment, EnvironmentConfigError, build_address
from typing import Union
import lmctl.drivers.arm as arm_drivers

class ArmEnvironment(Environment):

    def __init__(self, name: str, address: str = None, host: str = None, port: Union[str,int] = None, protocol: str = 'https', onboarding_addr: str = None):
        name = name.strip() if name is not None else None
        if not name:
            raise EnvironmentConfigError('AnsibleRM environment cannot be configured without property: name')
        self.name = name
        if address is not None:
            self._address = address
        else:
            host = host.strip() if host is not None else None
            if not host:
                raise EnvironmentConfigError('AnsibleRM environment cannot be configured without "address" property or "host" property')
            self._address = build_address(host, protocol=protocol, port=port)
        self.onboarding_addr = onboarding_addr.strip() if onboarding_addr is not None and len(onboarding_addr.strip())>0 else None

    @property
    def address(self):
        return self._address

    @property
    def api_address(self):
        return self._address

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
            raise EnvironmentConfigError('config not provided to session')
        self.env = session_config.env
        self.__arm_driver = None

    @property
    def arm_driver(self):
        if not self.__arm_driver:
            self.__arm_driver = arm_drivers.AnsibleRmDriver(self.env.api_address)
        return self.__arm_driver
