from .common import ConfigError
import lmctl.environment.group as envgroups
import lmctl.environment.lmenv as lmenvs
import lmctl.environment.armenv as armenvs

class EnvironmentGroupsParser:

    @staticmethod
    def from_dict(groups_config_dict):
        return EnvironmentGroupParserWorker(groups_config_dict).parse()

class EnvironmentGroupParserWorker:

    def __init__(self, groups_config_dict):
        self.groups_config_dict = groups_config_dict

    def parse(self):
        group_configs = {}
        for group_name, group_config_dict in self.groups_config_dict.items():
            group_configs[group_name] = self.__parse_group(group_name, group_config_dict)
        return group_configs

    def __parse_group(self, group_name, group_config_dict):
        description = group_config_dict.get('description', None)
        lm_env = None
        arm_envs = None
        if 'lm' in group_config_dict and 'alm' in group_config_dict:
            raise ConfigError('Environment should not feature both \'lm\' and \'alm\'')
        lm_config_dict = group_config_dict.get('lm', group_config_dict.get('alm', None))
        if lm_config_dict:
            lm_env = self.__parse_lm_env(lm_config_dict)
        arm_configs_dict = group_config_dict.get('arm', None)
        if arm_configs_dict:
            arm_envs = self.__parse_arm_envs(arm_configs_dict)
        try:
            return envgroups.EnvironmentGroup(group_name, description, lm_env, arm_envs)
        except envgroups.EnvironmentConfigError as e:
            raise ConfigError(str(e)) from e

    def __parse_lm_env(self, lm_config_dict):
        name = 'alm'
        host = lm_config_dict.get('host', lm_config_dict.get('ip_address', None))
        port = lm_config_dict.get('port', None)
        path = lm_config_dict.get('path', None)
        protocol = lm_config_dict.get('protocol', None)
        if not protocol:
            secure_port = lm_config_dict.get('secure_port', None)
            if secure_port is True:
                protocol = lmenvs.HTTPS_PROTOCOL
            elif secure_port is False:
                protocol = lmenvs.HTTP_PROTOCOL
        secure = lm_config_dict.get('secure', False)
        username = lm_config_dict.get('username', None)
        auth_host = lm_config_dict.get('auth_host', lm_config_dict.get('auth_address', None))
        auth_port = lm_config_dict.get('auth_port', None)
        password = lm_config_dict.get('password', None)
        auth_protocol = lm_config_dict.get('auth_protocol', None)
        try:
            return lmenvs.LmEnvironment(name, host, port, protocol, path=path, secure=secure,  username=username, password=password, auth_host=auth_host, auth_port=auth_port, auth_protocol=auth_protocol)
        except envgroups.EnvironmentConfigError as e:
            raise ConfigError(str(e)) from e

    def __parse_arm_envs(self, arm_configs_dict):
        arm_configs = {}
        for key,value in arm_configs_dict.items():
            arm_configs[key] = self.__parse_arm_env(key, value)
        return arm_configs

    def __parse_arm_env(self, name, arm_config_dict):
        host = arm_config_dict.get('host', arm_config_dict.get('ip_address', None))
        port = arm_config_dict.get('port', None)
        protocol = arm_config_dict.get('protocol', None)
        if not protocol:
            secure_port = arm_config_dict.get('secure_port', None)
            if secure_port is True:
                protocol = armenvs.HTTPS_PROTOCOL
            elif secure_port is False:
                protocol = armenvs.HTTP_PROTOCOL
        onboarding_addr = arm_config_dict.get('onboarding_addr', None)
        try:
            return armenvs.ArmEnvironment(name, host, port, protocol, onboarding_addr=onboarding_addr)
        except envgroups.EnvironmentConfigError as e:
            raise ConfigError(str(e)) from e
