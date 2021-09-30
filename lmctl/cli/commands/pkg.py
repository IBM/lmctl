import click
import logging
import shutil
import os
import lmctl.cli.lifecycle as lifecycle_cli
import lmctl.project.package.core as pkgs
from lmctl.cli.format import determine_format_class
from lmctl.cli.cmd_tags import project_tag

logger = logging.getLogger(__name__)

@project_tag
@click.group(short_help='Onboard a package built from a Project', help='Onboard a package previously built from a Project, distributed as a ".tgz" or ".csar" file')
def pkg():
    logger.debug('Package Management')


PUSH_HEADER = 'Push'


@pkg.command(help='Push a previously built package to a CP4NA orchestration environment')
@click.argument('package')
@click.argument('environment', required=False, default=None)
@click.option('--config', default=None, help='configuration file')
@click.option('--armname', default='defaultrm', help='if using ansible-rm packaging the name of ARM to upload Resources to must be provided')
@click.option('--pwd', '--api-key', default=None, help='password/api_key used for authenticating with CP4NA orchestration. Only required if the environment is secure and a username has been included in your configuration file with no password (api_key when using auth_mode=zen)')
@click.option('--autocorrect', default=False, is_flag=True, help='allow validation warnings and errors to be autocorrected if supported')
def push(package, environment, config, armname, pwd, autocorrect):
    """Pushes an existing Assembly/Resource package to a target CP4NA orchestration (and ARM) environment"""
    logger.debug('Pushing package at: {0}'.format(package))
    pkg, pkg_content = lifecycle_cli.get_pkg_and_open(package)
    try:
        env_sessions = lifecycle_cli.build_sessions_for_pkg(pkg_content.meta, environment, pwd, armname, config)
        controller = lifecycle_cli.ExecutionController(PUSH_HEADER)
        controller.start(package)
        exec_push(controller, pkg, env_sessions, allow_autocorrect=autocorrect)
    finally:
        cleanup_pkg(pkg_content)
    controller.finalise()


@pkg.command(help='Inspect a package')
@click.argument('package')
@click.option('--config', default=None, help='configuration file')
@click.option('-f', '--format', 'output_format', default='yaml', help='format of output [yaml, json]')
def inspect(package, config, output_format):
    logger.debug('Inspecting package at: {0}'.format(package))
    pkg_content = lifecycle_cli.open_pkg(package)
    try:
        inspection_report = pkg_content.inspect()
        result = format_inspection_report(output_format, inspection_report)
        click.echo(result)
    finally:
        cleanup_pkg(pkg_content)
    
def cleanup_pkg(pkg):
    if os.path.exists(pkg.tree.root_path):
        shutil.rmtree(pkg.tree.root_path)

def format_inspection_report(output_format, inspection_report):
    inspection_report_tpl = inspection_report.to_dict()
    formatter_class = determine_format_class(output_format)
    formatter = formatter_class()
    result = formatter.convert_element(inspection_report_tpl)
    return result

def exec_push(controller, pkg, env_sessions, allow_autocorrect=False):
    push_options = pkgs.PushOptions()
    push_options.allow_autocorrect = allow_autocorrect
    push_options.journal_consumer = controller.consumer
    return controller.execute(pkg.push, env_sessions, push_options)
