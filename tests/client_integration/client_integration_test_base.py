import unittest
import os
import yaml
import json
import logging
import zipfile
import tempfile
import shutil
import time
import jinja2 as jinja
import lmctl.client as lm_clients
from typing import Dict, Any, Callable
from lmctl.client.client_credentials_auth import ClientCredentialsAuth
from lmctl.client.pass_auth import UserPassAuth, LegacyUserPassAuth
from .names import generate_name

logger = logging.getLogger(__name__)

default_props_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_properties.yaml')

jinja_env = jinja.Environment(loader=jinja.BaseLoader, variable_start_string='[[', variable_end_string=']]')

class ClientTestProperties:

    def __init__(self, lm_address: str, main_auth: str, client_credentials: ClientCredentialsAuth, user_pass: UserPassAuth, legacy_user_pass: LegacyUserPassAuth, kami_address: str = None):
        self.lm_address = lm_address
        self.main_auth = main_auth
        self.kami_address = kami_address
        self.client_credentials = client_credentials
        self.user_pass = user_pass
        self.legacy_user_pass = legacy_user_pass

    @staticmethod
    def from_dict(lm_address: str, 
                    client_credentials: Dict, 
                    user_pass: Dict, 
                    legacy_user_pass: Dict, 
                    main_auth: str = 'client_credentials', 
                    kami_address: str = None):
        return ClientTestProperties(
            lm_address=lm_address,
            main_auth=main_auth,
            kami_address=kami_address,
            client_credentials=ClientCredentialsAuth(**client_credentials),
            user_pass=UserPassAuth(**user_pass),
            legacy_user_pass=LegacyUserPassAuth(**legacy_user_pass)
        )

class ClientTester:

    def __init__(self):
        self.test_properties = self._read_properties()
        self.default_client = self.build_default_client()
        self.execution_id = generate_name()
        print(f'Generated execution name: {self.execution_id}')
        self.tmp_dir = tempfile.mkdtemp(prefix='lmctltests')
    
    def _read_properties(self):
        props_location = os.getenv('LMCTL_TEST_PROPS')
        if props_location is None or len(props_location) == 0:
            props_location = default_props_path
        logger.info(f'Loading test properties from: {props_location}')
        with open(props_location, 'r') as f:
            props_dict = yaml.safe_load(f.read())
        return ClientTestProperties.from_dict(**props_dict)

    def build_default_client(self):
        return self.build_client(chosen_auth=self.test_properties.main_auth)

    def build_client(self, chosen_auth: str = None):
        client_builder = lm_clients.builder().address(self.test_properties.lm_address)
        if chosen_auth == 'client_credentials':
            client_builder.auth(self.test_properties.client_credentials)
        elif chosen_auth == 'user_pass':
            client_builder.auth(self.test_properties.user_pass)
        elif chosen_auth == 'legacy_user_pass':
            client_builder.auth(self.test_properties.legacy_user_pass)
        if self.test_properties.kami_address is not None:
            client_builder.kami_address(self.test_properties.kami_address)
        return client_builder.build()
           
    def exec_prepended_name(self, name: str) -> str:
        return f'{self.execution_id}-{name}'

    def wait_until(self, condition: Callable, *condition_args, timeout: float = 60, interval: float = 0.1):
        start = time.time()
        condition_passed = condition(*condition_args) 
        while not condition_passed and time.time() - start < timeout:
            time.sleep(interval)
            condition_passed = condition(*condition_args)
        if condition_passed:
            return True
        else:
            raise Exception(f'Timed out waiting for condition: {condition}')

    @property
    def test_files_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_files')

    def test_file(self, name: str) -> str:
        return os.path.join(self.test_files_path, name)

    def tmp_file(self, name: str) -> str:
        return os.path.join(self.tmp_dir, name)

    def render_template_file(self, src_file_path: str, target_file_path: str) -> str:
        with open(src_file_path, 'r') as f:
            content = f.read()
        render_context = {
            'execution_id': self.execution_id
        }
        rendered = jinja_env.from_string(content).render(render_context)
        with open(target_file_path, 'w') as f:
            f.write(rendered)
        return target_file_path

    def render_template_directory(self, src_dir_path: str, target_dir_path: str) -> str:
        src_dir_name = os.path.basename(src_dir_path)
        if src_dir_name == '__pycache__':
            return
        if not os.path.exists(target_dir_path):
            os.mkdir(target_dir_path)
        for item in os.listdir(src_dir_path):
            item_path = os.path.join(src_dir_path, item)
            if os.path.isdir(item_path):
                self.render_template_directory(item_path, os.path.join(target_dir_path, item))
            else:
                self.render_template_file(item_path, os.path.join(target_dir_path, item))
        return target_dir_path

    def build_resource_package_from(self, resource_src_path: str, target_path: str):
        rendered_src_path = self.tmp_file(os.path.basename(resource_src_path))
        self.render_template_directory(resource_src_path, rendered_src_path)
        with zipfile.ZipFile(target_path, "w") as res_pkg:
            included_dirs = ['Definitions', 'Lifecycle']
            for dir_name in included_dirs:
                src_path = os.path.join(rendered_src_path, dir_name)
                res_pkg.write(src_path, arcname=dir_name)
                rootlen = len(src_path) + 1
                for root, dirs, files in os.walk(src_path):
                    for dirname in dirs:
                        full_path = os.path.join(root, dirname)
                        res_pkg.write(full_path, arcname=os.path.join(dir_name, full_path[rootlen:]))
                    for filename in files:
                        full_path = os.path.join(root, filename)
                        res_pkg.write(full_path, arcname=os.path.join(dir_name, full_path[rootlen:]))
        return target_path

    def load_descriptor_from(self, descriptor_path: str) -> Dict:
        target_file_path = self.tmp_file(os.path.basename(descriptor_path))
        self.render_template_file(descriptor_path, target_file_path)
        with open(target_file_path, 'r') as f:
            descriptor = yaml.safe_load(f.read())
        return descriptor

    def load_behaviour_scenario_from(self, scenario_path: str) -> Dict:
        target_file_path = self.tmp_file(os.path.basename(scenario_path))
        self.render_template_file(scenario_path, target_file_path)
        with open(target_file_path, 'r') as f:
            scenario = json.loads(f.read())
        return scenario

class ClientIntegrationTest(unittest.TestCase):
    tester: ClientTester = None

    @classmethod
    def setUpClass(cls):
        if ClientIntegrationTest.tester is None:
            ClientIntegrationTest.tester = ClientTester()
        cls.before_test_case(ClientIntegrationTest.tester)

    @classmethod
    def tearDownClass(cls):
        cls.after_test_case(ClientIntegrationTest.tester)
        ClientIntegrationTest.tester.default_client.close()

    @classmethod
    def before_test_case(cls, tester):
        pass

    @classmethod
    def after_test_case(cls, tester):
        pass

    def setUp(self):
        self.local_tmp_dir = tempfile.mkdtemp(prefix='lmctl_tests')
        self.before_test()

    def tearDown(self):
        self.after_test()
        if os.path.exists(self.local_tmp_dir):
            shutil.rmtree(self.local_tmp_dir)

    def before_test(self):
        pass

    def after_test(self):
        pass

