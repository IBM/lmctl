import os
import tests.common.simulations.project_lab as project_lab
from tests.common.project_testing import (ProjectSimTestCase, PROJECT_CONTAINS_DIR) 
from lmctl.project.package.core import Pkg, PkgContent, PushOptions
from lmctl.project.sessions import EnvironmentSessions

class TestPushBrentProjects(ProjectSimTestCase):

    def test_push(self):
        pkg_sim = self.simlab.simulate_pkg_brent_basic()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_rm({'name': 'brent', 'url': 'http://brent:8443'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        res_pkg_path = os.path.join(result.tree.root_path, 'basic.zip')
        lm_session.descriptor_driver.delete_descriptor.assert_called_once_with('resource::basic::1.0')
        lm_session.resource_pkg_driver.delete_package.assert_called_once_with('resource::basic::1.0')
        lm_session.resource_pkg_driver.onboard_package.assert_called_once_with(res_pkg_path)
        lm_session.onboard_rm_driver.get_rm_by_name.assert_called_once_with('brent')
        lm_session.onboard_rm_driver.update_rm.assert_called_once_with({'name': 'brent', 'url': 'http://brent:8443'})
    
    def test_push_csar(self):
        pkg_sim = self.simlab.simulate_pkg_brent_tosca()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_rm({'name': 'brent', 'url': 'http://brent:8443'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        res_pkg_path = os.path.join(result.tree.root_path, 'with_tosca.zip')
        lm_session.descriptor_driver.delete_descriptor.assert_called_once_with('resource::with_tosca::1.0')
        lm_session.resource_pkg_driver.delete_package.assert_called_once_with('resource::with_tosca::1.0')
        lm_session.resource_pkg_driver.onboard_package.assert_called_once_with(res_pkg_path)
        lm_session.onboard_rm_driver.get_rm_by_name.assert_called_once_with('brent')
        lm_session.onboard_rm_driver.update_rm.assert_called_once_with({'name': 'brent', 'url': 'http://brent:8443'})
    
class TestPushBrentSubprojects(ProjectSimTestCase):

    def test_push(self):
        pkg_sim = self.simlab.simulate_pkg_assembly_contains_brent_basic()
        pkg = Pkg(pkg_sim.path)
        push_options = PushOptions()
        lm_sim = self.simlab.simulate_lm()
        lm_sim.add_rm({'name': 'brent', 'url': 'http://brent:8443'})
        lm_session = lm_sim.as_mocked_session()
        env_sessions = EnvironmentSessions(lm_session)
        result = pkg.push(env_sessions, push_options)
        self.assertIsInstance(result, PkgContent)
        res_pkg_path = os.path.join(result.tree.root_path, PROJECT_CONTAINS_DIR, project_lab.SUBPROJECT_NAME_BRENT_BASIC, 'sub_basic-contains_basic.zip')
        lm_session.descriptor_driver.delete_descriptor.assert_called_once_with('resource::sub_basic-contains_basic::1.0')
        lm_session.resource_pkg_driver.delete_package.assert_called_once_with('resource::sub_basic-contains_basic::1.0')
        lm_session.resource_pkg_driver.onboard_package.assert_called_once_with(res_pkg_path)
        lm_session.onboard_rm_driver.get_rm_by_name.assert_called_once_with('brent')
        lm_session.onboard_rm_driver.update_rm.assert_called_once_with({'name': 'brent', 'url': 'http://brent:8443'})
        