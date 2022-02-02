import lmctl.drivers.lm as lm_drivers
from typing import Union, Optional
from .common import build_address
from urllib.parse import urlparse
from lmctl.client import TNCOClient, TNCOClientBuilder, TOKEN_AUTH_MODE, ZEN_AUTH_MODE, OAUTH_MODE
from pydantic.dataclasses import dataclass
from pydantic import constr, root_validator
from lmctl.utils.dcutils.dc_capture import recordattrs

DEFAULT_KAMI_PORT = '31289'
DEFAULT_KAMI_PROTOCOL = 'http'
DEFAULT_BRENT_NAME = 'brent'
DEFAULT_PROTOCOL = 'https'
DEFAULT_SECURE = False

@recordattrs
@dataclass
class TNCOEnvironment:
    address: constr(strip_whitespace=True, min_length=1) = None
    name: str = None
    secure: bool = DEFAULT_SECURE

    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    username: Optional[str] = None 
    password: Optional[str] = None
    api_key: Optional[str] = None
    token: Optional[str] = None
    auth_mode: Optional[str] = OAUTH_MODE

    host: Optional[str] = None
    port: Optional[Union[str,int]] = None
    protocol: Optional[str] = DEFAULT_PROTOCOL
    path: Optional[str] = None

    auth_address: Optional[str] = None
    auth_host: Optional[str] = None
    auth_port: Optional[str] = None 
    auth_protocol: Optional[str] = DEFAULT_PROTOCOL 

    brent_name: Optional[str] = DEFAULT_BRENT_NAME
    kami_address: Optional[str] = None
    kami_port: Optional[Union[str,int]] = DEFAULT_KAMI_PORT 
    kami_protocol: Optional[str] = DEFAULT_KAMI_PROTOCOL

    @root_validator(pre=True)
    @classmethod
    def check_security(cls, values):
        secure = values.get('secure', DEFAULT_SECURE)
        if secure is True:

            auth_mode = values.get('auth_mode', None)
            if auth_mode is None:
                auth_mode = OAUTH_MODE
                values['auth_mode'] = auth_mode

            if auth_mode.lower() == OAUTH_MODE:
                values = cls._validate_oauth(values)
            elif auth_mode.lower() == ZEN_AUTH_MODE:
                values = cls._validate_zen(values)
            elif auth_mode.lower() == TOKEN_AUTH_MODE:
                pass
            else:
                raise ValueError(f'TNCO environment configured with invalid "auth_mode": {auth_mode}')

        return values

    @classmethod
    def _validate_oauth(cls, values):
        client_id = values.get('client_id', None)
        client_secret = values.get('client_secret', None)
        username = values.get('username', None)
        password = values.get('password', None)
        if not client_id and not username:
            raise ValueError(f'Secure TNCO environment must be configured with either "client_id" or "username" property when using "auth_mode={OAUTH_MODE}". If the TNCO environment is not secure then set "secure" to False')
        # Currently api_key can only be used with Zen, so we perform an extra check to let the user know 
        api_key = values.get('api_key', None)
        if api_key is not None:
            raise ValueError(f'Secure TNCO environment cannot be configured with "api_key" when using "auth_mode={OAUTH_MODE}". Use "client_id/client_secret" or "username/password" combination or set "auth_mode" to "{ZEN_AUTH_MODE}". If the TNCO environment is not secure then set "secure" to False')
        return values

    @classmethod
    def _validate_zen(cls, values):
        username = values.get('username', None)
        if not username:
            raise ValueError(f'Secure TNCO environment must be configured with a "username" property when using "auth_mode={ZEN_AUTH_MODE}". If the TNCO environment is not secure then set "secure" to False')
        # Zen auth address must be provided
        auth_address = values.get('auth_address', None)
        auth_host = values.get('auth_host', None)
        if not auth_address and not auth_host:
            raise ValueError(f'Secure TNCO environment must be configured with Zen authentication address on the "auth_address" property (or "auth_host"/"auth_port"/"auth_protocol") when using "auth_mode={ZEN_AUTH_MODE}". If the TNCO environment is not secure then set "secure" to False')
        return values

    @root_validator(pre=True)
    @classmethod
    def normalize_addresses(cls, values):
        auth_mode = values.get('auth_mode', None)
        address = values.get('address', None)
        if address is None:
            host = values.get('host', None)
            host = host.strip() if host is not None else None
            if not host:
                raise ValueError('TNCO environment cannot be configured without "address" property or "host" property')
            protocol = values.get('protocol', DEFAULT_PROTOCOL)
            port = values.get('port', None)
            path = values.get('path', None)
            address = build_address(host, protocol=protocol, port=port, path=path)
            values['address'] = address

        # Auth host
        auth_address = values.get('auth_address', None)
        if auth_address is None and (auth_mode is None or auth_mode.lower() != TOKEN_AUTH_MODE):
            auth_host = values.get('auth_host', None)
            auth_host = auth_host.strip() if auth_host is not None else None
            if not auth_host:
                values['auth_address'] = address
            else:
                auth_protocol = values.get('auth_protocol', values.get('protocol', DEFAULT_PROTOCOL))
                auth_port = values.get('auth_port', None)
                auth_path = values.get('auth_path', None)
                auth_address = build_address(auth_host, protocol=auth_protocol, port=auth_port)
                values['auth_address'] = auth_address

        # Kami Address
        kami_address = values.get('kami_address', None)
        kami_port = values.get('kami_port', DEFAULT_KAMI_PORT)
        kami_protocol = values.get('kami_protocol', DEFAULT_KAMI_PROTOCOL)
        if kami_address is None:
            parsed_url = urlparse(address)
            if parsed_url.port:
                new_netloc = parsed_url.netloc.replace(f':{parsed_url.port}', f':{kami_port}')
            else:
                new_netloc = f'{parsed_url.netloc}:{kami_port}'
            parsed_url = parsed_url._replace(scheme=kami_protocol, netloc=new_netloc, path='')
            kami_address = parsed_url.geturl()
            values['kami_address'] = kami_address

        return values

    def create_session_config(self):
        return LmSessionConfig(self, 
                                username=self.username, 
                                password=self.password, 
                                client_id=self.client_id, 
                                client_secret=self.client_secret, 
                                api_key=self.api_key,
                                token=self.token,
                                auth_mode=self.auth_mode
                            )
    def build_client(self):
        builder = TNCOClientBuilder()
        builder.address(self.address)
        builder.kami_address(self.kami_address)
        if self.secure:
            if self.auth_mode == ZEN_AUTH_MODE:
                builder.zen_api_key_auth(username=self.username, api_key=self.api_key, zen_auth_address=self.auth_address)
            elif self.auth_mode == TOKEN_AUTH_MODE:
                builder.token_auth(token=self.token)
            else:
                if self.username is not None:
                    # Using password auth
                    if self.client_id is not None:
                        builder.user_pass_auth(username=self.username, password=self.password, client_id=self.client_id, client_secret=self.client_secret)
                    else:
                        # Legacy password auth
                        builder.legacy_user_pass_auth(username=self.username, password=self.password, legacy_auth_address=self.auth_address)
                else:
                    builder.client_credentials_auth(client_id=self.client_id, client_secret=self.client_secret)
        return builder.build()

    @property
    def api_address(self):
        return self.address

    @property
    def is_using_oauth(self):
        return self.auth_mode.lower() == OAUTH_MODE.lower()

    @property
    def is_using_zen_auth(self):
        return self.auth_mode.lower() == ZEN_AUTH_MODE.lower()
    
    @property
    def is_using_token_auth(self):
        return self.auth_mode.lower() == TOKEN_AUTH_MODE.lower()

