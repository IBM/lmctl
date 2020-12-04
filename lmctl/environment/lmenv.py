from .common import Environment, EnvironmentConfigError, EnvironmentRuntimeError, get_value_or_default, value_or_default
import lmctl.drivers.lm as lm_drivers

CONFIG_KWARGS = ['secure', 'username', 'auth_host', 'auth_port', 'auth_protocol', 'password', 'brent_name']

HTTP_PROTOCOL = 'http'
HTTPS_PROTOCOL = 'https'
SUPPORTED_PROTOCOLS = [HTTP_PROTOCOL, HTTPS_PROTOCOL]

class LmEnvironment(Environment):

    def __init__(self, name, host, port=None, protocol=HTTPS_PROTOCOL, path=None, secure=False, \
                                    username=None, password=None, auth_host=None, auth_port=None, auth_protocol=None, \
                                         brent_name='brent', kami_port=31289, kami_protocol=HTTP_PROTOCOL, kami_address=None):
        name = value_or_default(name, None)
        if not name:
            raise EnvironmentConfigError('LM environment cannot be configured without property: name')
        self.name = name
        host = value_or_default(host, None)
        if not host:
            raise EnvironmentConfigError('LM environment cannot be configured without property: host (ip_address)')
        self.host = host
        self.port = value_or_default(port, default=None)
        self.path = value_or_default(path, default=None)
        protocol = str(value_or_default(protocol, default=HTTPS_PROTOCOL))
        self.protocol = protocol.lower()
        if self.protocol not in SUPPORTED_PROTOCOLS:
            raise EnvironmentConfigError('LM environment cannot be configured with unsupported protocol \'{0}\'. Must be one of: {1}'.format(self.protocol, SUPPORTED_PROTOCOLS))
        self.brent_name = value_or_default(brent_name, default='brent')
        self.kami_port = kami_port
        self.kami_protocol = value_or_default(kami_protocol, default=self.protocol).lower()
        self._kami_address = value_or_default(kami_address, default=None)
        self.secure = value_or_default(secure, default=False)
        self.username = value_or_default(username, default=None)
        self.auth_host = value_or_default(auth_host, default=self.host)
        self.auth_port = value_or_default(auth_port, default=self.port)
        self.auth_protocol = value_or_default(auth_protocol, default=self.protocol).lower()
        self.password = value_or_default(password, default=None)
        if self.secure:
            if not self.username:
                raise EnvironmentConfigError('Secure LM environment cannot be configured without property: username. If the LM environment is not secure then set \'secure\' to False')
            if not self.auth_host:
                raise EnvironmentConfigError('Secure LM environment cannot be configured without property: auth_host')
            if self.auth_protocol not in SUPPORTED_PROTOCOLS:
                raise EnvironmentConfigError('LM environment cannot be configured with unsupported auth_protocol \'{0}\'. Must be one of: {1}'.format(self.auth_protocol, SUPPORTED_PROTOCOLS))

    def create_session_config(self):
        return LmSessionConfig(self, self.username, self.password)

    @property
    def is_secure(self):
        return self.secure

    @property
    def address(self):
        return self.api_address

    @property
    def api_address(self):
        base = '{0}://{1}'.format(self.protocol, self.host)
        if self.port:
            base += ':{0}'.format(self.port)
        if self.path:
            base += '/{0}'.format(self.path)
        return base

    @property
    def auth_address(self):
        if not self.secure:
            raise EnvironmentRuntimeError('auth_address cannot be determined for a non-secure LM environment')
        base = '{0}://{1}'.format(self.auth_protocol, self.auth_host)
        if self.auth_port:
            base += ':{0}'.format(self.auth_port)
        return base

    @property
    def kami_address(self):
        if self._kami_address is not None:
            return self._kami_address
        base = '{0}://{1}'.format(self.kami_protocol, self.host)
        if self.kami_port:
            base += ':{0}'.format(self.kami_port)
        return base

class LmSessionConfig:

    def __init__(self, env, username=None, password=None):
        self.env = env
        self.username = username
        self.password = password

    def create(self):
        return LmSession(self)

