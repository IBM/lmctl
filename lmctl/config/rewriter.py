import os
import yaml
import shutil 
from .exceptions import ConfigError

class ConfigRewriter:

    def __init__(self, path, config):
        self.path = path
        self.config = config

    def rewrite(self):
        new_config = {}
        if type(self.config) is not dict:
            raise ConfigError('Configuration should be a dictionary')
        environments = self.config
        if type(environments) is dict:
            for env_group_name, env_group_config in environments.items():
                environments[env_group_name] = self.__reconfigure_environment_group(env_group_config)
        new_config['environments'] = environments
        if os.path.exists(self.path):
            backup_file_name = '{0}.bak'.format(os.path.basename(self.path))
            backup_path = os.path.join(os.path.dirname(self.path), backup_file_name)
            shutil.copyfile(self.path, backup_path)
            os.remove(self.path)
        with open(self.path, 'w') as writer:
            writer.write('## Lmctl has updated this file with the latest schema changes. A backup of your existing config file has been placed in the same directory with a .bak extension\n')
            yaml.safe_dump(new_config, writer, default_flow_style=False, sort_keys=False)
        return new_config

    def __reconfigure_environment_group(self, env_group_config):
        if 'alm' in env_group_config:
            env_group_config['alm'] = self.__reconfigure_lm(env_group_config['alm'])
        if 'arm' in env_group_config:
            arms = env_group_config['arm']
            if type(arms) is dict:
                for arm_name, arm_config in arms.items():
                    arms[arm_name] = self.__reconfigure_arm(arm_config)
                env_group_config['arm'] = arms
        return env_group_config

    def __reconfigure_lm(self, lm_config):
        if lm_config is None:
            return lm_config
        new_lm_config = {}
        for key, value in lm_config.items():
            if key == 'ip_address':
                key = 'host'
            elif key == 'secure_port':
                key = 'protocol'
                value = 'https'
                if lm_config['secure_port'] is False:
                    value = 'http'
            new_lm_config[key] = value
        if 'secure' not in new_lm_config:
            if 'username' not in new_lm_config:
                new_lm_config['secure'] = False
            else:
                new_lm_config['secure'] = True
        return new_lm_config

    def __reconfigure_arm(self, arm_config):
        if arm_config is None:
            return arm_config
        new_arm_config = {}
        for key,value in arm_config.items():
            if key == 'ip_address':
                key = 'host'
            elif key == 'secure_port':
                key = 'protocol'
                value = 'https'
                if arm_config['secure_port'] is False:
                    value = 'http'
            if key != 'onboarding_addr':
                new_arm_config[key] = value
        return new_arm_config
