import lmctl.drivers.lm as lm_drivers
import logging
import os

from .common import build_address
from .auth_modes import (OAUTH_MODE, OAUTH_CLIENT_MODE, OAUTH_LEGACY_USER_MODE, OAUTH_USER_MODE, 
                         OKTA_CLIENT_MODE, OKTA_USER_MODE, NO_AUTH_MODE, ZEN_AUTH_MODE, CP_API_KEY_AUTH_MODE,
                         TOKEN_AUTH_MODE, OKTA_MODE,
                         is_no_auth_mode, is_oauth_mode, 
                         is_oauth_client_mode, is_oauth_user_mode, is_cp_api_key_mode, 
                         is_okta_mode, is_okta_client_mode, is_okta_user_mode, 
                         is_token_mode, is_oauth_legacy_user_mode)

from typing import Union, Optional
from urllib.parse import urlparse
from pydantic.dataclasses import dataclass
from pydantic import constr, root_validator

from lmctl.utils.jwt import decode_jwt
from lmctl.utils.dcutils.dc_capture import recordattrs
from lmctl.client import TNCOClientBuilder

logger = logging.getLogger(__name__)

ALLOW_ALL_SCHEMES_ENV_VAR = 'LMCTL_ALLOW_ALL_SCHEMES'

HTTP_PROTOCOL = 'http'
HTTPS_PROTOCOL = 'https'

DEFAULT_KAMI_PORT = '31289'
DEFAULT_KAMI_PROTOCOL = HTTP_PROTOCOL
DEFAULT_BRENT_NAME = 'brent'
DEFAULT_PROTOCOL = HTTPS_PROTOCOL
DEFAULT_SECURE = False

