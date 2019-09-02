from .common import Environment, EnvironmentConfigError, get_value_or_default, value_or_default
import lmctl.drivers.arm as arm_drivers

CONFIG_KWARGS = ['onboarding_addr']

HTTP_PROTOCOL = 'http'
HTTPS_PROTOCOL = 'https'
SUPPORTED_PROTOCOLS = [HTTP_PROTOCOL, HTTPS_PROTOCOL]

class ArmEnvironment(Environment):

    def __init__(self, name, host, port=None, protocol=HTTPS_PROTOCOL, **kwargs):
        name = value_or_default(name, None)
        if not name:
            raise EnvironmentConfigError('AnsibleRM environment cannot be configured without property: name')
        self.name = name
        host = value_or_default(host, None)
        if not host:
            raise EnvironmentConfigError('AnsibleRM environment cannot be configured without property: host (ip_address)')
        self.host = host
        self.port = value_or_default(port, None)
        protocol = str(value_or_default(protocol, HTTPS_PROTOCOL))
        self.protocol = protocol.lower()
        if self.protocol not in SUPPORTED_PROTOCOLS:
            raise EnvironmentConfigError('AnsibleRM environment cannot be configured with unsupported protocol \'{0}\'. Must be one of: {1}'.format(self.protocol, SUPPORTED_PROTOCOLS))
        self.__validate_for_unsupported_keys(kwargs)
        self.onboarding_addr = get_value_or_default(kwargs, 'onboarding_addr', None)

    def __validate_for_unsupported_keys(self, kwargs):
        for key,value in kwargs.items():
            if key not in CONFIG_KWARGS:
                raise EnvironmentConfigError('Unsupported key argument: {0}'.format(key))

    @property
    def address(self):
        return self.api_address

    @property
    def api_address(self):
        base = '{0}://{1}'.format(self.protocol, self.host)
        if self.port:
            base += ':{0}'.format(self.port)
        return base

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
