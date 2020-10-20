from typing import Union
from .common import Environment, EnvironmentConfigError, EnvironmentRuntimeError, build_address
from urllib.parse import urlparse
import lmctl.drivers.lm as lm_drivers

KAMI_PORT = '31289'
DEFAULT_BRENT_NAME = 'brent'

class LmEnvironment(Environment):

    def __init__(self, name, 
                       host: str = None, 
                       port: Union[str,int] = None,
                       protocol: str = 'https', 
                       path: str = None, 
                       address: str = None,
                       secure: bool = False,
                       client_id: str = None,
                       client_secret: str = None,
                       username: str = None, 
                       password: str= None, 
                       auth_address: str = None,
                       auth_host: str = None, 
                       auth_port: str = None, 
                       auth_protocol: str = None, 
                       brent_name: str = DEFAULT_BRENT_NAME, 
                       kami_address: str = None,
                       kami_port: Union[str,int] = KAMI_PORT, 
                       kami_protocol: str = 'http'):
        name = name.strip() if name is not None else None
        if not name:
            raise EnvironmentConfigError('LM environment cannot be configured without "name" property')
        self.name = name
        self._read_addresses(
            address=address,
            host=host, 
            port=port,
            protocol=protocol,
            path=path,
            auth_address=auth_address,
            auth_host=auth_host,
            auth_port=auth_port,
            auth_protocol=auth_protocol, 
            kami_address=kami_address,
            kami_port=kami_port, 
            kami_protocol=kami_protocol
        )
        if brent_name is None or len(brent_name.strip()) == 0:
            brent_name = DEFAULT_BRENT_NAME
        self.brent_name = brent_name.strip()
        self.secure = secure
        self._read_security(client_id=client_id, client_secret=client_secret, username=username, password=password)

    def _read_security(self, client_id: str = None,
                             client_secret: str = None,
                             username: str = None,
                             password: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        if self.secure and not self.client_id and not self.username:
            raise EnvironmentConfigError('Secure LM environment cannot be configured without "client_id" or "username" property. If the LM environment is not secure then set "secure" to False')
            
    def _read_addresses(self, address: str = None, 
                              protocol: str = 'https', 
                              host: str = None, 
                              port: Union[str, int] = None, 
                              path: str = None, 
                              auth_address: str = None,
                              auth_host: str = None,
                              auth_port: str = None,
                              auth_protocol: str = None, 
                              kami_address: str = None,
                              kami_port: Union[str,int] = KAMI_PORT, 
                              kami_protocol: str = 'http'):
        if address is not None:
            self._address = address
        else:
            host = host.strip() if host is not None else None
            if not host:
                raise EnvironmentConfigError('LM environment cannot be configured without "address" property or "host" property')
            self._address = build_address(host, protocol=protocol, port=port, path=path)
        #Auth host
        if auth_address is not None:
            self.auth_address = auth_address
        else:
            auth_host = auth_host.strip() if auth_host is not None else None
            if auth_host:
                self.auth_address = build_address(auth_host, protocol=(auth_protocol or protocol), port=auth_port)
            else:
                self.auth_address = self._address
        self.auth_address = self.auth_address
        #Kami Address
        if kami_address is None:
            parsed_url = urlparse(self._address)
            if parsed_url.port:
                new_netloc = parsed_url.netloc.replace(f':{parsed_url.port}', f':{kami_port}')
            else:
                new_netloc = f'{parsed_url.netloc}:{kami_port}'
            parsed_url = parsed_url._replace(scheme=kami_protocol, netloc=new_netloc, path='')
            self.kami_address = parsed_url.geturl()
        else:
            self.kami_address = kami_address

    def create_session_config(self):
        return LmSessionConfig(self, self.username, self.password)

    @property
    def is_secure(self):
        return self.secure

    @property
    def address(self):
        return self._address

    @property
    def api_address(self):
        return self._address

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