class LmSession:

    def __init__(self, session_config):
        if not session_config:
            raise EnvironmentConfigError('config not provided to session')
        self.env = session_config.env
        self.username = session_config.username
        self.password = session_config.password
        self.__lm_security_ctrl = None
        self.__descriptor_driver = None
        self.__onboard_rm_driver = None
        self.__topology_driver = None
        self.__behaviour_driver = None
        self.__deployment_location_driver = None
        self.__vim_driver_mgmt_driver = None
        self.__lifecycle_driver_mgmt_driver = None
        self.__resource_driver_mgmt_driver = None
        self.__resource_pkg_driver = None
        self.__infrastructure_keys_driver = None
        self.__descriptor_template_driver = None

    def __get_lm_security_ctrl(self):
        if self.env.is_secure:
            if not self.__lm_security_ctrl:
                self.__lm_security_ctrl = lm_drivers.LmSecurityCtrl(self.env.auth_address, self.username, self.password)
            return self.__lm_security_ctrl
        return None


    @property
    def descriptor_driver(self):
        """
        Obtain a LmDescriptorDriver configured for use against this LM environment

        Returns:
            LmDescriptorDriver: a configured DescriptorDriver for this LM environment
        """
        if not self.__descriptor_driver:
            self.__descriptor_driver = lm_drivers.LmDescriptorDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__descriptor_driver

    @property
    def onboard_rm_driver(self):
        """
        Obtain a LmOnboardRmDriver configured for use against this LM environment

        Returns:
            LmOnboardRmDriver: a configured LmOnboardRmDriver for this LM environment
        """
        if not self.__onboard_rm_driver:
            self.__onboard_rm_driver = lm_drivers.LmOnboardRmDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__onboard_rm_driver

    @property
    def topology_driver(self):
        """
        Obtain a LmTopologyDriver configured for use against this LM environment

        Returns:
            LmTopologyDriver: a configured LmTopologyDriver for this LM environment
        """
        if not self.__topology_driver:
            self.__topology_driver = lm_drivers.LmTopologyDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__topology_driver

    @property
    def behaviour_driver(self):
        """
        Obtain a LmBehaviourDriver configured for use against this LM environment

        Returns:
            LmBehaviourDriver: a configured LmBehaviourDriver for this LM environment
        """
        if not self.__behaviour_driver:
            self.__behaviour_driver = lm_drivers.LmBehaviourDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__behaviour_driver

    @property
    def deployment_location_driver(self):
        """
        Obtain a LmDeploymentLocationDriver configured for use against this LM environment

        Returns:
            LmDeploymentLocationDriver: a configured LmDeploymentLocationDriver for this LM environment
        """
        if not self.__deployment_location_driver:
            self.__deployment_location_driver = lm_drivers.LmDeploymentLocationDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__deployment_location_driver

    @property
    def resource_pkg_driver(self):
        """
        Obtain a LmResourcePkgDriver configured for use against this LM environment

        Returns:
            LmResourcePkgDriver: a configured LmResourcePkgDriver for this LM environment
        """
        if not self.__resource_pkg_driver:
            self.__resource_pkg_driver = lm_drivers.LmResourcePkgDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__resource_pkg_driver

    @property
    def resource_driver_mgmt_driver(self):
        """
        Obtain a LmResourceDriverMgmtDriver configured for use against this LM environment

        Returns:
            LmResourceDriverMgmtDriver: a configured LmResourceDriverMgmtDriver for this LM environment
        """
        if not self.__resource_driver_mgmt_driver:
            self.__resource_driver_mgmt_driver = lm_drivers.LmResourceDriverMgmtDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__resource_driver_mgmt_driver

    @property
    def vim_driver_mgmt_driver(self):
        """
        Obtain a LmVimDriverMgmtDriver configured for use against this LM environment

        Returns:
            LmVimDriverMgmtDriver: a configured LmVimDriverMgmtDriver for this LM environment
        """
        if not self.__vim_driver_mgmt_driver:
            self.__vim_driver_mgmt_driver = lm_drivers.LmVimDriverMgmtDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__vim_driver_mgmt_driver

    @property
    def lifecycle_driver_mgmt_driver(self):
        """
        Obtain a LmLifecycleDriverMgmtDriver configured for use against this LM environment

        Returns:
            LmLifecycleDriverMgmtDriver: a configured LmLifecycleDriverMgmtDriver for this LM environment
        """
        if not self.__lifecycle_driver_mgmt_driver:
            self.__lifecycle_driver_mgmt_driver = lm_drivers.LmLifecycleDriverMgmtDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__lifecycle_driver_mgmt_driver

    @property
    def infrastructure_keys_driver(self):
        """
        Obtain a LmInfrastructureKeysDriver configured for use against this LM environment

        Returns:
            LmInfrastructureKeysDriver: a configured LmInfrastructureKeysDriver for this LM environment
        """
        if not self.__infrastructure_keys_driver:
            self.__infrastructure_keys_driver = lm_drivers.LmInfrastructureKeysDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__infrastructure_keys_driver

    @property
    def descriptor_template_driver(self):
        """
        Obtain a LmDescriptorTemplatesDriver configured for use against this LM environment

        Returns:
            LmDescriptorTemplatesDriver: a configured LmDescriptorTemplatesDriver for this LM environment
        """
        if not self.__descriptor_template_driver:
            self.__descriptor_template_driver = lm_drivers.LmDescriptorTemplatesDriver(self.env.kami_address)
        return self.__descriptor_template_driver
