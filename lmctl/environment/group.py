from .common import EnvironmentRuntimeError, EnvironmentConfigError, value_or_default
from .lmenv import LmEnvironment
from .armenv import ArmEnvironment

class EnvironmentGroup:

    def __init__(self, name, description='', lm_env=None, arm_envs=None):
        name = value_or_default(name)
        if not name:
            raise EnvironmentConfigError('name must be defined')
        self.name = name
        self.description = description
        if lm_env is not None:
            if not isinstance(lm_env, LmEnvironment):
                raise EnvironmentConfigError('lm_env provided must be of type LmEnvironment')
        self.lm_env = lm_env
        if arm_envs is None:
            arm_envs = {}
        if type(arm_envs) is not dict:
            raise EnvironmentConfigError('arm_envs must be name/value pairs')
        for key, value in arm_envs.items():
            if not isinstance(value, ArmEnvironment):
                raise EnvironmentConfigError('Items in arm_envs dict must be of type ArmEnvironment')
        self.arm_envs = arm_envs

    @property
    def lm(self):
        if not self.lm_env:
            raise EnvironmentRuntimeError('No TNCO environment has been configured on this group: {0}'.format(self.name))
        return self.lm_env

    @property
    def tnco(self):
        if not self.lm_env:
            raise EnvironmentRuntimeError('No TNCO environment has been configured on this group: {0}'.format(self.name))
        return self.lm_env

    @property
    def has_lm(self):
        return self.lm_env is not None

    @property
    def arms(self):
        return self.arm_envs

    def arm_named(self, arm_name):
        if arm_name in self.arm_envs:
            return self.arm_envs[arm_name]
        else:
            raise EnvironmentRuntimeError('No ARM named \'{0}\' on this group: {1}'.format(arm_name, self.name))

