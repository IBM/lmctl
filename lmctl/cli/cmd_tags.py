from collections import OrderedDict
import click

DEPRECATED_TAG = 'Deprecated'
SETTINGS_TAG = 'Settings'
PROJECT_TAG = 'Projects'
ACTIONS_TAG = 'Actions'

def tag(name: str):
    def decorator(f):
        if not hasattr(f, '__clitags__'):
            f.__clitags__ = []
        f.__clitags__.append(name)
        return f
    return decorator

def get_tags(cmd):
    return getattr(cmd, '__clitags__', [])

def deprecated_tag(f):
    return tag(DEPRECATED_TAG)(f)

def project_tag(f):
    return tag(PROJECT_TAG)(f)

def settings_tag(f):
    return tag(SETTINGS_TAG)(f)

def actions_tag(f):
    return tag(ACTIONS_TAG)(f)



class TagFormattedMixin:

    def format_commands(self, ctx, formatter):
        """
        Override format_commands to separate commands
        """
        cmds_by_tag = OrderedDict({
            SETTINGS_TAG: [],
            ACTIONS_TAG: [],
            PROJECT_TAG: [],
            DEPRECATED_TAG: []
        })
        other_commands = []
        for cmd_name in self.list_commands(ctx):
            cmd = self.get_command(ctx, cmd_name)
            if cmd is None:
                continue
            if cmd.hidden:
                continue
            cmd_tags = get_tags(cmd)
            if cmd_tags is None or len(cmd_tags) == 0:
                other_commands.append((cmd_name, cmd))
            else:
                for tag in cmd_tags:
                    if tag not in cmds_by_tag:
                        cmds_by_tag[cmd_tag] = []
                    cmds_by_tag[tag].append((cmd_name, cmd))
        
        for tag, cmd_tpls in cmds_by_tag.items():
            if len(cmd_tpls) > 0:
                self._write_commands_to_formatter(formatter, tag, cmd_tpls)
        if len(other_commands) > 0:
            self._write_commands_to_formatter(formatter, 'Other', other_commands)
        
    def _write_commands_to_formatter(self, formatter, title, command_tpls, pre_text = None):
        if len(command_tpls):
            # Click recommended width
            # Take away 6 for spacing
            # Take away the length of the largest command name
            limit = formatter.width - 6 - max(len(cmd_name) for cmd_name, _ in command_tpls)
            rows = []
            for cmd_name, cmd in command_tpls:
                help = cmd.get_short_help_str(limit)
                rows.append((cmd_name, help))
            if rows:
                if pre_text:
                    formatter.write_paragraph()
                    formatter.write_text(pre_text)
                with formatter.section(title):
                    formatter.write_dl(rows)

class TagFormattedGroup(TagFormattedMixin, click.Group):
    pass