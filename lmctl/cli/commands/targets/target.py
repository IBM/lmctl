import click
from lmctl.cli.controller import get_global_controller

class Target:

    def __init__(self, name: str = None, display_name: str = None):
        if name is None:
            if not hasattr(self, 'name'):
                raise ValueError(f'Subclass of Target must set "name" class attribute: Subclass={self.__class__.__name__}')
        else:
            self.name = name

    def _get_controller(self, override_config_path: str = None):
        return get_global_controller(override_config_path=override_config_path)
    