@recordattrs
@dataclass
class TNCOEnvironment:
    address: constr(strip_whitespace=True, min_length=1) = None
    name: str = None

    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    scope: Optional[str] = None
    auth_server_id: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    api_key: Optional[str] = None
    token: Optional[str] = None
    auth_mode: Optional[str] = NO_AUTH_MODE

    host: Optional[str] = None
    port: Optional[Union[str,int]] = None
    protocol: Optional[str] = DEFAULT_PROTOCOL
    path: Optional[str] = None

    auth_address: Optional[str] = None
    auth_host: Optional[str] = None
    auth_port: Optional[str] = None 
    auth_protocol: Optional[str] = DEFAULT_PROTOCOL 

    cp_front_door_address: Optional[str] = None
    cp_auth_endpoint: Optional[str] = None

    brent_name: Optional[str] = DEFAULT_BRENT_NAME
    kami_address: Optional[str] = None
    kami_port: Optional[Union[str,int]] = DEFAULT_KAMI_PORT 
    kami_protocol: Optional[str] = DEFAULT_KAMI_PROTOCOL

    # Not used but here to allow for constructor arg
    secure: bool = None

    @root_validator(pre=True)
    @classmethod
    def _assume_auth_mode_based_on_backwards_compatibility(cls, values):
        """
        Backwards compatibility for "secure" flag. 
        Previously the default value of "secure" was False.
        Previously when default value of "auth_mode" was "OAUTH_MODE" but that only applied when "secure=True". 
        
        Now, we want the default value of "auth_mode" to be "NO_AUTH_MODE", which matches the previous default of "secure=False". 

        However, to match the previous behaviour of "secure=True", we need to change the "auth_mode" default to "OAUTH_MODE" when we see "secure=True". 
        """
        if is_no_auth_mode(values.get('auth_mode', None)):
            secure = values.get('secure', DEFAULT_SECURE)
            if secure is True:
                values['auth_mode'] = OAUTH_MODE
            else:
                values['secure'] = False
        else:
            values['secure'] = True

        return values

    @root_validator(pre=True)
    @classmethod
    def normalize_addresses(cls, values):
        address = values.get('address', None)
        if address is None:
            host = values.get('host', None)
            host = host.strip() if host is not None else None
            if host:
                protocol = values.get('protocol', DEFAULT_PROTOCOL)
                port = values.get('port', None)
                path = values.get('path', None)
                values['address'] = build_address(host, protocol=protocol, port=port, path=path)
        
        if values.get('address', None) is None:
            raise ValueError('Invalid CP4NA environment - must specify "address" or "host" property')

        # Auth host
        auth_address = values.get('auth_address', None)
        if auth_address is None:
            auth_host = values.get('auth_host', None)
            auth_host = auth_host.strip() if auth_host is not None else None
            if auth_host:
                auth_protocol = values.get('auth_protocol', values.get('protocol', DEFAULT_PROTOCOL))
                auth_port = values.get('auth_port', None)
                auth_path = values.get('auth_path', None)
                values['auth_address'] = build_address(auth_host, protocol=auth_protocol, port=auth_port, path=auth_path)

        # Kami Address
        kami_address = values.get('kami_address', None)
        kami_port = values.get('kami_port', DEFAULT_KAMI_PORT)
        kami_protocol = values.get('kami_protocol', DEFAULT_KAMI_PROTOCOL)
        if kami_address is None:
            address = values.get('address', None)
            if address is not None:
                parsed_url = urlparse(address)

                if parsed_url.scheme is None or len(parsed_url.scheme.strip()) == 0:
                    parsed_url = urlparse(f'{HTTPS_PROTOCOL}://{address}')

                if parsed_url.port:
                    new_netloc = parsed_url.netloc.replace(f':{parsed_url.port}', f':{kami_port}')
                else:
                    new_netloc = f'{parsed_url.netloc}:{kami_port}'
                parsed_url = parsed_url._replace(scheme=kami_protocol, netloc=new_netloc, path='')
                kami_address = parsed_url.geturl()
                values['kami_address'] = kami_address

        return values

    def validate(self, allow_no_token: bool = False):
        """
        Validate the environment properties are set to allow for a client to be constructed against this environment.

        WARNING - the definition of valid includes empty/unset values for password, api_key and client_secret as we're not privy to the policy rules for those, 
        which, on the rare occassion, may include support for empty values
        """
        if not self.address:
            raise ValueError(f'Invalid CP4NA environment - must specify "address" property')
        
        if is_oauth_mode(self.auth_mode):
            self._validate_oauth()

        elif is_oauth_client_mode(self.auth_mode):
            self._validate_oauth_client()

        elif is_oauth_user_mode(self.auth_mode):
            self._validate_oauth_user()

        elif is_oauth_legacy_user_mode(self.auth_mode):
            self._validate_oauth_legacy_user()

        elif is_cp_api_key_mode(self.auth_mode):
            self._validate_cp_api_key()

        elif is_okta_mode(self.auth_mode):
            self._validate_okta()

        elif is_okta_user_mode(self.auth_mode):
            self._validate_okta_user()

        elif is_okta_client_mode(self.auth_mode):
            self._validate_okta_client()

        elif is_token_mode(self.auth_mode):
            self._validate_token(allow_no_token)

        elif is_no_auth_mode(self.auth_mode):
            pass

        else:
            raise ValueError(f'CP4NA environment configured with invalid "auth_mode": {self.auth_mode}')

    def _validate_oauth(self):
        if self.username:
            if self.client_id:
                return self._validate_oauth_user()
            else:
                return self._validate_oauth_legacy_user()
        elif self.client_id:
            return self._validate_oauth_client()
        else:
            raise ValueError(f'Invalid CP4NA environment - must configure "username" or "client_id" when using "auth_mode={OAUTH_MODE}"')
        
    def _validate_oauth_user(self):
        if not self.username:
            raise ValueError(f'Invalid CP4NA environment - must configure "username" when using "auth_mode={OAUTH_USER_MODE}"')

        if not self.client_id:
            raise ValueError(f'Invalid CP4NA environment - must configure "client_id" when using "auth_mode={OAUTH_USER_MODE}"')

    def _validate_oauth_legacy_user(self):
        if not self.username:
            raise ValueError(f'Invalid CP4NA environment - must configure "username" when using "auth_mode={OAUTH_LEGACY_USER_MODE}"')

    def _validate_oauth_client(self):
        if not self.client_id:
            raise ValueError(f'Invalid CP4NA environment - must configure "client_id" when using "auth_mode={OAUTH_CLIENT_MODE}"')

    def _validate_okta(self):
        if self.client_id:
            if self.username:
                self._validate_okta_user()
            else:
                self._validate_okta_client()
        else:
            raise ValueError(f'Invalid CP4NA environment - must configure "username" and/or "client_id" when using "auth_mode={OKTA_MODE}"')
    
    def _validate_okta_user(self):
        if not self.client_id:
            raise ValueError(f'Invalid CP4NA environment - must configure "client_id" when using "auth_mode={OKTA_USER_MODE}"')
        if not self.username:
            raise ValueError(f'Invalid CP4NA environment - must configure "username" when using "auth_mode={OKTA_USER_MODE}"')
        if not self.auth_server_id:
            raise ValueError(f'Invalid CP4NA environment - must configure "auth_server_id" when using "auth_mode={OKTA_USER_MODE}"')
        if not self.scope:
            raise ValueError(f'Invalid CP4NA environment - must configure "scope" when using "auth_mode={OKTA_USER_MODE}"')

    def _validate_okta_client(self):
        if not self.client_id:
            raise ValueError(f'Invalid CP4NA environment - must configure "client_id" when using "auth_mode={OKTA_CLIENT_MODE}"')
        if not self.auth_server_id:
            raise ValueError(f'Invalid CP4NA environment - must configure "auth_server_id" when using "auth_mode={OKTA_CLIENT_MODE}"')
        if not self.scope:
            raise ValueError(f'Invalid CP4NA environment - must configure "scope" when using "auth_mode={OKTA_CLIENT_MODE}"')
        
    def _validate_cp_api_key(self):
        # Report "ZEN_AUTH_MODE" in the error if that alias was used instead of "CP_API_KEY_AUTH_MODE"
        auth_mode_for_error = CP_API_KEY_AUTH_MODE if self.auth_mode != ZEN_AUTH_MODE else ZEN_AUTH_MODE 
        
        if not self.username:
            raise ValueError(f'Invalid CP4NA environment - must configure "username" when using "auth_mode={auth_mode_for_error}"')

    def _validate_token(self, allow_no_token: bool):
        if not self.token and not allow_no_token:
            raise ValueError(f'Invalid CP4NA environment - must configure "token" when using "auth_mode={TOKEN_AUTH_MODE}"')
        
    def create_session(self):
        return LmSession(self)
    
    def build_client(self):
        self.validate()

        builder = TNCOClientBuilder()
        builder.address(self.get_usable_address())
        if self.kami_address:
            builder.kami_address(self.kami_address)

        if is_oauth_mode(self.auth_mode):
            if self.username:
                if self.client_id:
                    self._add_oauth_user(builder)
                else:
                    self._add_oauth_legacy_user(builder)
            else:
                self._add_oauth_client(builder)

        elif is_oauth_client_mode(self.auth_mode):
            self._add_oauth_client(builder)
        
        elif is_oauth_user_mode(self.auth_mode):
            self._add_oauth_user(builder)

        elif is_oauth_legacy_user_mode(self.auth_mode):
            self._add_oauth_legacy_user(builder)

        elif is_cp_api_key_mode(self.auth_mode):
            zen_address = self.get_usable_cp_front_door_address()
            if zen_address is None and self.auth_address:
                # Backward compatibility support for using "auth_address" which may have the authorise path already appended to it (Zen Auth handler deals with this)
                zen_address = self._finalise_address(self.auth_address)
            builder.zen_api_key_auth(username=self.username, api_key=self.api_key, zen_auth_address=zen_address, override_auth_endpoint=self.cp_auth_endpoint)

        elif is_okta_mode(self.auth_mode):
            if self.username and self.client_id:
                self._add_okta_user(builder)
            else:
                self._add_okta_client(builder)

        elif is_okta_user_mode(self.auth_mode):
            self._add_okta_user(builder)

        elif is_okta_client_mode(self.auth_mode):
            self._add_okta_client(builder)

        elif is_token_mode(self.auth_mode):
            builder.token_auth(token=self.token)

        return builder.build()
    
    def get_usable_address(self):
        return self._finalise_address(self.address)
    
    def get_usable_cp_front_door_address(self):
        if self.cp_front_door_address:
            return self._finalise_address(self.cp_front_door_address)
        else: 
            return None
    
    def get_usable_oauth_legacy_user_address(self):
        if self.auth_address:
            return self._finalise_address(self.auth_address)
        else:
            return None
        
    def get_usable_okta_address(self):
        if self.auth_address:
            return self._finalise_address(self.auth_address)
        else:
            return None
    
    def _add_oauth_user(self, builder: TNCOClientBuilder):
        builder.user_pass_auth(username=self.username, password=self.password, client_id=self.client_id, client_secret=self.client_secret)

    def _add_oauth_client(self, builder: TNCOClientBuilder):
        builder.client_credentials_auth(client_id=self.client_id, client_secret=self.client_secret)
    
    def _add_oauth_legacy_user(self, builder: TNCOClientBuilder):
        builder.legacy_user_pass_auth(username=self.username, password=self.password, legacy_auth_address=self.get_usable_oauth_legacy_user_address())

    def _add_okta_user(self, builder: TNCOClientBuilder):
        builder.okta_user_pass_auth(username=self.username, 
                                    password=self.password,
                                    client_id=self.client_id,
                                    client_secret=self.client_secret,
                                    scope=self.scope, 
                                    auth_server_id=self.auth_server_id,
                                    okta_server=self.get_usable_okta_address())

    def _add_okta_client(self, builder: TNCOClientBuilder):
        builder.okta_client_credentials_auth(client_id=self.client_id,
                                            client_secret=self.client_secret,
                                            scope=self.scope, 
                                            auth_server_id=self.auth_server_id,
                                            okta_server=self.get_usable_okta_address())
        
        
    def _finalise_address(self, address):
        parsed_url = urlparse(address)

        if parsed_url.scheme is None or len(parsed_url.scheme.strip()) == 0:
            logger.debug(f'Adding "{HTTPS_PROTOCOL}://" to {address}')
            return f'{HTTPS_PROTOCOL}://{address}'
        elif parsed_url.scheme != HTTPS_PROTOCOL:
            allow_all_schemes = os.environ.get(ALLOW_ALL_SCHEMES_ENV_VAR, None)
            if allow_all_schemes is None or allow_all_schemes.lower() != 'true':
                raise ValueError(f'Use of "{parsed_url.scheme}" scheme is not encouraged by lmctl, use "{HTTPS_PROTOCOL}" instead ({address})')

        return address

    @property
    def api_address(self):
        return self.get_usable_address()

    def summarise_user(self) -> str:
        if self.token is not None and len(self.token.strip()) > 0:
            try:
                decoded_token = decode_jwt(self.token)
                return decoded_token.get('username', '<No user on token>')
            except ValueError as e:
                return '<Invalid Token>'
        else:
            user_str = ''
            if self.username is not None and len(self.username.strip()) > 0:
                user_str += self.username
            if self.client_id is not None and len(self.client_id.strip()) > 0:
                client_str = f'{self.client_id} (Client)'
                if len(user_str) > 0:
                    user_str += f', {client_str}'
                else:
                    user_str = client_str

            return user_str
        
    def is_using_no_auth(self):
        return is_no_auth_mode(self.auth_mode)
    
    def is_using_okta_auth(self):
        return is_okta_mode(self.auth_mode)
    
    def is_using_ambigious_okta_auth(self):
        if is_okta_mode(self.auth_mode):
            if not self.is_using_okta_user_auth() and not self.is_using_okta_client_auth():
                return True
        
        return False

    
    def is_using_okta_user_auth(self):
        return is_okta_user_mode(self.auth_mode) or (is_okta_mode(self.auth_mode) and self.username and not self.client_id)
    
    def is_using_okta_client_auth(self):
        return is_okta_client_mode(self.auth_mode) or (is_okta_mode(self.auth_mode) and self.client_id and not self.username)
    
    def is_using_oauth_user_auth(self):
        return is_oauth_user_mode(self.auth_mode)
    
    def is_using_oauth_client_auth(self):
        return is_oauth_client_mode(self.auth_mode)
    
    def is_using_oauth_legacy_user_auth(self):
        return is_oauth_legacy_user_mode(self.auth_mode)
    
    def is_using_cp_api_key_auth(self):
        return is_cp_api_key_mode(self.auth_mode)
    
    def is_using_token_auth(self):
        return is_token_mode(self.auth_mode)

