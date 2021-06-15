import click
from typing import List, Dict
from lmctl.cli.cmd_tags import actions_tag

class Action(click.MultiCommand):

    def __init__(self, name: str = None, group_attrs: Dict = None, targets: List = None):
        if name is None:
            if not hasattr(self, 'name'):
                raise ValueError(f'Subclass of Action must set "name" class attribute: Subclass={self.__class__.__name__}')
        else:
            self.name = name
        if group_attrs is not None:
            self.group_attrs = group_attrs
        if hasattr(self, 'group_attrs'):
            group_attrs_to_pass = self.group_attrs
        else:
            group_attrs_to_pass = {}
        self.targets = targets
        actions_tag(self)
        super().__init__(name=self.name, **group_attrs_to_pass)

    def _can_act_on(self, target):
        if hasattr(target, self.name):
            action_on_target = getattr(target, self.name)()
            if callable(action_on_target) and isinstance(action_on_target, click.Command):
                return True, action_on_target
        return False, None

    def list_commands(self, ctx):
        result = []
        for t in self.targets:
            can_act, _ = self._can_act_on(t)
            if can_act:
                result.append(t.name)
        result.sort()
        return result

    def get_command(self, ctx, name):
        for t in self.targets:
            if t.name == name or (hasattr(t, 'plural') and getattr(t, 'plural') == name):
                can_act, callable_on_target = self._can_act_on(t)
                if can_act:
                    return callable_on_target
                break
        return None