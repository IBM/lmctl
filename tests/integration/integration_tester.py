import logging
import os
import yaml
import json
import zipfile
import tempfile
import time
import shutil
import jinja2 as jinja
from typing import Callable, Dict
from .names import generate_name
from .integration_test_properties import IntegrationTestProperties
from lmctl.config import get_global_config, get_config

logger = logging.getLogger(__name__)

default_props_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'local_test_properties.yaml')

jinja_env = jinja.Environment(loader=jinja.BaseLoader, variable_start_string='[[', variable_end_string=']]')

class IntegrationTester:

    def __init__(self):
        self.test_properties = self._read_properties()
        self.tmp_dir = tempfile.mkdtemp(prefix='lmctltests')
        self._create_config_file()
        self.config = get_global_config()
        self.default_client = self.build_default_client()
        self.execution_id = generate_name()
        self.test_id = 0
        print(f'Generated execution name: {self.execution_id}')
    
    def start(self):
        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)
            
    def close(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)

    def read_latest_copy_of_config(self):
        return get_config(override_config_path=self.config_path)
    
    def _create_config_file(self):
        self.config_path = os.path.join(self.tmp_dir, 'lmctl-config.yaml')
        with open(self.config_path, 'w') as f:
            f.write(yaml.safe_dump(self.test_properties.config))
        os.environ['LMCONFIG'] = self.config_path

    def _read_properties(self):
        props_location = os.getenv('LMCTL_TEST_PROPS')
        if props_location is None:
            props_location = default_props_path
        logger.info(f'Loading test properties from: {props_location}')
        with open(props_location, 'r') as f:
            props_dict = yaml.safe_load(f.read())
        return IntegrationTestProperties.from_dict(**props_dict)
    
    def get_default_env(self):
        return self.config.environments.get('default')

    def build_default_client(self):
        return self.build_client()

    def build_client(self):
        default_env = self.get_default_env()
        return default_env.tnco.build_client()

    def exec_prepended_name(self, name: str) -> str:
        return f'{self.execution_id}-{name}'

    def short_exec_prepended_name(self, name: str, limit: int = 30) -> str:
        result = self.exec_prepended_name(name)
        if len(result) > limit:
            vowels = set('AEIOU')
            short_exec_id = ''.join([letter for letter in self.execution_id if letter.upper() not in vowels])
            new_result = f'{short_exec_id}-{name}'
            if len(new_result) > limit:
                new_result = ''.join([letter for letter in new_result if letter.upper() not in vowels])
                if len(new_result) > limit:
                    raise ValueError(f'Could not shorten {result} to less than {limit} characters')
            return new_result
        else:
            return result

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

    def render_template_file(self, src_file_path: str, target_file_path: str, suffix: str = None, ctx: Dict = None) -> str:
        with open(src_file_path, 'r') as f:
            content = f.read()
        if ctx is not None:
            render_context = ctx
        else:
            render_context = {}
        render_context['execution_id'] = self.execution_id
        render_context['test_id'] = self.test_id
        render_context['suffix'] = suffix or self.test_id
        rendered = jinja_env.from_string(content).render(render_context)
        with open(target_file_path, 'w') as f:
            f.write(rendered)
        return target_file_path

    def render_template_directory(self, src_dir_path: str, target_dir_path: str, suffix: str = None, ctx: Dict = None) -> str:
        src_dir_name = os.path.basename(src_dir_path)
        if src_dir_name == '__pycache__':
            return
        if not os.path.exists(target_dir_path):
            os.mkdir(target_dir_path)
        for item in os.listdir(src_dir_path):
            item_path = os.path.join(src_dir_path, item)
            if os.path.isdir(item_path):
                self.render_template_directory(item_path, os.path.join(target_dir_path, item), suffix=suffix, ctx=ctx)
            else:
                self.render_template_file(item_path, os.path.join(target_dir_path, item), suffix=suffix, ctx=ctx)
        return target_dir_path

    def build_resource_package_from(self, resource_src_path: str, target_path: str, suffix: str = None, ctx: Dict = None):
        rendered_src_path = self.tmp_file(os.path.basename(resource_src_path))
        self.render_template_directory(resource_src_path, rendered_src_path, suffix=suffix, ctx=ctx)
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

    def load_descriptor_from(self, descriptor_path: str, suffix: str = None, ctx: Dict = None) -> Dict:
        target_file_path = self.tmp_file(os.path.basename(descriptor_path))
        self.render_template_file(descriptor_path, target_file_path, suffix=suffix, ctx=ctx)
        with open(target_file_path, 'r') as f:
            descriptor = yaml.safe_load(f.read())
        return descriptor

    def load_behaviour_scenario_from(self, scenario_path: str, suffix: str = None, ctx: Dict = None) -> Dict:
        target_file_path = self.tmp_file(os.path.basename(scenario_path))
        self.render_template_file(scenario_path, target_file_path, suffix=suffix, ctx=ctx)
        with open(target_file_path, 'r') as f:
            scenario = json.loads(f.read())
        return scenario

    def create_yaml_file(self, file_name: str, obj: Dict):
        tmp_file = self.tmp_file(file_name)
        with open(tmp_file, 'w') as f:
            f.write(yaml.safe_dump(obj))
        return tmp_file

    def create_json_file(self, file_name: str, obj: Dict):
        tmp_file = self.tmp_file(file_name)
        with open(tmp_file, 'w') as f:
            f.write(json.dumps(obj))
        return tmp_file
    