import unittest
import tests.common.simulations.project_lab as project_lab
from tests.common.project_testing import (ProjectSimTestCase, PROJECT_CONTAINS_DIR, PKG_CONTENT_DIR) 
from lmctl.project.package.core import Pkg, PkgContent, PushOptions
from lmctl.project.sessions import EnvironmentSessions
import os

class TestPushAnsibleRmProjects(ProjectSimTestCase):

    def test_push(self):
        pkg_sim = self.simlab.simulate_pkg_arm_basic()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        arm_sim = self.simlab.simulate_arm()
        arm_session = arm_sim.as_mocked_session()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_rm({'name': arm_session.env.name, 'url': arm_session.env.address})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session, arm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        csar_path = os.path.join(result.tree.root_path, 'basic.csar')
        arm_session.arm_driver.onboard_type.assert_called_once_with('basic', '1.0', csar_path)
        lm_session.onboard_rm_driver.get_rm_by_name.assert_called_once_with(arm_session.env.name)
        lm_session.onboard_rm_driver.update_rm.assert_called_once_with({'name': arm_session.env.name, 'url': arm_session.env.address})
        
class TestPushAnsibleRmSubprojects(ProjectSimTestCase):

    def test_push(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_arm_basic()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        arm_sim = self.simlab.simulate_arm()
        arm_session = arm_sim.as_mocked_session()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_rm({'name': arm_session.env.name, 'url': arm_session.env.address})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session, arm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        csar_path = os.path.join(result.tree.root_path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_ARM_BASIC, 'sub_basic-contains_basic.csar')
        arm_session.arm_driver.onboard_type.assert_called_once_with('sub_basic-contains_basic', '1.0', csar_path)
        lm_session.onboard_rm_driver.get_rm_by_name.assert_called_once_with(arm_session.env.name)
        lm_session.onboard_rm_driver.update_rm.assert_called_once_with({'name': arm_session.env.name, 'url': arm_session.env.address})
        