import click
import logging
import lmctl.cli.lifecycle as lifecycle_cli
import lmctl.project.package.core as pkgs
from lmctl.cli.format import determine_format_class

logger = logging.getLogger(__name__)


@click.group(help='Commands for managing a package built from an Assembly/Resource Project')
def pkg():
    logger.debug('Package Management')


PUSH_HEADER = 'Push'


@pkg.command(help='Push a previously built package to a LM environment')
@click.argument('package')
@click.argument('environment')
@click.option('--config', default=None, help='configuration file')
@click.option('--armname', default='defaultrm', help='if using ansible-rm packaging the name of ARM to upload Resources to must be provided')
@click.option('--pwd', default=None, help='password used for authenticating with LM (only required if LM is secure and a username has been included in the environment config)')
def push(package, environment, config, armname, pwd):
    """Pushes an existing Assembly/Resource package to a target LM (and ARM) environment"""
    logger.debug('Pushing package at: {0}'.format(package))
    pkg = lifecycle_cli.open_pkg(package)
    env_sessions = lifecycle_cli.build_sessions_for_project(package.config, environment, pwd, armname, config)
    controller = lifecycle_cli.ExecutionController(PUSH_HEADER)
    controller.start(pkg.path)
    exec_push(controller, pkg, env_sessions)
    controller.finalise()


@pkg.command(help='Inspect a package')
@click.argument('package')
@click.option('--config', default=None, help='configuration file')
@click.option('-f', '--format', 'output_format', default='yaml', help='format of output [yaml, json]')
def inspect(package, config, output_format):
    logger.debug('Inspecting package at: {0}'.format(package))
    pkg = lifecycle_cli.open_pkg(package)
    inspection_report = pkg.inspect()
    result = format_inspection_report(output_format, inspection_report)
    click.echo(result)
    
def format_inspection_report(output_format, inspection_report):
    inspection_report_tpl = inspection_report.to_dict()
    formatter_class = determine_format_class(output_format)
    formatter = formatter_class()
    result = formatter.convert_element(inspection_report_tpl)
    return result

def exec_push(controller, pkg, env_sessions):
    push_options = pkgs.PushOptions()
    push_options.journal_consumer = controller.consumer
    return controller.execute(pkg.push, env_sessions)