class LmSessionConfig:

    def __init__(self, env, username=None, password=None, client_id=None, client_secret=None, token=None, api_key=None, auth_mode=None):
        self.env = env
        self.username = username
        self.password = password
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_key = api_key
        self.token = token
        self.auth_mode = auth_mode

    @property
    def is_using_oauth(self):
        return self.auth_mode.lower() == OAUTH_MODE.lower()

    @property
    def is_using_zen_auth(self):
        return self.auth_mode.lower() == ZEN_AUTH_MODE.lower()
    
    @property
    def is_using_token_auth(self):
        return self.auth_mode.lower() == TOKEN_AUTH_MODE.lower()

    def create(self):
        return LmSession(self)

class LmSession:

    def __init__(self, session_config):
        if not session_config:
            raise ValueError('config not provided to session')
        self.env = session_config.env
        self.client_id = session_config.client_id
        self.client_secret = session_config.client_secret
        self.username = session_config.username
        self.password = session_config.password
        self.api_key = session_config.api_key
        self.token = session_config.token
        self.auth_mode = session_config.auth_mode
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
        self.__pkg_mgmt_driver = None
        self.__infrastructure_keys_driver = None
        self.__descriptor_template_driver = None

    def __get_lm_security_ctrl(self):
        if self.env.secure:
            if not self.__lm_security_ctrl:
                self.__lm_security_ctrl = lm_drivers.LmSecurityCtrl(self.env.auth_address, 
                                                                    username=self.username, 
                                                                    password=self.password,
                                                                    client_id=self.client_id, 
                                                                    client_secret=self.client_secret,
                                                                    api_key=self.api_key,
                                                                    token=self.token,
                                                                    auth_mode=self.auth_mode
                                                                )
            return self.__lm_security_ctrl
        return None


    @property
    def descriptor_driver(self):
        """
        Obtain a LmDescriptorDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmDescriptorDriver: a configured DescriptorDriver for this CP4NA orchestration environment
        """
        if not self.__descriptor_driver:
            self.__descriptor_driver = lm_drivers.LmDescriptorDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__descriptor_driver

    @property
    def onboard_rm_driver(self):
        """
        Obtain a LmOnboardRmDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmOnboardRmDriver: a configured LmOnboardRmDriver for this CP4NA orchestration environment
        """
        if not self.__onboard_rm_driver:
            self.__onboard_rm_driver = lm_drivers.LmOnboardRmDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__onboard_rm_driver

    @property
    def topology_driver(self):
        """
        Obtain a LmTopologyDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmTopologyDriver: a configured LmTopologyDriver for this CP4NA orchestration environment
        """
        if not self.__topology_driver:
            self.__topology_driver = lm_drivers.LmTopologyDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__topology_driver

    @property
    def behaviour_driver(self):
        """
        Obtain a LmBehaviourDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmBehaviourDriver: a configured LmBehaviourDriver for this CP4NA orchestration environment
        """
        if not self.__behaviour_driver:
            self.__behaviour_driver = lm_drivers.LmBehaviourDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__behaviour_driver

    @property
    def deployment_location_driver(self):
        """
        Obtain a LmDeploymentLocationDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmDeploymentLocationDriver: a configured LmDeploymentLocationDriver for this CP4NA orchestration environment
        """
        if not self.__deployment_location_driver:
            self.__deployment_location_driver = lm_drivers.LmDeploymentLocationDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__deployment_location_driver

    @property
    def resource_pkg_driver(self):
        """
        Obtain a LmResourcePkgDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmResourcePkgDriver: a configured LmResourcePkgDriver for this CP4NA orchestration environment
        """
        if not self.__resource_pkg_driver:
            self.__resource_pkg_driver = lm_drivers.LmResourcePkgDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__resource_pkg_driver

    @property
    def pkg_mgmt_driver(self):
        """
        Obtain a EtsiPackageMgmtDriver configured for use against this CP4NA orchestration environment

        Returns:
            EtsiPackageMgmtDriver: a configured EtsiPackageMgmtDriver for this CP4NA orchestration environment
        """
        if not self.__pkg_mgmt_driver:
            self.__pkg_mgmt_driver = lm_drivers.EtsiPackageMgmtDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__pkg_mgmt_driver        

    @property
    def resource_driver_mgmt_driver(self):
        """
        Obtain a LmResourceDriverMgmtDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmResourceDriverMgmtDriver: a configured LmResourceDriverMgmtDriver for this CP4NA orchestration environment
        """
        if not self.__resource_driver_mgmt_driver:
            self.__resource_driver_mgmt_driver = lm_drivers.LmResourceDriverMgmtDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__resource_driver_mgmt_driver

    @property
    def vim_driver_mgmt_driver(self):
        """
        Obtain a LmVimDriverMgmtDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmVimDriverMgmtDriver: a configured LmVimDriverMgmtDriver for this CP4NA orchestration environment
        """
        if not self.__vim_driver_mgmt_driver:
            self.__vim_driver_mgmt_driver = lm_drivers.LmVimDriverMgmtDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__vim_driver_mgmt_driver

    @property
    def lifecycle_driver_mgmt_driver(self):
        """
        Obtain a LmLifecycleDriverMgmtDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmLifecycleDriverMgmtDriver: a configured LmLifecycleDriverMgmtDriver for this CP4NA orchestration environment
        """
        if not self.__lifecycle_driver_mgmt_driver:
            self.__lifecycle_driver_mgmt_driver = lm_drivers.LmLifecycleDriverMgmtDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__lifecycle_driver_mgmt_driver

    @property
    def infrastructure_keys_driver(self):
        """
        Obtain a LmInfrastructureKeysDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmInfrastructureKeysDriver: a configured LmInfrastructureKeysDriver for this CP4NA orchestration environment
        """
        if not self.__infrastructure_keys_driver:
            self.__infrastructure_keys_driver = lm_drivers.LmInfrastructureKeysDriver(self.env.api_address, self.__get_lm_security_ctrl())
        return self.__infrastructure_keys_driver

    @property
    def descriptor_template_driver(self):
        """
        Obtain a LmDescriptorTemplatesDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmDescriptorTemplatesDriver: a configured LmDescriptorTemplatesDriver for this CP4NA orchestration environment
        """
        if not self.__descriptor_template_driver:
            self.__descriptor_template_driver = lm_drivers.LmDescriptorTemplatesDriver(self.env.kami_address)
        return self.__descriptor_template_driver

LmEnvironment = TNCOEnvironment