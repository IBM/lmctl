import logging
import lmctllib.drivers.arm as arm_drivers
import lmctllib.drivers.lm as lm_drivers

logger = logging.getLogger(__name__)

class Environment:
    """
    Handles configuration of an Lmctl environment
    """
    def __init__(self, env_name, description, lm_env, arm_envs):
        self.name = env_name
        self.description = description
        self.lm = lm_env
        self.arms = arm_envs

    def getArm(self, arm_name):
        """
        Helper method to retrieve an Ansible RM environment by name

        Returns:
          ArmEnvironment: the ArmEnvironment for the Ansible RM known by the given name
        """
        if arm_name in self.arms:
            return self.arms[arm_name]
        else:
            raise ValueError('No ARM named {0} on environment {1}'.format(arm_name, self.name))
        
class ArmEnvironment:
    """
    Holds configuration of a target Ansible RM environment
    """
    def __init__(self, arm_name, arm_env):
        self.name = arm_name
        self.arm_driver = None
        if 'ip_address' not in arm_env:
            raise ValueError('Environment arm config missing ip_address')
        if 'port' not in arm_env:
            raise ValueError('Environment arm config missing port')
        self.ip_address = arm_env['ip_address']
        self.port = arm_env['port']
        if 'secure_port' in arm_env:
            self.secure_port = arm_env['secure_port']
        else:
            self.secure_port = False
        if 'onboarding_addr' in arm_env:
            self.onboarding_addr = arm_env['onboarding_addr']
        else:
            self.onboarding_addr = None

    def __armBase(self):
        protocol = 'http'
        if self.secure_port:
            protocol = 'https'
        return '{0}://{1}:{2}'.format(protocol, self.ip_address, self.port)

    def getUrl(self):
        return self.__armBase()

    def getOnboardingUrl(self):
        if self.onboarding_addr is not None:
            return self.onboarding_addr
        else:
            return self.__armBase()

    def getArmDriver(self):
        if not self.arm_driver:
            self.arm_driver = arm_drivers.AnsibleRmDriver(self.__armBase())   
        return self.arm_driver

class LmEnvironment:
    """
    Holds configuration of a target Lifecycle Manager environment
    """
    def __init__(self, alm_env):
        self.__lm_security_ctrl = None
        self.__descriptor_driver = None
        self.__onboard_rm_driver = None
        self.__topology_driver = None
        self.__behaviour_driver = None

        if 'ip_address' not in alm_env:
            raise ValueError('Environment alm config missing ip_address')
        if 'port' not in alm_env:
            raise ValueError('Environment alm config missing port')

        self.ip_address = alm_env['ip_address']
        self.port = alm_env['port']
        if 'secure_port' in alm_env:
            self.secure_port = alm_env['secure_port']
        else:
            self.secure_port = False

        if 'username' in alm_env:
            self.username = alm_env['username']
            if 'auth_address' not in alm_env:
                raise ValueError('Environment alm config missing auth_address (must be set when a username is provided)')
            self.auth_address = alm_env['auth_address']
            if 'auth_port' not in alm_env:
                self.auth_port = self.port
            else:
                self.auth_port = alm_env['auth_port']
            if 'password' in alm_env:
                pwd = alm_env['password']
                if pwd is None:
                    pwd = ""
                self.password = pwd
            else:
                self.password = None
        else:
            self.username = None
            self.auth_address = None
            self.auth_port = None
            self.password = None

    def requiresAuthentication(self):
        """
        Returns True if the configuration of the LM environment indicates that it is a secured one (i.e. a username has been specified)

        Returns:
            bool: True if the configuration of the LM environment indicates that it is a secured one
        """
        if self.username:
            return True
        else:
            return False

    def getUrl(self):
        """
        Returns the URL configured for this LM environment

        Returns:
            str: the URL configured for this LM environment
        """
        return self.__lmBase()

    def __lmBase(self):
        protocol = 'http'
        if self.secure_port:
            protocol = 'https'
        return '{0}://{1}:{2}'.format(protocol, self.ip_address, self.port)

    def __authBase(self):
        protocol = 'http'
        if self.secure_port:
            protocol = 'https'
        return '{0}://{1}:{2}'.format(protocol, self.auth_address, self.auth_port)

    def __lmSecurityCtrl(self):
        if self.requiresAuthentication():
            if not self.__lm_security_ctrl:
                self.__lm_security_ctrl = lm_drivers.LmSecurityCtrl(self.__authBase(), self.username, self.password)
            return self.__lm_security_ctrl
        return None

    def getDescriptorDriver(self):
        """
        Obtain a LmDescriptorDriver configured for use against this LM environment

        Returns:
            LmDescriptorDriver: a configured DescriptorDriver for this LM environment
        """
        if not self.__descriptor_driver:
            self.__descriptor_driver = lm_drivers.LmDescriptorDriver(self.__lmBase(), self.__lmSecurityCtrl())   
        return self.__descriptor_driver

    def getOnboardRmDriver(self):
        """
        Obtain a LmOnboardRmDriver configured for use against this LM environment

        Returns:
            LmOnboardRmDriver: a configured LmOnboardRmDriver for this LM environment
        """
        if not self.__onboard_rm_driver:
            self.__onboard_rm_driver = lm_drivers.LmOnboardRmDriver(self.__lmBase(), self.__lmSecurityCtrl())   
        return self.__onboard_rm_driver

    def getTopologyDriver(self):
        """
        Obtain a LmTopologyDriver configured for use against this LM environment

        Returns:
            LmTopologyDriver: a configured LmTopologyDriver for this LM environment
        """
        if not self.__topology_driver:
            self.__topology_driver = lm_drivers.LmTopologyDriver(self.__lmBase(), self.__lmSecurityCtrl())   
        return self.__topology_driver
        
    def getBehaviourDriver(self):
        """
        Obtain a LmBehaviourDriver configured for use against this LM environment

        Returns:
            LmBehaviourDriver: a configured LmBehaviourDriver for this LM environment
        """
        if not self.__behaviour_driver:
            self.__behaviour_driver = lm_drivers.LmBehaviourDriver(self.__lmBase(), self.__lmSecurityCtrl())   
        return self.__behaviour_driver
