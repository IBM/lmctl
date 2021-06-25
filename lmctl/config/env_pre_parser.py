from .exceptions import ConfigError

class EnvironmentGroupPreParser:

    def parse(self, groups_config_dict):
        group_configs = {}
        for group_name, group_config_dict in groups_config_dict.items():
            group_configs[group_name] = self.__parse_group(group_name, group_config_dict)
        return group_configs

    def __parse_group(self, group_name, group_config_dict):
        group_config_dict['name'] = group_name
        lm_conf = group_config_dict.pop('lm', None)
        alm_conf = group_config_dict.pop('alm', None)
        tnco_conf = group_config_dict.pop('tnco', None)
        if lm_conf is not None and alm_conf is not None:
            raise ConfigError('Environment should not feature both "lm" and "alm"')
        if lm_conf is not None and tnco_conf is not None:
            raise ConfigError('Environment should not feature both "lm" and "tnco"')
        if alm_conf is not None and tnco_conf is not None:
            raise ConfigError('Environment should not feature both "alm" and "tnco"')
        tnco_conf_dict = tnco_conf or lm_conf or alm_conf
        if tnco_conf_dict is not None:
            tnco_conf_dict = self.__parse_tnco_env(tnco_conf_dict)
        if tnco_conf_dict is not None:
            group_config_dict['tnco'] = tnco_conf_dict
       
        arm_configs_dict = group_config_dict.pop('arm', None)
        arms_configs_dict = group_config_dict.pop('arms', None)
        if arms_configs_dict is not None:
            arms_configs_dict = self.__parse_arm_envs(arms_configs_dict)
        elif arm_configs_dict is not None:
            arms_configs_dict = self.__parse_arm_envs(arm_configs_dict)
        if arms_configs_dict is not None:
            group_config_dict['arms'] = arms_configs_dict

        return group_config_dict
       
    def __parse_tnco_env(self, tnco_conf_dict):
        if 'ip_address' in tnco_conf_dict and 'host' not in tnco_conf_dict:
            tnco_conf_dict['host'] = tnco_conf_dict['ip_address']
        if 'protocol' not in tnco_conf_dict and 'secure_port' in tnco_conf_dict:
            secure_port = tnco_conf_dict['secure_port']
            if secure_port is True:
                tnco_conf_dict['protocol'] = 'https'
            else:
                tnco_conf_dict['protocol'] = 'http'
        tnco_conf_dict.pop('ip_address', None)
        tnco_conf_dict.pop('secure_port', None)
        return tnco_conf_dict

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
        return arm_config_dict
