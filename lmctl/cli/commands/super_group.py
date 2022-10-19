import click
from typing import Iterable, Optional, Tuple
from collections import OrderedDict

DEFAULT_UNTAGGED_COMMAND_TITLE = 'Other'

class SuperGroup(click.Group):
    
    def __init__(self, *args, tag_order: Optional[Iterable[str]] = None, untagged_command_title: Optional[str] = DEFAULT_UNTAGGED_COMMAND_TITLE, **kwargs):
        self.tag_order = [] if tag_order is None else [t for t in tag_order]
        self.cmds_by_alias = {}
        self.cmd_aliases = {}
        self.cmd_tags = {}
        self.untagged_command_title = untagged_command_title

        super().__init__(*args, **kwargs)

    def _establish_tag_buckets(self) -> OrderedDict:
        cmds_by_tags = OrderedDict({})
        if self.tag_order:
            for tag in self.tag_order:
                cmds_by_tags[tag] = []
        return cmds_by_tags

    def associate_aliases(self, cmd: click.Command, aliases: Optional[Iterable[str]]):
        for alias in aliases:
            self.cmds_by_alias[alias] = cmd
        if cmd not in self.cmd_aliases:
            self.cmd_aliases[cmd] = []
        self.cmd_aliases[cmd].extend(aliases)

    def associate_tags(self, cmd: click.Command, tags: Optional[Iterable[str]]):
        if cmd not in self.cmd_tags:
            self.cmd_tags[cmd] = []
        self.cmd_tags[cmd].extend(tags)

    def add_command(self, cmd: click.Command, name: Optional[str] = None, aliases: Optional[Iterable[str]] = None, tags: Optional[Iterable[str]] = None) -> None:
        super().add_command(cmd, name=name)
        if aliases:
            self.associate_aliases(cmd, aliases)
        if tags:
            self.associate_tags(cmd, tags)

    def command(self, *args, aliases: Optional[Iterable[str]] = None, tags: Optional[Iterable[str]] = None, **kwargs):
        parent_decorator = super().command(*args, **kwargs)
        if not aliases and not tags:
            return parent_decorator
        def decorator(f):
            # Let click.Group decorate the command as normal
            cmd = parent_decorator(f)
            if aliases:
                self.associate_aliases(cmd, aliases)
            if tags:
                self.associate_tags(cmd, tags)
        return decorator

    def group(self, *args, aliases: Optional[Iterable[str]] = None, tags: Optional[Iterable[str]] = None, **kwargs):
        parent_decorator = super().group(*args, **kwargs)
        if not aliases and not tags:
            return parent_decorator
        def decorator(f):
            # Let click.Group decorate the group as normal
            cmd = parent_decorator(f)
            if aliases:
                self.associate_aliases(cmd, aliases)
            if tags:
                self.associate_tags(cmd, tags)
        return decorator

    def get_command(self, ctx: click.Context, cmd_name: str) -> Optional[click.Command]:
        cmd = super().get_command(ctx, cmd_name)
        if cmd is not None:
            return cmd

        # Try aliases
        cmd = self.cmds_by_alias.get(cmd_name, None)
        return cmd

    def format_commands(self, ctx: click.Context, formatter: click.HelpFormatter):
        """
        Override format_commands to separate commands by tag
        """
        cmds_by_tag = self._sort_commands_by_tags(ctx)
        self._write_command_tag_groups(ctx, formatter, cmds_by_tag)
        

    def _sort_commands_by_tags(self, ctx: click.Context) -> 'OrderedDict[str, Tuple[str, click.Command]]':
        cmds_by_tag = self._establish_tag_buckets()
        untagged_cmds = []
        for cmd_name in self.list_commands(ctx):
            cmd = self.get_command(ctx, cmd_name)
            if cmd is None:
                continue
            if cmd.hidden:
                continue
            
            if cmd not in self.cmd_tags or len(self.cmd_tags[cmd]) == 0:
                untagged_cmds.append((cmd_name, cmd))
            else:
                for tag in self.cmd_tags[cmd]:
                    if tag not in cmds_by_tag:
                        cmds_by_tag[tag] = []
                    cmds_by_tag[tag].append((cmd_name, cmd))
        cmds_by_tag[self.untagged_command_title] = untagged_cmds
        return cmds_by_tag

    def _all_commands_are_untagged(self, cmds_by_tag: 'OrderedDict[str, Tuple[str, click.Command]]') -> bool:
        tags_with_cmds = [tag for tag, cmd_tpls in cmds_by_tag.items() if len(cmd_tpls) > 0]
        return len(tags_with_cmds) == 1 and tags_with_cmds[0] == self.untagged_command_title

    def _write_command_tag_groups(self, ctx: click.Context, formatter: click.HelpFormatter, cmds_by_tag: 'OrderedDict[str, Tuple[str, click.Command]]'):
        # Check if all commands ended up in the untagged section
        if self._all_commands_are_untagged(cmds_by_tag):
            # Shortcut to print as a normal list of commands with title "Commands"
            self._write_commands_in_tag_group(ctx, formatter, 'Commands', cmds_by_tag[self.untagged_command_title])
            return

        for tag, cmd_tpls in cmds_by_tag.items():
            if len(cmd_tpls) > 0:
                self._write_commands_in_tag_group(ctx, formatter, tag, cmd_tpls)

    def _write_commands_in_tag_group(self, ctx: click.Context, formatter: click.HelpFormatter, tag: str, cmd_tpls: Tuple[str, click.Command]):
        if len(cmd_tpls):
            # Click recommended width
            # Take away 6 for spacing
            # Take away the length of the largest command name
            limit = formatter.width - 6 - max(len(cmd_name) for cmd_name, _ in cmd_tpls)
            rows = []
            for cmd_name, cmd in cmd_tpls:
                help = cmd.get_short_help_str(limit)
                rows.append((cmd_name, help))
            if rows:
                with formatter.section(tag):
                    formatter.write_dl(rows)

    def _get_command_help_row(self, ctx: click.Context, cmd_name: str, cmd: click.Command, limit: int) -> Tuple[str, str]:
        help_msg = cmd.get_short_help_str(limit)

        # Include aliases in cmd_name
        cmd_name_msg = cmd_name
        aliases = self.cmd_aliases.get(cmd, [])
        if len(aliases) > 0:
            aliases_str = ', '.join(aliases)
            cmd_name_msg += f'({aliases_str})'

        return (cmd_name_msg, help_msg)