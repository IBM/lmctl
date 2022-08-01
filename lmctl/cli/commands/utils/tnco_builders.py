import click
from ..actions import (
    create as create_group,
    get as get_group,
    update as update_group, 
    delete as delete_group,
    generate as generate_group,
)
from .tnco_env_command import TNCOEnvironmentCommand
from .tnco_create_command import TNCOCreateCommand
from .tnco_get_command import TNCOGetCommand
from .tnco_update_command import TNCOUpdateCommand
from .tnco_delete_command import TNCODeleteCommand
from .tnco_generate_command import TNCOGenerateCommand
from .tnco_general_command import TNCOGeneralCommand
from lmctl.cli.tags import CP4NA_CORE_TAG
from typing import Iterable

__all__ = (
    'TNCOCommandBuilder',
)

class TNCOCommandBuilder:

    def __init__(self, singular: str, plural: str, display_name: str, aliases: Iterable[str] = None):
        self.singular = singular
        self.plural = plural
        self.display_name = display_name
        self.aliases = [a for a in aliases] if aliases is not None else []

    def _all_aliases(self):
        return [self.plural] + self.aliases

    def make_create_command(self, **kwargs):
        def decorator(f):
            return create_group.command(
                self.singular,
                cls=TNCOCreateCommand,
                type_display_name=self.display_name,
                aliases=self._all_aliases(),
                tags=[CP4NA_CORE_TAG],
                **kwargs
            )(f)
        return decorator

    def make_get_command(self, **kwargs):
        def decorator(f):
            return get_group.command(
                self.singular,
                cls=TNCOGetCommand,
                type_display_name=self.display_name,
                aliases=self._all_aliases(),
                tags=[CP4NA_CORE_TAG],
                **kwargs
            )(f)
        return decorator

    def make_update_command(self, **kwargs):
        def decorator(f):
            return update_group.command(
                self.singular,
                cls=TNCOUpdateCommand,
                type_display_name=self.display_name,
                aliases=self._all_aliases(),
                tags=[CP4NA_CORE_TAG],
                **kwargs
            )(f)
        return decorator

    def make_delete_command(self, **kwargs):
        def decorator(f):
            return delete_group.command(
                self.singular,
                cls=TNCODeleteCommand,
                type_display_name=self.display_name,
                aliases=self._all_aliases(),
                tags=[CP4NA_CORE_TAG],
                **kwargs
            )(f)
        return decorator

    def make_generate_command(self, **kwargs):
        def decorator(f):
            return generate_group.command(
                self.singular,
                cls=TNCOGenerateCommand,
                type_display_name=self.display_name,
                aliases=self._all_aliases(),
                tags=[CP4NA_CORE_TAG],
                **kwargs
            )(f)
        return decorator

    def make_general_command(self, group: click.Group = None, **kwargs):
        if group is None:
            group = click
        def decorator(f):
            return group.command(
                self.singular,
                cls=TNCOGeneralCommand,
                type_display_name=self.display_name,
                aliases=self._all_aliases(),
                tags=[CP4NA_CORE_TAG],
                **kwargs
            )(f)
        return decorator

    def make_command(self, group: click.Group = None, **kwargs):
        if group is None:
            group = click
        def decorator(f):
            return group.command(
                self.singular,
                cls=TNCOEnvironmentCommand,
                aliases=self._all_aliases(),
                tags=[CP4NA_CORE_TAG],
                **kwargs
            )(f)
        return decorator