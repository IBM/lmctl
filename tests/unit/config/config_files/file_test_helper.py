import os
import shutil
import yaml
from typing import Dict

this_dir = os.path.dirname(__file__)

class ConfigFileTestHelper:

    def __init__(self, workspace: str):
        self.workspace = workspace

    def _ensure_workspace(self):
        if not os.path.exists(workspace):
            os.makedirs(workspace)

    def prepare_file(self, name: str):
        target_path = os.path.join(self.workspace, f'{name}.yaml')
        shutil.copyfile(os.path.join(this_dir, f'{name}.yaml'), target_path)
        return target_path

    def read_yaml_file(self, name: str) -> Dict:
        file_path = os.path.join(this_dir, f'{name}.yaml')
        with open(file_path, 'r') as f:
            return yaml.safe_load(f.read())

    def read_workspace_yaml_file(self, file_name: str) -> Dict:
        file_path = os.path.join(self.workspace, file_name)
        with open(file_path, 'r') as f:
            return yaml.safe_load(f.read())
