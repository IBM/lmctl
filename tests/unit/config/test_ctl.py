import unittest
import os
from lmctl.config import Ctl, Config, ConfigError
from lmctl.environment.group import EnvironmentGroup, EnvironmentGroup
from lmctl.environment.lmenv import LmEnvironment
from lmctl.environment.armenv import ArmEnvironment

class TestCtl(unittest.TestCase):

    def test_init(self):
        environments = {
            'groupA': EnvironmentGroup('groupA', '', LmEnvironment('alm', 'host'), {'defaultrm': ArmEnvironment('defaultrm', 'host')}),
            'groupB': EnvironmentGroup('groupB', '', LmEnvironment('alm', 'hostB'), {'defaultrm': ArmEnvironment('defaultrm', 'hostB')})
        }
        config = Config(environments)
        ctl = Ctl(config)
        self.assertEqual(len(ctl.environments), 2)
        groupA_env = ctl.environment_group_named('groupA')
        self.assertIsNotNone(groupA_env)
        self.assertIsInstance(groupA_env, EnvironmentGroup)
        groupB_env = ctl.environment_group_named('groupB')
        self.assertIsNotNone(groupB_env)
        self.assertIsInstance(groupB_env, EnvironmentGroup)

    def test_environment_group_named_fails_when_not_found(self):
        config = Config({})
        ctl = Ctl(config)
        with self.assertRaises(ConfigError) as context:
            ctl.environment_group_named('groupA')
        self.assertEqual(str(context.exception), 'No environment group with name: groupA')