class LmSession:

    def __init__(self, env):
        if not env:
            raise ValueError('config not provided to session')
        self.env = env
        self.env.validate()
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
        if not self.env.is_using_no_auth():
            if not self.__lm_security_ctrl:
                self.__lm_security_ctrl = lm_drivers.LmSecurityCtrl(self.env)
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
            self.__descriptor_driver = lm_drivers.LmDescriptorDriver(self.env.get_usable_address(), self.__get_lm_security_ctrl())
        return self.__descriptor_driver

    @property
    def onboard_rm_driver(self):
        """
        Obtain a LmOnboardRmDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmOnboardRmDriver: a configured LmOnboardRmDriver for this CP4NA orchestration environment
        """
        if not self.__onboard_rm_driver:
            self.__onboard_rm_driver = lm_drivers.LmOnboardRmDriver(self.env.get_usable_address(), self.__get_lm_security_ctrl())
        return self.__onboard_rm_driver

    @property
    def topology_driver(self):
        """
        Obtain a LmTopologyDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmTopologyDriver: a configured LmTopologyDriver for this CP4NA orchestration environment
        """
        if not self.__topology_driver:
            self.__topology_driver = lm_drivers.LmTopologyDriver(self.env.get_usable_address(), self.__get_lm_security_ctrl())
        return self.__topology_driver

    @property
    def behaviour_driver(self):
        """
        Obtain a LmBehaviourDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmBehaviourDriver: a configured LmBehaviourDriver for this CP4NA orchestration environment
        """
        if not self.__behaviour_driver:
            self.__behaviour_driver = lm_drivers.LmBehaviourDriver(self.env.get_usable_address(), self.__get_lm_security_ctrl())
        return self.__behaviour_driver

    @property
    def deployment_location_driver(self):
        """
        Obtain a LmDeploymentLocationDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmDeploymentLocationDriver: a configured LmDeploymentLocationDriver for this CP4NA orchestration environment
        """
        if not self.__deployment_location_driver:
            self.__deployment_location_driver = lm_drivers.LmDeploymentLocationDriver(self.env.get_usable_address(), self.__get_lm_security_ctrl())
        return self.__deployment_location_driver

    @property
    def resource_pkg_driver(self):
        """
        Obtain a LmResourcePkgDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmResourcePkgDriver: a configured LmResourcePkgDriver for this CP4NA orchestration environment
        """
        if not self.__resource_pkg_driver:
            self.__resource_pkg_driver = lm_drivers.LmResourcePkgDriver(self.env.get_usable_address(), self.__get_lm_security_ctrl())
        return self.__resource_pkg_driver

    @property
    def pkg_mgmt_driver(self):
        """
        Obtain a EtsiPackageMgmtDriver configured for use against this CP4NA orchestration environment

        Returns:
            EtsiPackageMgmtDriver: a configured EtsiPackageMgmtDriver for this CP4NA orchestration environment
        """
        if not self.__pkg_mgmt_driver:
            self.__pkg_mgmt_driver = lm_drivers.EtsiPackageMgmtDriver(self.env.get_usable_address(), self.__get_lm_security_ctrl())
        return self.__pkg_mgmt_driver        

    @property
    def resource_driver_mgmt_driver(self):
        """
        Obtain a LmResourceDriverMgmtDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmResourceDriverMgmtDriver: a configured LmResourceDriverMgmtDriver for this CP4NA orchestration environment
        """
        if not self.__resource_driver_mgmt_driver:
            self.__resource_driver_mgmt_driver = lm_drivers.LmResourceDriverMgmtDriver(self.env.get_usable_address(), self.__get_lm_security_ctrl())
        return self.__resource_driver_mgmt_driver

    @property
    def vim_driver_mgmt_driver(self):
        """
        Obtain a LmVimDriverMgmtDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmVimDriverMgmtDriver: a configured LmVimDriverMgmtDriver for this CP4NA orchestration environment
        """
        if not self.__vim_driver_mgmt_driver:
            self.__vim_driver_mgmt_driver = lm_drivers.LmVimDriverMgmtDriver(self.env.get_usable_address(), self.__get_lm_security_ctrl())
        return self.__vim_driver_mgmt_driver

    @property
    def lifecycle_driver_mgmt_driver(self):
        """
        Obtain a LmLifecycleDriverMgmtDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmLifecycleDriverMgmtDriver: a configured LmLifecycleDriverMgmtDriver for this CP4NA orchestration environment
        """
        if not self.__lifecycle_driver_mgmt_driver:
            self.__lifecycle_driver_mgmt_driver = lm_drivers.LmLifecycleDriverMgmtDriver(self.env.get_usable_address(), self.__get_lm_security_ctrl())
        return self.__lifecycle_driver_mgmt_driver

    @property
    def infrastructure_keys_driver(self):
        """
        Obtain a LmInfrastructureKeysDriver configured for use against this CP4NA orchestration environment

        Returns:
            LmInfrastructureKeysDriver: a configured LmInfrastructureKeysDriver for this CP4NA orchestration environment
        """
        if not self.__infrastructure_keys_driver:
            self.__infrastructure_keys_driver = lm_drivers.LmInfrastructureKeysDriver(self.env.get_usable_address(), self.__get_lm_security_ctrl())
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