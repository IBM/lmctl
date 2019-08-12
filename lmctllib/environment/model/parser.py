from .model import Environment, LmEnvironment, ArmEnvironment

class EnvironmentParser:
    """
    Handles reading a raw environment object into Environment objects
    """
    def __init__(self, env_name, raw_env):
        if not raw_env:
            raise ValueError('raw_env must be defined')
        self.raw_env = raw_env
        self.env_name = env_name

    def parse(self):
        """
        Parse the raw_env, validating LM and ARM environments
        """
        lm_env = self.__parseLm()
        arm_envs = self.__parseArm()
        return Environment(self.env_name, self.raw_env['description'], lm_env, arm_envs)

    def __parseLm(self):
        if 'alm' in self.raw_env:
            return LmEnvironment(self.raw_env['alm'])
        else:
            raise ValueError('Environment {0} missing alm section'.format(self.env_name))
    
    def __parseArm(self):
        arms = {}
        if 'arm' in self.raw_env:
            for arm_name in self.raw_env['arm']:
              arms[arm_name] = ArmEnvironment(arm_name, self.raw_env['arm'][arm_name])
        else:
            raise ValueError('Environment {0} missing arm section'.format(self.env_name))
        return arms
