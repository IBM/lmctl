from .exceptions import ConfigError
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
        lm_conf = group_config_dict.get('lm', None)
        alm_conf = group_config_dict.get('alm', None)
        tnco_conf = group_config_dict.get('tnco', None)
        if lm_conf is not None and alm_conf is not None:
            raise ConfigError('Environment should not feature both "lm" and "alm"')
        if lm_conf is not None and tnco_conf is not None:
            raise ConfigError('Environment should not feature both "lm" and "tnco"')
        if alm_conf is not None and tnco_conf is not None:
            raise ConfigError('Environment should not feature both "alm" and "tnco"')
        lm_config_dict = tnco_conf or lm_conf or alm_conf
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
        if 'ip_address' in lm_config_dict and 'host' not in lm_config_dict:
            lm_config_dict['host'] = lm_config_dict['ip_address']
        if 'protocol' not in lm_config_dict and 'secure_port' in lm_config_dict:
            secure_port = lm_config_dict['secure_port']
            if secure_port is True:
                lm_config_dict['protocol'] = 'https'
            else:
                lm_config_dict['protocol'] = 'http'
        lm_config_dict.pop('ip_address', None)
        lm_config_dict.pop('secure_port', None)
        try:
            return lmenvs.LmEnvironment(name, **lm_config_dict)
        except envgroups.EnvironmentConfigError as e:
            raise ConfigError(str(e)) from e

    def __parse_arm_envs(self, arm_configs_dict):
        arm_configs = {}
        for key,value in arm_configs_dict.items():
            arm_configs[key] = self.__parse_arm_env(key, value)
        return arm_configs

    def __parse_arm_env(self, name, arm_config_dict):
        if 'ip_address' in arm_config_dict and 'host' not in arm_config_dict:
            arm_config_dict['host'] = arm_config_dict['ip_address']
        if 'protocol' not in arm_config_dict and 'secure_port' in arm_config_dict:
            secure_port = arm_config_dict['secure_port']
            if secure_port is True:
                arm_config_dict['protocol'] = 'https'
            else:
                arm_config_dict['protocol'] = 'http'
        arm_config_dict.pop('ip_address', None)
        arm_config_dict.pop('secure_port', None)
        try:
            return armenvs.ArmEnvironment(name, **arm_config_dict)
        except envgroups.EnvironmentConfigError as e:
            raise ConfigError(str(e)) from e
